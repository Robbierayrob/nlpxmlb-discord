# Discord Gemini Bot Setup

## Create Virtual Environment

Create a virtual environment in the project directory:

```bash
python -m venv venv
```

## Activate Virtual Environment

### On Windows
```bash
source venv/Scripts/activate
```

### On macOS or Linux
```bash
source venv/bin/activate
```

## Install Requirements

Install the project dependencies:

```bash
pip install -r requirements.txt
```

## Configure Environment Variables

Create a `.env` file in the project directory and add the following environment variables:

```
GOOGLE_API_KEY=YOUR_GOOGLE_API_KEY
DISCORD_TOKEN=YOUR_DISCORD_TOKEN
ALLOWED_SERVER_ID=YOUR_SERVER_ID
ALLOWED_CHANNELS=YOUR_CHANNEL_NAMES
```

Replace `YOUR_GOOGLE_API_KEY` with your actual Google API key.

Replace `YOUR_DISCORD_TOKEN` with your actual Discord token.

Replace `YOUR_SERVER_ID` with the ID of the server you want the bot to join.

Replace `YOUR_CHANNEL_NAMES` with a comma-separated list of channel names you want the bot to join.

For example:

```
GOOGLE_API_KEY=YOUR_GOOGLE_API_KEY
DISCORD_TOKEN=YOUR_DISCORD_TOKEN
ALLOWED_SERVER_ID=1234567890
ALLOWED_CHANNELS=general,announcements
```

## Run the Bot

Start the Discord Gemini bot:

```bash
python discord_gemini_bot.py
```



Enjoy! 🤖
