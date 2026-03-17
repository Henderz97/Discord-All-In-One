🤖 All-In-One Discord Utility Bot
A versatile Discord bot built with Python, designed to automate daily information delivery and provide on-demand market insights. This bot is cloud-hosted and runs 24/7 to ensure real-time alerts and data availability.

🚀 Key Features
💰 Daily Crypto Updates: Automatically broadcasts the current Bitcoin (BTC) price to a designated channel every morning.

📈 On-Demand Stock Analysis: Use the !stock [SYMBOL] command to retrieve real-time market data (price, currency, etc.) via the Yahoo Finance API.

🎮 Free Games Alerts (Coming Soon): Automated monitoring of the Epic Games Store and Steam to notify users about 100% discount deals.

📚 Manga Tracker (Coming Soon): Real-time notifications for new chapter releases from selected manga sources.

🛠 Tech Stack
Language: Python 3.x

Framework: discord.py

APIs: CoinGecko API, yfinance (Yahoo Finance)

Deployment: Render / Square Cloud

Uptime Strategy: Integrated Flask server for keep-alive monitoring.

📋 Setup & Installation
Clone the repository:

Bash
git clone https://github.com/Henderz97/Discord-All-In-One.git
Install dependencies:

Bash
pip install -r requirements.txt
Configure Environment Variables:
Create a .env file or set the following variables in your hosting provider's dashboard:

DISCORD_TOKEN: Your unique bot token from the Discord Developer Portal.

CHANNEL_ID: The ID of the Discord channel where automated updates should be sent.

Run the bot:

Bash
python main.py
