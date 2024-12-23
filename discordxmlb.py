import discord
from discord.ext import commands
from langchain_google_genai import GoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain.memory import VectorStoreRetrieverMemory
from langchain_core.memory import BaseMemory
from langchain_core.messages import AIMessage, HumanMessage
from pydantic import BaseModel, Field
from langchain_core.runnables import RunnableWithMessageHistory
from langchain.prompts import PromptTemplate
from langchain_chroma import Chroma
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure environment variables
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")

# Validate token
if not DISCORD_TOKEN:
    raise ValueError("No Discord token found. Please check your .env file.")

# Create the database directory if it doesn't exist
DB_DIR = "./chroma_db"
Path(DB_DIR).mkdir(parents=True, exist_ok=True)

# Initialize Discord bot
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

# Initialize Gemini model
llm = GoogleGenerativeAI(
    model="gemini-1.5-flash",
    google_api_key=GOOGLE_API_KEY
)

# Initialize embeddings
embeddings = GoogleGenerativeAIEmbeddings(
    model="models/embedding-001",
    google_api_key=GOOGLE_API_KEY
)

# Initialize vector store with explicit collection name
vectorstore = Chroma(
    collection_name="conversation_history",
    embedding_function=embeddings,
    persist_directory=DB_DIR
)

# Verify the collection exists or create it
collections = vectorstore._client.list_collections()
if not any(c.name == "conversation_history" for c in collections):
    print("Creating new conversation history collection...")
    vectorstore._client.create_collection("conversation_history")
    vectorstore.persist()
else:
    print("Found existing conversation history collection")

# Custom memory class that works with RunnableWithMessageHistory
class VectorStoreMemoryWrapper(BaseMemory, BaseModel):
    vector_store_memory: VectorStoreRetrieverMemory = Field(...)
    _messages: list = []

    @property
    def memory_variables(self):
        return ["chat_history"]

    def load_memory_variables(self, inputs):
        # Retrieve relevant context from vector store
        retriever = self.vector_store_memory.retriever
        docs = retriever.get_relevant_documents(inputs.get("input", ""))
        
        # Convert retrieved docs to message format
        chat_history = []
        for doc in docs:
            chat_history.append(HumanMessage(content=doc.page_content))
        
        return {"chat_history": chat_history}

    def save_context(self, inputs, outputs):
        # Save messages to the internal list
        self._messages.extend([
            HumanMessage(content=inputs.get("input", "")),
            AIMessage(content=outputs)
        ])

    def clear(self):
        self._messages.clear()

# Configure memory
vector_store_memory = VectorStoreRetrieverMemory(
    retriever=vectorstore.as_retriever(search_kwargs=dict(k=5)),
    memory_key="chat_history"
)
memory = VectorStoreMemoryWrapper(vector_store_memory)

# Create conversation prompt template
template = """The following is a conversation between a human and an AI assistant.
Current conversation:
{chat_history}
Human: {input}
AI Assistant: """

prompt = PromptTemplate(
    input_variables=["chat_history", "input"], 
    template=template
)

# Create session history management
def get_session_history(session_id: str):
    return memory

# Create runnable with message history
conversation = RunnableWithMessageHistory(
    runnable=llm.bind(prompt=prompt),
    get_session_history=get_session_history,
    input_messages_key="input",
    history_messages_key="chat_history"
)

@bot.event
async def on_ready():
    print(f'{bot.user} has connected to Discord!')
    print(f'Chroma database directory: {os.path.abspath(DB_DIR)}')
    print(f'Collection name: conversation_history')

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    if bot.user in message.mentions:
        user_input = message.content.replace(f'<@{bot.user.id}>', '').strip()
        
        # Get response from conversation chain
        config = {"configurable": {"session_id": str(message.author.id)}}
        response = conversation.invoke({"input": user_input}, config)
        
        # Send response
        await message.channel.send(response)

    await bot.process_commands(message)

# Run the bot
if __name__ == "__main__":
    print("Initializing bot...")
    print(f"Database directory: {os.path.abspath(DB_DIR)}")
    bot.run(DISCORD_TOKEN)
