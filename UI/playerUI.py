# Imports
import discord
from discord import Interaction, Color
import wavelink
import datetime

def get_current_client(interaction):
    if (interaction.client.voice_clients):
        for voice_client in interaction.client.voice_clients:
            if voice_client.channel == interaction.user.voice.channel:
                return voice_client
    else: return None


class YoutubeControls(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.value = None
        self.paused = False

    @discord.ui.button(emoji="⏯️")
    async def toggle_pause(self, button: discord.ui.Button, interaction: Interaction):
        vc: wavelink.Player = get_current_client(interaction)

        if self.paused:
            button.style = discord.ButtonStyle.gray
            await interaction.edit(view=self)
            self.paused = False
            return await vc.resume()

        else:
            button.style = discord.ButtonStyle.red
            await interaction.edit(view=self)
            self.paused = True
            return await vc.pause()

    @discord.ui.button(emoji="⏭️")
    async def pular(self, button: discord.ui.Button, interaction: Interaction):
        vc: wavelink.Player = get_current_client(interaction)

        if vc.loop: return await vc.play(vc.source)

        if not vc.queue.is_empty:
            next_song = vc.queue.get()
            await songCard(next_song, interaction)
            await vc.play(next_song)
        else:
            await vc.stop()

        self.stop()

    @discord.ui.button(emoji="🔁")
    async def loop(self, button: discord.ui.Button, interaction: Interaction):
        vc: wavelink.Player = get_current_client(interaction)

        if (not hasattr(vc, 'loop')):
            setattr(vc, "loop", False)

        if vc.loop == False:
            vc.loop = True
            button.style = discord.ButtonStyle.green
            await interaction.edit(view=self)

        else:
            vc.loop = False
            button.style = discord.ButtonStyle.gray
            await interaction.edit(view=self)

    @discord.ui.button(emoji="📃")
    async def song_list(self, button: discord.ui.Button, interaction: Interaction):
        vc: wavelink.Player = get_current_client(interaction)

        list_duration = 0
        for song in vc.queue:
            list_duration += song.length

        embed = discord.Embed(title="Fila:", description=f"Duração da fila: `{datetime.timedelta(seconds=list_duration)}`")
        if not vc.queue.is_empty:
            i = 0
            for song in vc.queue:
                i += 1
                title = f"`{i}. {song.title[:16] + '...' if len(song.title) > 20 else song.title}`"
                embed.add_field(name="", value=title, inline=False)
            await interaction.response.send_message(embed=embed, ephemeral=True)
        else:
            await interaction.response.send_message("A fila esta vazia", delete_after=5, ephemeral=True)

    @discord.ui.button(emoji="❤️")
    async def favorite(self, button: discord.ui.Button, interaction: Interaction):
        vc: wavelink.Player = get_current_client(interaction)

        dm = await interaction.user.create_dm()
        await dm.send(f"Ta na mão chefe:\n{vc.source.uri}")

class QuitPrompt(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=30)
        self.value = None

    @discord.ui.button(emoji="✅")
    async def quit(self, button: discord.ui.Button, interaction: Interaction):
        self.value = "quit"
        self.stop()

    @discord.ui.button(emoji="❌")
    async def cancel(self, button: discord.ui.Button, interaction: Interaction):
        self.value = False
        self.stop()

async def songCard(song: wavelink.Playable, interaction: Interaction):
    vc: wavelink.Player = get_current_client(interaction)
    view = YoutubeControls()

    embed = discord.Embed(title=f"💿 `{song.title}`", url=song.uri, description=f"🕒 Duração: `{str(datetime.timedelta(seconds=song.length))}`", colour=Color.from_rgb(255,0,0))

    embed.set_image(song.thumbnail)

    if len(vc.queue) > 0:
        embed.set_footer(text=f"{len(vc.queue)} musicas restantes | Proxima: {vc.queue[0].title[:32]+'...' if len(vc.queue[0].title) > 35 else vc.queue[0].title}")

    return await interaction.response.send_message(embed=embed, view=view)