# Imports
import nextcord
from nextcord.ext import commands
import wavelink
import os
from apiKeys import *

# Global variables
intents = nextcord.Intents.all() # Setup bot intents
client = commands.Bot(command_prefix="/", intents=intents) # Create bot client

# --- Aux ---
async def node_connect():
    await client.wait_until_ready()
    await wavelink.NodePool.create_node(bot=client, host="lavalink.oops.wtf", port=443, password="www.freelavalink.ga", https=True)

# --- Events ---
@client.event
async def on_ready():
    client.loop.create_task(node_connect())

initial_extensions = []

for filename in os.listdir("./cogs"):
    if (filename.endswith(".py")):
        initial_extensions.append("cogs." + filename[:-3])

if __name__ == "__main__":
    for extension in initial_extensions:
        client.load_extension(extension)

# Start bot
client.run(BOTTOKEN)