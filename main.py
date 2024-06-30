# Import libraries
import discord
import asyncio
from discord.ext import commands, tasks
import subprocess
import os
import datetime
from dotenv import load_dotenv
import ticketing  # Import the ticketing system
from severity_assessment import assess_severity  # Import severity assessment function

# Load environment variables
load_dotenv()
TOKEN = os.getenv("TOKEN")

# Initialise bot and intents
intents = discord.Intents.default()
intents.message_content = True
intents.messages = True
intents.guilds = True
bot = commands.Bot(command_prefix="$", intents=intents)

# Bot class
class MyBot(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # Bot startup command
    @commands.Cog.listener()
    async def on_ready(self):
        print(f"Logged in as {self.bot.user.name}")
        await bot.tree.sync()  # Sync the slash commands with Discord

    # Bot scan command
    @discord.app_commands.command(name="scan", description="Initiate a scan for a given URL")
    async def scan(self, interaction: discord.Interaction, url: str):
        embed = discord.Embed(
            title="Scan Initiated", 
            description=f"Initiating scan for {url}", 
            color=discord.Color.blue()
        )
        await interaction.response.send_message(embed=embed)
        
        # Run the scan using nmap
        try:
            result = subprocess.run(["nmap", "-sV", "-oN", "-", url], capture_output=True, text=True)
            embed = discord.Embed(
                title="Scan Complete", 
                description=f"Results:\n{result.stdout}", 
                color=discord.Color.green()
            )
            await interaction.followup.send(embed=embed)
            
            # Assess severity dynamically based on scan results
            severity_level = assess_severity(result.stdout)
            
            # Create a ticket based on the scan results and severity level
            ticket_id = ticketing.create_ticket(
                title=f"Vulnerability Scan for {url}",
                description=f"Scan results:\n{result.stdout}",
                severity_level=severity_level,
                affected_components=url,
                steps_to_reproduce="Run the scan command again with the same URL",
                attachments=None
            )
            await interaction.followup.send(f"Scan complete. Ticket ID: {ticket_id}\nResults:\n{result.stdout}")
        except Exception as e:
            embed = discord.Embed(
                title="Error", 
                description=f"An error has occurred: {str(e)}", 
                color=discord.Color.red()
            )
            await interaction.followup.send(embed=embed)

    # Bot Schedule Scan command
    @discord.app_commands.command(name="schedule_scan", description="Schedule a scan for a given URL at a specified interval")
    async def schedule_scan(self, interaction: discord.Interaction, url: str, interval: str):
        intervals = {
            "daily": datetime.timedelta(days=1),
            "weekly": datetime.timedelta(weeks=1)
        }
        scan_interval = intervals.get(interval.lower(), None)
        if scan_interval:
            embed = discord.Embed(
                title="Scan Scheduled", 
                description=f"Scheduled a {interval} scan for {url}", 
                color=discord.Color.blue()
            )
            await interaction.response.send_message(embed=embed)

            @tasks.loop(seconds=scan_interval.total_seconds())
            async def scheduled_scan():
                await self.scan(interaction, url)

            scheduled_scan.start()
        else:
            embed = discord.Embed(
                title="Invalid Interval", 
                description="Invalid interval. Please use 'daily' or 'weekly'.", 
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed)

    @discord.app_commands.command(name="scan_report", description="Fetch scan history for a given URL")
    async def scan_report(self, interaction: discord.Interaction, url: str):
        embed = discord.Embed(
            title="Fetching Scan History", 
            description=f"Fetching scan history for {url}...", 
            color=discord.Color.blue()
        )
        await interaction.response.send_message(embed=embed)
        
        tickets = ticketing.get_all_tickets()
        report = "\n".join([f"Ticket ID: {t[0]}, Title: {t[1]}, Status: {t[7]}" for t in tickets if url in t[3]])
        embed = discord.Embed(
            title="Scan History", 
            description=report, 
            color=discord.Color.green()
        )
        await interaction.followup.send(embed=embed)

    @discord.app_commands.command(name="help", description="Help command for CyberSweep")
    async def bot_help(self, interaction: discord.Interaction):
        embed = discord.Embed(
            title="CyberSweep Bot Help",
            description="Below is a list of available commands and their descriptions:",
            color=discord.Color.blurple()
        )
        embed.add_field(
            name="`/scan [url]`",
            value="Initiates a vulnerability scan on the specified URL.",
            inline=False
        )
        embed.add_field(
            name="`/schedule_scan [url] [interval]`",
            value="Schedules a recurring vulnerability scan at specified intervals (e.g., daily, weekly).",
            inline=False
        )
        embed.add_field(
            name="`/scan_report [url]`",
            value="Fetches the scan history for the specified URL.",
            inline=False
        )
        embed.set_footer(text="For more information, contact us on Discord at 'geosirey'.")

        terms_button = discord.ui.Button(style=discord.ButtonStyle.link, label="Terms of Service", url="https://gist.github.com/NickEvans4130/ba8c2222ab20190ab5cce9dee95b384b")
        privacy_button = discord.ui.Button(style=discord.ButtonStyle.link, label="Privacy Policy", url="https://gist.github.com/NickEvans4130/4e3afa7fda29797ce3d0a0af8649e894")
        view = discord.ui.View()
        view.add_item(terms_button)
        view.add_item(privacy_button)

        await interaction.followup.send(embed=embed, view=view)

    @tasks.loop(seconds=3600)
    async def notify_scan_completion(self):
        # Check for completed scans and notify users
        pass

    async def cog_load(self):
        self.notify_scan_completion.start()  # Start the scheduled task

async def setup(bot):
    await bot.add_cog(MyBot(bot))

@bot.event
async def on_ready():
    await bot.tree.sync()  # Sync the slash commands with Discord

async def main():
    async with bot:
        await setup(bot)
        await bot.start(TOKEN)

asyncio.run(main())
