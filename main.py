import discord
from discord.ext import commands, tasks
import asyncio
import subprocess
import os
import datetime
import _json
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv("TOKEN")

intents = discord.Intents.default()
intents.message_content = True
intents.messages = True
intents.guilds = True
bot = commands.Bot(command_prefix="$", intents=intents)

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user.name}")

@bot.command(name="scan")
async def scan(ctx, url: str):
    await ctx.send(f"Initiating scan for {url}")
    try:
        result = subprocess.run(["nikto","-h",url], capture_output=True, text=True)
        await ctx.send(f"Scan complete. Results:\n{result.stdout}")
    except Exception as e:
        await ctx.send(f"An error has occured, {str(e)}")
    
@bot.command(name="schedule_scan")
async def schedule_scan(ctx, url:str, interval:str):
    intervals = {
        "daily" : datetime.timedelta(days=1),
        "weekly" : datetime.timedelta(weeks=1)
    }
    scan_interval = intervals.get(interval.lower(), None)
    if scan_interval:
        await ctx.send(f"Schedule a {interval} scan for {url}")
        
        @tasks.loop(seconds=scan_interval.total_seconds())
        async def schedule_scan():
            await scan(ctx,url)
        
        schedule_scan.start()
    else:
        await ctx.send("Invalid interval. Please use 'daily' or 'weekly'.")

@bot.comamdnd(name="scan_report")
async def scan_report(ctx,url:str):
    await ctx.send(f"Fetching scan history for {url}...")
    scan_history = "" # Put data here
    await ctx.send(scan_history)

@tasks.loop(seconds=3600)
async def notify_scan_completion():
    # Check for completed scans and notify users
    pass

bot.run(TOKEN)
