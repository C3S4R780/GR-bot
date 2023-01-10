import nextcord
from nextcord import Interaction, SlashOption
from nextcord.ext import commands
from asyncio import sleep
import random
from apiKeys import DM_ID

class Misc(commands.Cog):
    def __init__(self, client):
        self.bot = client

    @commands.Cog.listener()
    async def on_message(self, msg):

        if not msg.channel.type == nextcord.ChannelType.private: return
        if msg.author.bot: return

        my_dm = await self.bot.fetch_user(DM_ID)
        await my_dm.send(
            f"{msg.author.mention}` | {msg.author.display_name}: {msg.content}`"
        )

    # Command to make the bot say something
    @nextcord.slash_command(name="diga", description="Me faça dizer algo 😁")
    async def diga(self, interaction: Interaction, msg: str = SlashOption(name="texto", description="O que devo dizer ?"), user_id = SlashOption(name="enviar_para", description="Envia esta mensagem para a DM do usuario selecionado", required=False)):

        # Responds the interaction with an empty message and deletes it right after
        await interaction.send(content="⠀", ephemeral=True, delete_after=0.1)

        if interaction.channel.type == nextcord.ChannelType.private:
            if user_id and user_id != f"<@{DM_ID}>":
                await interaction.send(f"Você: `{msg}`")

        # If a user was given...
        if user_id:

            # Extract the specified user id from the string
            try:
                user_id = int(user_id.translate({ord(i): None for i in '<@>'}))
            except ValueError:
                return await interaction.send(content="para de trola e manda um usuario valido pora", ephemeral=True)

            # Get the speficied user
            user = nextcord.Client.get_user(self.bot, user_id)

            # Skip command if the specified user is a bot
            if user.bot: return await interaction.send(content="Num vo manda DM pra bot caraio", ephemeral=True)

            # Creates a new DM instance and sends the message to it
            user_dm = await user.create_dm()
            return await user_dm.send(msg)

        # Get the current channel
        channel = self.bot.get_channel(interaction.channel_id)

        # Simulate the bot typing for 1 to 4 seconds
        async with channel.typing():
            await sleep(random.randint(1,4))

        # Send the specified message, as the bot, to the current channel
        return await channel.send(msg)

def setup(client):
    client.add_cog(Misc(client))