# Imports
import datetime
import discord
import nextcord
from nextcord import Interaction, SlashOption, Color
from nextcord.ext import commands
import wavelink

async def song_card(song: wavelink.YouTubeTrack, interaction: Interaction):
    view = YoutubeControls(song.length)
    embed = nextcord.Embed(title=f"💿 `{song.title}`", url=song.uri, description=f"🎶 Adicionada por: {interaction.user.mention} | 🕒 Duração: `{str(datetime.timedelta(seconds=song.length))}`", colour=Color.from_rgb(255,0,0))
    embed.set_image(f"https://img.youtube.com/vi/{song.info.get('identifier')}/maxresdefault.jpg")
    return await interaction.send(embed=embed, view=view)

class YoutubeControls(nextcord.ui.View):
    def __init__(self, song_duration):
        super().__init__(timeout=song_duration)
        self.value = None
        self.paused = False

    @nextcord.ui.button(emoji="⏯️")
    async def toggle_pause(self, button: nextcord.ui.Button, interaction: Interaction):
        if (interaction.client.voice_clients):
            vc: wavelink.Player = None
            for voice_client in interaction.client.voice_clients:
                if voice_client.channel == interaction.user.voice.channel:
                    vc: wavelink.Player = voice_client

            if self.paused:
                button.style = button.style = discord.ButtonStyle.gray
                await interaction.edit(view=self)
                self.paused = False
                return await vc.resume()

            else:
                button.style = button.style = discord.ButtonStyle.red
                await interaction.edit(view=self)
                self.paused = True
                return await vc.pause()

        self.value = "toggle_pause"

    @nextcord.ui.button(emoji="⏭️")
    async def pular(self, button: nextcord.ui.Button, interaction: Interaction):
        if (interaction.client.voice_clients):
            vc: wavelink.Player = None
            for voice_client in interaction.client.voice_clients:
                if voice_client.channel == interaction.user.voice.channel:
                    vc: wavelink.Player = voice_client

            await vc.seek(vc.track.length*1000)
            if not vc.queue.is_empty:
                await interaction.message.delete()
        self.value = "skip"

    @nextcord.ui.button(emoji="🔁")
    async def loop(self, button: nextcord.ui.Button, interaction: Interaction):
        if (interaction.client.voice_clients):
            for voice_client in interaction.client.voice_clients:
                if voice_client.channel == interaction.user.voice.channel:
                    vc: wavelink.Player = voice_client
            if vc.loop == False:
                vc.loop = True
                self.timeout = None
                button.style = discord.ButtonStyle.green
                await interaction.edit(view=self)
            else:
                vc.loop = False
                self.timeout = 180
                button.style = discord.ButtonStyle.gray
                await interaction.edit(view=self)
        self.value = "loop"

    @nextcord.ui.button(emoji="📃")
    async def song_list(self, button: nextcord.ui.Button, interaction: Interaction):
        if (interaction.client.voice_clients):
            for voice_client in interaction.client.voice_clients:
                if voice_client.channel == interaction.user.voice.channel:
                    vc: wavelink.Player = voice_client
            i = 0
            list_duration = 0
            for song in vc.queue:
                list_duration += song.length

            embed = nextcord.Embed(title="Fila:", description=f"Duração da fila: `{datetime.timedelta(seconds=list_duration)}`")
            if not vc.queue.is_empty:
                for song in vc.queue:
                    i += 1
                    embed.add_field(name=f"{i}. ", value=f"`{song.title}` por {interaction.user.mention}", inline=False)
                await interaction.send(embed=embed, ephemeral=True)
            else:
                await interaction.send("A fila esta vazia", delete_after=5, ephemeral=True)

        self.value = "song_list"

    @nextcord.ui.button(emoji="❤️")
    async def favorite(self, button: nextcord.ui.Button, interaction: Interaction):
        if (interaction.client.voice_clients):
            for voice_client in interaction.client.voice_clients:
                if voice_client.channel == interaction.user.voice.channel:
                    vc: wavelink.Player = voice_client
            dm = await interaction.user.create_dm()
            await dm.send(f"Ta na mão chefe:\n{vc.track.uri}")

        self.value = "favorite"

class Youtube(commands.Cog):
    def __init__(self, client):
        self.bot = client
        client.loop.create_task(self.node_connect())

    async def node_connect(self):
        await self.bot.wait_until_ready()
        await wavelink.NodePool.create_node(bot=self.bot, host="lavalink.oops.wtf", port=443, password="www.freelavalink.ga", https=True)

    @commands.Cog.listener()
    async def on_wavelink_track_end(self, player: wavelink.Player, track: wavelink.Track, reason):
        ctx = player.ctx
        vc: player = ctx.guild.voice_client

        if vc.loop:
            return await vc.play(track)

        if not vc.queue.is_empty:
            next_song = vc.queue.get()
            await song_card(next_song, ctx)
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
                    vc: wavelink.Player = voice_client
                else:
                    return await interaction.send("⚠️ Você precisa estar no mesmo canal de voz que eu para usar este comando", ephemeral=True)
        else:
            vc: wavelink.Player = await userVoiceChannel.connect(cls=wavelink.Player)

        search = await wavelink.YouTubeTrack.search(query=musica, return_first=True)
        self.song = search
        vc.ctx = self.interaction = interaction
        setattr(vc, "loop", False)

        if vc.is_playing():
            await vc.queue.put_wait(search)
            return await interaction.send(f"{interaction.user.mention} adicionou `{search.title}` a lista")

        await song_card(search, interaction)

        await vc.play(search)

def setup(client):
    client.add_cog(Youtube(client))