# Imports
import nextcord
from nextcord.ext import commands
import os
from apiKeys import BOTTOKEN

# Global variables
intents = nextcord.Intents.all() # Setup bot intents
activity = nextcord.Activity(type=nextcord.ActivityType.listening, name='Rap de anime') # Bot activity
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
client.run(BOTTOKEN)