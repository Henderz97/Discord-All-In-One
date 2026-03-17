import discord
from discord.ext import commands, tasks
import yfinance as ticker_info
import requests
import os
from flask import Flask
from threading import Thread
from datetime import datetime

# --- חלק 1: שרת Flask להשארת הבוט ער ---
app = Flask('')

@app.route('/')
def home():
    return "Bot is running!"

def run():
    app.run(host='0.0.0.0', port=10000)

def keep_alive():
    t = Thread(target=run)
    t.start()

# --- חלק 2: הגדרות Secrets ---
TOKEN = os.environ.get('DISCORD_TOKEN')
env_channel_id = os.environ.get('CHANNEL_ID')
CHANNEL_ID = int(env_channel_id) if env_channel_id else None

class MyBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(command_prefix='!', intents=intents)

    async def setup_hook(self):
        self.daily_updates.start()

    async def on_ready(self):
        print(f'Logged in as {self.user}')
        print('------')

    @tasks.loop(hours=24)
    async def daily_updates(self):
        if not CHANNEL_ID:
            return
            
        channel = self.get_channel(CHANNEL_ID)
        if channel:
            # 1. עדכון ביטקוין
            await self.send_btc_update(channel)
            # 2. עדכון משחקים חינמיים
            await self.send_free_games_update(channel)

    async def send_btc_update(self, channel):
        try:
            response = requests.get('https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd')
            btc_price = response.json()['bitcoin']['usd']
            embed = discord.Embed(title="💰 עדכון ביטקוין יומי", color=discord.Color.gold())
            embed.add_field(name="מחיר נוכחי", value=f"${btc_price:,}", inline=False)
            await channel.send(embed=embed)
        except Exception as e:
            print(f"BTC Error: {e}")

    async def send_free_games_update(self, channel):
        try:
            # שליפת נתונים מה-API של Epic Games
            url = "https://store-site-backend-static.ak.epicgames.com/freeGamesPromotions?locale=en-US&country=US&allowCountries=US"
            response = requests.get(url).json()
            games = response['data']['Catalog']['searchStore']['elements']
            
            found_free = False
            embed = discord.Embed(title="🎮 משחקים חינמיים השבוע (Epic Games)", color=discord.Color.green())

            for game in games:
                promotions = game.get('promotions')
                if not promotions or not promotions.get('promotionalOffers'):
                    continue
                
                offers = promotions['promotionalOffers'][0]['promotionalOffers']
                for offer in offers:
                    # בדיקה אם המחיר כרגע הוא 0 (חינם)
                    if offer.get('discountSetting', {}).get('discountPercentage') == 0:
                        title = game['title']
                        desc = game.get('description', 'No description available.')
                        game_url = f"https://store.epicgames.com/en-US/p/{game.get('catalogNs', {}).get('pages', [{}])[0].get('pageSlug', '')}"
                        
                        embed.add_field(name=title, value=f"[לחץ כאן למעבר למשחק]({game_url})", inline=False)
                        found_free = True

            if found_free:
                await channel.send(embed=embed)
        except Exception as e:
            print(f"Games Error: {e}")

    @daily_updates.before_loop
    async def before_daily_updates(self):
        await self.wait_until_ready()

bot = MyBot()

@bot.command(name='stock')
async def stock_info(ctx, symbol: str):
    try:
        data = ticker_info.Ticker(symbol)
        price = data.info.get('currentPrice', 'N/A')
        await ctx.send(f"המחיר של **{symbol.upper()}** הוא: {price} {data.info.get('currency', 'USD')}")
    except Exception as e:
        await ctx.send(f"שגיאה בשליפת נתונים: {e}")

if __name__ == "__main__":
    if TOKEN:
        keep_alive()
        bot.run(TOKEN)
