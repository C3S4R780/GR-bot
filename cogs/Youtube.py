# Imports
import nextcord
from nextcord import Interaction, SlashOption
from nextcord.ext import commands
import wavelink
from UI.playerUI import QuitPrompt, songCard
class Youtube(commands.Cog):
    def __init__(self, client):
        self.bot = client
        client.loop.create_task(self.node_connect())

    async def node_connect(self):
        await self.bot.wait_until_ready()
        await wavelink.NodePool.create_node(bot=self.bot, host="lavalink.oops.wtf", port=443, password="www.freelavalink.ga", https=True)

    @commands.Cog.listener()
    async def on_wavelink_track_start(self, player: wavelink.Player, track: wavelink.Track):
        ctx = player.ctx
        vc: player = ctx.guild.voice_client
        setattr(vc, "loop", False)

    @commands.Cog.listener()
    async def on_wavelink_track_end(self, player: wavelink.Player, track: wavelink.Track, reason):
        ctx = player.ctx
        vc: player = ctx.guild.voice_client

        if vc.loop:
            return await vc.play(track)

        if not vc.queue.is_empty:
            next_song = vc.queue.get()
            await songCard(next_song, ctx)
            await vc.play(next_song)

    # Command to call the bot into voice chat and play the especified youtube video
    @nextcord.slash_command(name="yt", description="Me chama para tocar algo do youtube no canal de voz atual 😁")
    async def yt(self, interaction: Interaction, musica: str = SlashOption(description="Nome ou URL do video")):

        if not (interaction.user.voice):
            return await interaction.send(content="⚠️ Você precisar estar em um canal de voz para usar este comando.", ephemeral=True)

        userVoiceChannel = interaction.user.voice.channel

        if (interaction.client.voice_clients):
            for voice_client in interaction.client.voice_clients:
                if voice_client.channel == userVoiceChannel:
                    if not hasattr(voice_client, 'queue'):
                        voice_client.cleanup()
                        await voice_client.disconnect()
                        vc: wavelink.Player = await userVoiceChannel.connect(cls=wavelink.Player)
                        break
                    vc: wavelink.Player = voice_client
                else:
                    return await interaction.send("⚠️ Você precisa estar no mesmo canal de voz que eu para usar este comando", ephemeral=True)
        else:
            vc: wavelink.Player = await userVoiceChannel.connect(cls=wavelink.Player)

        search = await wavelink.YouTubeTrack.search(query=musica, return_first=True)
        vc.ctx = interaction

        if vc.is_playing():
            await vc.queue.put_wait(search)
            return await interaction.send(f"{interaction.user.mention} adicionou `{search.title}` a lista")

        await songCard(search, interaction)

        await vc.play(search)

    # Command to remove the bot from the current voice channel
    @nextcord.slash_command(name="sair", description="Me remove do canal de voz 😔")
    async def sair(self, interaction: Interaction):

        if (interaction.client.voice_clients):
            for client in interaction.client.voice_clients:

                if (client.channel != interaction.user.voice.channel):
                    return await interaction.response.send_message(content="⚠️ Você não está no mesmo canal para me remover.", ephemeral=True)

                if (hasattr(client, "queue") and not client.queue.is_empty):
                    view = QuitPrompt()
                    await interaction.send(content="Ainda tem musica na fila, deseja mesmo que eu saia ?", view=view, delete_after=30)
                    await view.wait()

                    if (view.value == None):
                        return
                    elif (view.value == "quit"):
                        client.cleanup()
                        await client.disconnect()
                        await interaction.send(content=f"{interaction.user.mention} me mando sair 😔")
                    else:
                        await interaction.delete_original_message()

                else:
                    client.cleanup()
                    await client.disconnect()
                    await interaction.send(content="❤️ Até a proxima.")

        else:
            await interaction.send(content="⚠️ Ainda não estou em nenhum canal de voz.", ephemeral=True)

def setup(client):
    client.add_cog(Youtube(client))