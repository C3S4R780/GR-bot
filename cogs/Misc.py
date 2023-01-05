import nextcord
from nextcord import Interaction, SlashOption
from nextcord.ext import commands
from asyncio import sleep
import random

class Misc(commands.Cog):
    def __init__(self, client):
        self.bot = client

    # Command to make the bot say something
    @nextcord.slash_command(name="diga", description="Me faça dizer algo 😁")
    async def diga(self, interaction: Interaction, msg: str = SlashOption(name="texto", description="O que devo dizer ?")):

        # Responds the interaction with an empty message and deletes it right after
        await interaction.send(content="⠀", ephemeral=True, delete_after=0.1)

        # Get the current channel
        channel = self.bot.get_channel(interaction.channel_id)

        # Simulate the bot typing for 1 to 4 seconds
        async with channel.typing():
            await sleep(random.randint(2,4))

        # Send the specified message, as the bot, to the current channel
        return await channel.send(msg)

def setup(client):
    client.add_cog(Misc(client))