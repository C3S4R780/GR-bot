#           GGGGGGGGGGGGGGGG   RRRRRRRRRRRRRRRRRRRRRRR
#      GGGGG:::::::::::::GGG   R::::::::::::::::::::::RR
#    GG::::::::::::::::::GGG   R::::::::RRRRRRRR::::::::R
#  G:::::::G       GGGGGGGGG   R::::::::R       R::::::::RR
# G:::::::G                    R::::::::R       R::::::::RR
# G:::::::G                    R::::::::RRRRRRRR::::::::R
# G:::::::G    GGGGGGGGGGGGG   R:::::::::::::::::::::RRR
# G:::::::G    G:::::::::GGG   R::::::::RRRRRRRR::::::::R
# G:::::::G    GGGGG:::::GGG   R::::::::R       R::::::::RR
#  G:::::::G       G:::::GGG   R::::::::R       R::::::::RR
#    GG::::::::::::::::::GGG   R::::::::R       R::::::::RR
#      GGGGG::::::GGG::::GGG   R::::::::R       R::::::::RR
#           GGGGGG   GGGGGGG   RRRRRRRRRR       RRRRRRRRRRR

# Imports
import discord
from discord.ext import commands
from keep_alive import keep_alive
from asyncio import sleep
import os

# Global variables
intents = discord.Intents.all() # Setup bot intents
activity = discord.Activity(type=discord.ActivityType.listening, name='Rap de anime') # Bot activity
client = commands.Bot(command_prefix="/", intents=intents, activity=activity) # Create bot client

# --- Events ---
# @client.event
# async def on_ready():
#     print("--- Ready ---")

# Cogs imports
initial_extensions = []
for filename in os.listdir("./cogs"):
    if (filename.endswith(".py")):
        initial_extensions.append("cogs." + filename[:-3])
if __name__ == "__main__":
    for extension in initial_extensions:
        client.load_extension(extension)

# Start bot
keep_alive()

try:
    client.run(os.environ['BOTTOKEN'])
except discord.errors.HTTPException as e:
    if e.status == 429:
        print("RATE LIMITED - RESTARTING...")
        sleep(10)
        os.system("python main.py")
        os.system('kill 1')