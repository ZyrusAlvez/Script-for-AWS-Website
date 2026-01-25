import discord
from discord.ext import commands
from dotenv import load_dotenv
import os
from datetime import datetime
import asyncio
import threading
import sys

# Load .env
load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")
STAGE_CHANNEL_ID = int(os.getenv("STAGE_CHANNEL_ID"))

# Intents
intents = discord.Intents.default()
intents.voice_states = True
intents.guilds = True
intents.members = True  

bot = commands.Bot(command_prefix="!", intents=intents)

# Attendance storage
# {user_id: {"join": datetime, "total_seconds": int}}
attendance = {}

@bot.event
async def on_ready():
    print(f"Bot logged in as {bot.user}")
    print(f"Monitoring stage channel ID: {STAGE_CHANNEL_ID}")
    
    # Join stage as audience
    stage_channel = bot.get_channel(STAGE_CHANNEL_ID)
    if stage_channel and isinstance(stage_channel, discord.StageChannel):
        try:
            # Connect to stage channel
            voice_client = await stage_channel.connect()
            # Request to speak (join as audience)
            await stage_channel.guild.me.edit(suppress=True)
            print(f"Joined stage channel as audience: {stage_channel.name}")
        except Exception as e:
            print(f"Failed to join stage: {e}")
    else:
        print("Stage channel not found or not a stage channel")

@bot.event
async def on_voice_state_update(member, before, after):
    # Skip bot's own voice state changes
    if member == bot.user:
        return
        
    # Joined stage
    if after.channel and after.channel.id == STAGE_CHANNEL_ID and (not before.channel or before.channel.id != STAGE_CHANNEL_ID):
        attendance[member.id] = attendance.get(member.id, {"total_seconds": 0})
        attendance[member.id]["join"] = datetime.now()
        print(f"{member.display_name} joined the stage at {attendance[member.id]['join']}")

    # Left stage
    if before.channel and before.channel.id == STAGE_CHANNEL_ID and (not after.channel or after.channel.id != STAGE_CHANNEL_ID):
        if member.id in attendance and "join" in attendance[member.id]:
            join_time = attendance[member.id].pop("join")
            duration = (datetime.now() - join_time).total_seconds()
            attendance[member.id]["total_seconds"] += int(duration)
            print(f"{member.display_name} left the stage. Duration: {int(duration)} seconds")

def show_current_attendance():
    if not attendance:
        print("\nNo attendance recorded yet.")
        return
    
    print("\n=== Current Stage Attendance ===")
    for user_id, data in attendance.items():
        user = bot.get_user(user_id)
        total_time = data.get("total_seconds", 0)
        
        # Add current session time if user is still in stage
        if "join" in data:
            current_session = (datetime.now() - data["join"]).total_seconds()
            total_time += int(current_session)
            status = "(currently in stage)"
        else:
            status = ""
            
        minutes = total_time // 60
        seconds = total_time % 60
        display_name = user.display_name if user else user_id
        print(f"{display_name}: {minutes}m {seconds}s {status}")
    print("================================\n")

def input_handler():
    while True:
        try:
            key = input().strip().lower()
            if key == 'q':
                show_current_attendance()
        except EOFError:
            break
        except KeyboardInterrupt:
            break

async def main():
    # Start input handler in separate thread
    input_thread = threading.Thread(target=input_handler, daemon=True)
    input_thread.start()
    
    print("Bot starting... Press 'q' + Enter to show current attendance")
    
    try:
        await bot.start(TOKEN)
    except KeyboardInterrupt:
        print("\nShutting down...")
        await bot.close()

if __name__ == "__main__":
    asyncio.run(main())
