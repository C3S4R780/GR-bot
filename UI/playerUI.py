# Imports
import nextcord
from nextcord import Interaction, Color
import nextwave as wavelink
import datetime

def get_current_client(interaction):
    if (interaction.client.voice_clients):
        for voice_client in interaction.client.voice_clients:
            if voice_client.channel == interaction.user.voice.channel:
                return voice_client
    else: return None


class YoutubeControls(nextcord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.value = None
        self.paused = False

    @nextcord.ui.button(emoji="⏯️")
    async def toggle_pause(self, button: nextcord.ui.Button, interaction: Interaction):
        vc: wavelink.Player = get_current_client(interaction)

        if self.paused:
            button.style = nextcord.ButtonStyle.gray
            await interaction.edit(view=self)
            self.paused = False
            return await vc.resume()

        else:
            button.style = nextcord.ButtonStyle.red
            await interaction.edit(view=self)
            self.paused = True
            return await vc.pause()

    @nextcord.ui.button(emoji="⏭️")
    async def pular(self, button: nextcord.ui.Button, interaction: Interaction):
        vc: wavelink.Player = get_current_client(interaction)

        if (not hasattr(vc, 'loop')):
            setattr(vc, "loop", False)

        if (vc.loop):
            return await vc.play(vc.source)

        if not (vc.queue.is_empty):
            next_song = vc.queue.get()
            await songCard(next_song, interaction)
            await vc.play(next_song)
        else:
            await vc.stop()

    @nextcord.ui.button(emoji="🔁")
    async def loop(self, button: nextcord.ui.Button, interaction: Interaction):
        vc: wavelink.Player = get_current_client(interaction)

        if (not hasattr(vc, 'loop')):
            setattr(vc, "loop", False)

        if vc.loop == False:
            vc.loop = True
            button.style = nextcord.ButtonStyle.green
            await interaction.edit(view=self)

        else:
            vc.loop = False
            button.style = nextcord.ButtonStyle.gray
            await interaction.edit(view=self)

    @nextcord.ui.button(emoji="📃")
    async def song_list(self, button: nextcord.ui.Button, interaction: Interaction):
        vc: wavelink.Player = get_current_client(interaction)

        list_duration = 0
        for song in vc.queue:
            list_duration += song.length

        embed = nextcord.Embed(title="Fila:", description=f"Duração da fila: `{datetime.timedelta(seconds=list_duration)}`")
        if not vc.queue.is_empty:
            i = 0
            for song in vc.queue:
                i += 1
                embed.add_field(name=f"{i}. ", value=f"`{song.title}`", inline=False)
            await interaction.send(embed=embed, ephemeral=True)
        else:
            await interaction.send("A fila esta vazia", delete_after=5, ephemeral=True)

    @nextcord.ui.button(emoji="❤️")
    async def favorite(self, button: nextcord.ui.Button, interaction: Interaction):
        vc: wavelink.Player = get_current_client(interaction)

        dm = await interaction.user.create_dm()
        await dm.send(f"Ta na mão chefe:\n{vc.source.uri}")

class QuitPrompt(nextcord.ui.View):
    def __init__(self):
        super().__init__(timeout=30)
        self.value = None

    @nextcord.ui.button(emoji="✅")
    async def quit(self, button: nextcord.ui.Button, interaction: Interaction):
        self.value = "quit"
        self.stop()

    @nextcord.ui.button(emoji="❌")
    async def cancel(self, button: nextcord.ui.Button, interaction: Interaction):
        self.value = False
        self.stop()

async def songCard(song: wavelink.YouTubeTrack, interaction: Interaction):
    view = YoutubeControls()
    embed = nextcord.Embed(title=f"💿 `{song.title}`", url=song.uri, description=f"🎶 Adicionada por: {interaction.user.mention} | 🕒 Duração: `{str(datetime.timedelta(seconds=song.length))}`", colour=Color.from_rgb(255,0,0))
    embed.set_image(song.thumbnail)
    return await interaction.send(embed=embed, view=view)