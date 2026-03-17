import discord
from discord.ext import commands, tasks
import yfinance as ticker_info
import requests
import os
from flask import Flask
from threading import Thread
from datetime import datetime

# --- חלק 1: שרת Flask קטן כדי להשאיר את הבוט ער בענן ---
app = Flask('')

@app.route('/')
def home():
    return "Bot is running!"

def run():
    # Render משתמש בפורט 10000 בדרך כלל
    app.run(host='0.0.0.0', port=10000)

def keep_alive():
    t = Thread(target=run)
    t.start()

# --- חלק 2: הגדרות מאובטחות (Environment Variables) ---
# אנחנו מושכים את המידע מהגדרות השרת ולא כותבים אותו בקוד
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
        print(f'Logged in as {self.user} (ID: {self.user.id})')
        print('------')

    # עדכון מחיר ביטקוין יומי
    @tasks.loop(hours=24)
    async def daily_updates(self):
        if not CHANNEL_ID:
            print("CHANNEL_ID not set, skipping daily update.")
            return
            
        channel = self.get_channel(CHANNEL_ID)
        if channel:
            try:
                response = requests.get('https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd')
                btc_price = response.json()['bitcoin']['usd']
                
                embed = discord.Embed(title="☀️ עדכון בוקר", color=discord.Color.gold())
                embed.add_field(name="Bitcoin Price", value=f"${btc_price:,}", inline=False)
                embed.set_footer(text=f"תאריך: {datetime.now().strftime('%d/%m/%Y')}")
                
                await channel.send(embed=embed)
            except Exception as e:
                print(f"Error in daily update: {e}")

    @daily_updates.before_loop
    async def before_daily_updates(self):
        await self.wait_until_ready()

# יצירת הבוט
bot = MyBot()

# --- פקודות ---

@bot.command(name='stock')
async def stock_info(ctx, symbol: str):
    try:
        data = ticker_info.Ticker(symbol)
        info = data.info
        current_price = info.get('currentPrice', 'N/A')
        currency = info.get('currency', 'USD')
        
        embed = discord.Embed(title=f"סיקור מניה: {symbol.upper()}", color=discord.Color.blue())
        embed.add_field(name="מחיר נוכחי", value=f"{current_price} {currency}")
        embed.add_field(name="שיא יומי", value=info.get('dayHigh', 'N/A'))
        embed.add_field(name="שווי שוק", value=f"{info.get('marketCap', 'N/A'):,}")
        
        await ctx.send(embed=embed)
    except Exception as e:
        await ctx.send(f"שגיאה בשליפת נתונים עבור {symbol}: {e}")

@bot.command(name='manga')
async def add_manga(ctx, *, manga_name: str):
    await ctx.send(f"הוספתי את **{manga_name}** לרשימת המעקב שלך! (פיצ'ר בבנייה)")

# --- הרצה ---
if __name__ == "__main__":
    if TOKEN:
        keep_alive()  # מפעיל את שרת ה-Flask ברקע
        bot.run(TOKEN)
    else:
        print("ERROR: No DISCORD_TOKEN found in environment variables!")
