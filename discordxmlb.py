import discord
from discord.ext import commands
from langchain_google_genai import GoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain.memory import VectorStoreRetrieverMemory
from langchain.chains import ConversationChain
from langchain.prompts import PromptTemplate
from langchain_community.vectorstores import Chroma
import os
from typing import Dict, List

# Configure environment variables
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")

# Initialize Discord bot
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

# Initialize Gemini model and embeddings
llm = GoogleGenerativeAI(model="gemini-1.5-flash", google_api_key=GOOGLE_API_KEY)
embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001", google_api_key=GOOGLE_API_KEY)

# Initialize vector store (Chroma)
vectorstore = Chroma(
    collection_name="chat_history",
    embedding_function=embeddings,
    persist_directory="./chroma_db"
)

# Configure memory with vector store
memory = VectorStoreRetrieverMemory(
    retriever=vectorstore.as_retriever(search_kwargs=dict(k=5)),
    memory_key="chat_history"
)

# Create conversation chain
template = """The following is a conversation between a human and an AI assistant.
Current conversation:
{chat_history}
Human: {input}
AI Assistant: """

prompt = PromptTemplate(
    input_variables=["chat_history", "input"], 
    template=template
)

conversation = ConversationChain(
    llm=llm,
    memory=memory,
    prompt=prompt,
    verbose=True
)

# Discord event handlers
@bot.event
async def on_ready():
    print(f'{bot.user} has connected to Discord!')

@bot.event
async def on_message(message):
    # Ignore messages from the bot itself
    if message.author == bot.user:
        return

    # Only respond to messages that mention the bot
    if bot.user in message.mentions:
        # Remove the bot mention from the message
        user_input = message.content.replace(f'<@{bot.user.id}>', '').strip()
        
        # Get response from conversation chain
        response = conversation.predict(input=user_input)
        
        # Send response
        await message.channel.send(response)

    await bot.process_commands(message)

# Run the bot
if __name__ == "__main__":
    bot.run(DISCORD_TOKEN)