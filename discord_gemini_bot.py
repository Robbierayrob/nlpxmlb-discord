import discord
from discord.ext import commands
from langchain_google_genai import GoogleGenerativeAI
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure environment variables
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
ALLOWED_SERVER_ID = os.getenv("ALLOWED_SERVER_ID")  # Optional: specify a specific server ID
ALLOWED_CHANNELS = os.getenv("ALLOWED_CHANNELS", "").split(",")  # Comma-separated list of channel names

# Validate tokens
if not DISCORD_TOKEN:
    raise ValueError("No Discord token found. Please check your .env file.")
if not GOOGLE_API_KEY:
    raise ValueError("No Google API key found. Please check your .env file.")

# Initialize Discord bot with all intents
intents = discord.Intents.all()  # Enable all intents to read messages
bot = commands.Bot(command_prefix="!", intents=intents)

# Initialize Gemini model with enhanced configuration
llm = GoogleGenerativeAI(
    model="gemini-1.5-flash",
    google_api_key=GOOGLE_API_KEY,
    temperature=0.7,  # Increased creativity
    max_output_tokens=256  # Reduced default token length
)

@bot.event
async def on_ready():
    """Confirms bot connection and prints connection details."""
    print(f'{bot.user} has connected to Discord!')
    print(f'Bot is ready in {len(bot.guilds)} servers')
    
    # Log details of servers and allowed channels
    for guild in bot.guilds:
        print(f'Connected to server: {guild.name}')
        print(f'Allowed channels: {ALLOWED_CHANNELS}')

@bot.event
async def on_message(message):
    """Handles messages in allowed channels."""
    # Ignore messages from the bot itself
    if message.author == bot.user:
        return

    # Check if a specific server is allowed
    if ALLOWED_SERVER_ID and str(message.guild.id) != ALLOWED_SERVER_ID:
        return

    # Check if the channel is in the allowed channels list
    if ALLOWED_CHANNELS and ALLOWED_CHANNELS[0]:
        # If ALLOWED_CHANNELS is set, only respond in those channels
        if message.channel.name not in ALLOWED_CHANNELS:
            return

    # Determine the user's display name (nickname if set, otherwise username)
    user_display_name = message.author.display_name

    # Prepare context for LLM
    prompt = f"""You are a Discord bot AI assistant, actively participating in a real-time conversation.

Conversation Context:
- Server: {message.guild.name}
- Channel: {message.channel.name}
- Sender: {user_display_name}

Original Message: {message.content.strip()}

Communication Guidelines:
- Respond naturally and concisely
- Be direct and engaging
- Provide relevant and interesting responses
- Refer to the sender by their display name"""
    
    try:
        # Get response from Gemini model
        response = llm.invoke(prompt)
        
        # Tag the sender using their user ID, but use display name in the response
        final_response = f"<@{message.author.id}> {response}"
        
        # Send the response
        await message.channel.send(final_response)
        
        # Log the interaction
        print(f"Responded to {user_display_name} in {message.guild.name}, channel {message.channel.name}")
    
    except Exception as e:
        # Comprehensive error handling
        print(f"Error generating response: {e}")
        await message.channel.send(f"Oops! System error: {str(e)}")

    # Ensure other bot commands can still be processed
    await bot.process_commands(message)

# Run the bot
if __name__ == "__main__":
    print("Initializing Gemini Discord Bot...")
    bot.run(DISCORD_TOKEN)
