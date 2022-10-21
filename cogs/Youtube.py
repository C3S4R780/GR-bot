# Imports
import datetime
import nextcord
from nextcord import Interaction, SlashOption
from nextcord.ext import commands
import wavelink

class Youtube(commands.Cog):
    def __init__(self, client):
        self.bot = client

    # Command to call the bot into voice chat and play the especified youtube video
    @nextcord.slash_command(name="yt_tocar", description="Me chama para tocar algo do youtube no canal de voz atual 😁")
    async def yt_tocar(self, interaction: Interaction, musica: str = SlashOption(description="Nome ou URL do video")):
        search = await wavelink.YouTubeTrack.search(query=musica, return_first=True)

        if not (interaction.guild.voice_client):
            vc: wavelink.Player = await interaction.user.voice.channel.connect(cls=wavelink.Player)
        else:
            vc: wavelink.Player = interaction.user.voice.channel

        embed = nextcord.Embed(title=f"`{search.title}`", url=search.uri, description=f"Adicionada por: {interaction.user.mention} | Duração: `{str(datetime.timedelta(seconds=search.length))}`")
        embed.set_image(f"https://img.youtube.com/vi/{search.info.get('identifier')}/0.jpg")

        await interaction.response.send_message(embed=embed)

        await vc.play(search)

    @nextcord.slash_command(name="yt_parar", description="Desligo o youtube")
    async def yt_parar(self, interaction: Interaction):
        if not (interaction.guild.voice_client):
            vc: wavelink.Player = await interaction.user.voice.channel.connect(cls=wavelink.Player)
        else:
            vc: wavelink.Player = interaction.user.voice.channel

        await vc.stop()

def setup(client):
    client.add_cog(Youtube(client))