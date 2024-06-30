import discord
from discord.ext import commands, tasks
from discord import app_commands
import subprocess
import os
import datetime
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv("TOKEN")

intents = discord.Intents.default()
intents.message_content = True
intents.messages = True
intents.guilds = True

class MyBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix="$", intents=intents, application_id=os.getenv("APPLICATION_ID"))

    async def setup_hook(self):
        self.tree.add_command(scan)
        self.tree.add_command(schedule_scan)
        self.tree.add_command(scan_report)
        await self.tree.sync()

bot = MyBot()

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user.name}")

@bot.event
async def on_guild_join(guild: discord.Guild):
    # Ensure commands are registered for new guilds
    await bot.tree.sync(guild=guild)

@bot.event
async def on_guild_remove(guild: discord.Guild):
    # Handle guild removal if needed
    pass

@bot.tree.command(name="scan", description="Initiate a vulnerability scan on the specified URL.")
@app_commands.describe(url="The URL to scan.")
async def scan(interaction: discord.Interaction, url: str):
    await interaction.response.send_message(f"Initiating scan for {url}")
    try:
        result = subprocess.run(["nikto", "-h", url], capture_output=True, text=True)
        await interaction.followup.send(f"Scan complete. Results:\n{result.stdout}")
    except Exception as e:
        await interaction.followup.send(f"An error has occurred, {str(e)}")

@bot.tree.command(name="schedule_scan", description="Schedule a recurring vulnerability scan at specified intervals.")
@app_commands.describe(url="The URL to scan.", interval="The scan interval (daily or weekly).")
async def schedule_scan(interaction: discord.Interaction, url: str, interval: str):
    intervals = {
        "daily": datetime.timedelta(days=1),
        "weekly": datetime.timedelta(weeks=1)
    }
    scan_interval = intervals.get(interval.lower(), None)
    if scan_interval:
        await interaction.response.send_message(f"Schedule a {interval} scan for {url}")

        @tasks.loop(seconds=scan_interval.total_seconds())
        async def scheduled_scan():
            await scan(interaction, url)

        scheduled_scan.start()
    else:
        await interaction.response.send_message("Invalid interval. Please use 'daily' or 'weekly'.")

@bot.tree.command(name="scan_report", description="Fetch the scan history for the specified URL.")
@app_commands.describe(url="The URL to fetch scan history for.")
async def scan_report(interaction: discord.Interaction, url: str):
    await interaction.response.send_message(f"Fetching scan history for {url}...")
    scan_history = ""  # Put data here
    await interaction.followup.send(scan_history)

@tasks.loop(seconds=3600)
async def notify_scan_completion():
    # Check for completed scans and notify users
    pass

bot.run(TOKEN)
