# Imports
from discord import Client, app_commands, Interaction
from discord.ext import commands
import wavelink
from UI.playerUI import QuitPrompt, songCard


class Youtube(commands.Cog):
    def __init__(self, client: Client):
        self.bot = client


    # --- Events ---
    @commands.Cog.listener()
    async def on_ready(self):
        await self.bot.tree.sync()


    @commands.Cog.listener()
    async def on_wavelink_node_ready(self, payload):
        print("Lavalink node connected")

    # When a new music starts...
    @commands.Cog.listener()
    async def on_wavelink_track_start(self, player: wavelink.Player, track: wavelink.TrackSource):

        # Pass the current player context and voice client
        ctx = player.ctx
        vc: player = ctx.guild.voice_client

        # Creates and sets the loop attribute to false
        if not hasattr(vc, 'loop'):
            setattr(vc, "loop", False)

        # Change bot status to show song title
        # await self.bot.change_presence(activity=discord.Activity(
        #     type=discord.ActivityType.listening,
        #     name=track.title
        # ))

    # When the music ends...
    @commands.Cog.listener()
    async def on_wavelink_track_end(self, player: wavelink.Player, track: wavelink.TrackSource, reason):

        # Pass the current player context and voice client
        ctx = player.ctx
        vc: player = ctx.guild.voice_client

        print("song ended")

        # If loop is active...
        if vc.loop:

            # Replay current track
            return await vc.play(track)

        # If the queue is not empty...
        if not vc.queue.is_empty:

            # Get the next song
            next_song = vc.queue.get()

            # Create the song card to the next song...
            await songCard(next_song, ctx)

            # Play the next song in queue
            await vc.play(next_song)

        # else:
            # Change bot status back to normal
            # await self.bot.change_presence(activity=discord.Activity(
            #     type=discord.ActivityType.watching,
            #     name="Hentai"
            # ))


    # --- Commands ---
    # Calls the bot into voice chat and play the specified youtube video
    @app_commands.command()
    async def yt(self, interaction: Interaction, musica: str):
        """Me chama para tocar algo do youtube no canal de voz atual 😁

        Parameters
        ----------
        musica: str
            Nome ou URL do video
        """

        # If the user is not in a voice channel...
        if not (interaction.user.voice):
            return await interaction.send(content="⚠️ Você precisar estar em um canal de voz para usar este comando.", ephemeral=True)

        await interaction.response.defer()

        # Get the user's voice channel
        userVoiceChannel = interaction.user.voice.channel

        # If the bot is already in a voice channel...
        if (interaction.client.voice_clients):
            for voice_client in interaction.client.voice_clients:

                # If the user is not in the same voice channel...
                if (voice_client.channel != userVoiceChannel):
                    return await interaction.resp
                    onse.send_message(content="⚠️ Você não está no mesmo canal para me remover.", ephemeral=True)

                # If the bot doesnt have the queue attribute... (is playing radio)
                if not hasattr(voice_client, 'queue'):

                    # Removes the radio client
                    voice_client.cleanup()
                    await voice_client.disconnect()

                    # Reconnect with the wavelink client
                    vc: wavelink.Player = await userVoiceChannel.connect(cls=wavelink.Player)

                    # Exit for loop
                    break

                # Sets the voice client to the current bot channel
                vc: wavelink.Player = voice_client

        # Bot is not in a voice channel...
        else:
            vc: wavelink.Player = await userVoiceChannel.connect(cls=wavelink.Player)

        timestamp = 0

        # Get the first search result for the song requested
        if "?list=" in musica or "&list=" in musica:
            search = await wavelink.YouTubePlaylist.search(query=musica)
        elif "?t=" in musica:
            timestamp = int(musica.split("?t=")[1])
            search = await wavelink.Playable.search(query=musica.split("?t=")[0], return_first=True)
        elif "&t=" in musica:
            timestamp = int(musica.split("&t=")[1])
            search = await wavelink.Playable.search(query=musica.split("&t=")[0], return_first=True)
        else:
            search = await wavelink.Playable.search(query=musica, return_first=True)

        # Initiate the client context
        vc.ctx = interaction
        if (not hasattr(vc, 'loop')):
            setattr(vc, "loop", False)

        # If the bot is already playing a song...
        if vc.is_playing():

            # Put the requested song in queue
            if isinstance(search, wavelink.YouTubePlaylist):
                for track in search.tracks:
                    await vc.queue.put_wait(track)
                return await interaction.send(f"{interaction.user.mention} adicionou `{len(search.tracks)}` musicas da playlist `{search.name}`")
            else:
                await vc.queue.put_wait(search)
                return await interaction.send(f"{interaction.user.mention} adicionou `{search.title}`")

        # Play the requested song
        index = int(musica.split("index=")[1])-1 if "index=" in musica else 0
        if isinstance(search, wavelink.YouTubePlaylist):
            for track in search.tracks:
                await vc.queue.put_wait(track)
            await interaction.send(f"{interaction.user.mention} adicionou `{len(search.tracks)}` musicas da playlist `{search.name}`")
            await vc.play(vc.queue[index])
            del vc.queue[index]
        else:
            await vc.play(search)

        await vc.seek(timestamp*1000)

        # Create a song card with controls for the current song
        if isinstance(search, wavelink.YouTubePlaylist):
            await songCard(search.tracks[index], interaction)
        else:
            await songCard(search, interaction)

    # Command to remove the bot from the current voice channel
    # WORKS FOR THE RADIO COMMAND TOO
    @app_commands.command()
    async def sair(self, interaction: Interaction):
        """Me remove do canal de voz 😔"""

        # If the bot is already in a voice channel...
        if (interaction.client.voice_clients):
            for client in interaction.client.voice_clients:

                # If the user is not in the same voice channel...
                if (client.channel != interaction.user.voice.channel):
                    return await interaction.response.send_message(content="⚠️ Você não está no mesmo canal para me remover.", ephemeral=True)

                # If the bot has a queue attribute, AND the queue is NOT empty...
                if (hasattr(client, "queue") and not client.queue.is_empty):

                    # Sends a prompt to confirm removing the bot while the queue is not finished
                    view = QuitPrompt()
                    await interaction.send(content="Ainda tem musica na fila, deseja mesmo que eu saia ?", view=view, delete_after=30)

                    # Await user response...
                    await view.wait()
                    if (view.value == None): return

                    # If the user confirms the prompt...
                    elif (view.value == "quit"):
                        await interaction.send(content=f"{interaction.user.mention} me mando sair 😔")

                    # User declined the prompt...
                    else:
                        return await interaction.delete_original_message()

                # Queue is empty...
                else:
                    await interaction.send(content="❤️ Até a proxima.")

                # Disconnect the bot
                client.cleanup()
                await client.disconnect()

        # Bot is not in a voice channel...
        else:
            await interaction.send(content="⚠️ Ainda não estou em nenhum canal de voz.", ephemeral=True)

async def setup(client):
    await client.add_cog(Youtube(client))