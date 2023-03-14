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

    # Creates a lavalink node
    async def node_connect(self):
        await self.bot.wait_until_ready()
        await wavelink.NodePool.create_node(bot=self.bot, host="node1.kartadharta.xyz", port=443, password="kdlavalink", https=True)

    # --- Events ---
    # When a new music starts...
    @commands.Cog.listener()
    async def on_wavelink_track_start(self, player: wavelink.Player, track: wavelink.Track):

        # Pass the current player context and voice client
        ctx = player.ctx
        vc: player = ctx.guild.voice_client

        # Creates and sets the loop attribute to false
        if not hasattr(vc, 'loop'):
            setattr(vc, "loop", False)

    # When the music ends...
    @commands.Cog.listener()
    async def on_wavelink_track_end(self, player: wavelink.Player, track: wavelink.Track, reason):

        # Pass the current player context and voice client
        ctx = player.ctx
        vc: player = ctx.guild.voice_client

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

    # --- Commands ---
    # Calls the bot into voice chat and play the specified youtube video
    @nextcord.slash_command(name="yt", description="Me chama para tocar algo do youtube no canal de voz atual 😁")
    async def yt(self, interaction: Interaction, musica:str = SlashOption(description="Nome ou URL do video")):

        # If the user is not in a voice channel...
        if not (interaction.user.voice):
            return await interaction.send(content="⚠️ Você precisar estar em um canal de voz para usar este comando.", ephemeral=True)

        # Get the user's voice channel
        userVoiceChannel = interaction.user.voice.channel

        # If the bot is already in a voice channel...
        if (interaction.client.voice_clients):
            for voice_client in interaction.client.voice_clients:

                # If the user is not in the same voice channel...
                if (voice_client.channel != userVoiceChannel):
                    return await interaction.response.send_message(content="⚠️ Você não está no mesmo canal para me remover.", ephemeral=True)

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

        # Get the first search result for the song requested
        search = await wavelink.YouTubeTrack.search(query=musica, return_first=True)

        # Initiate the client context
        vc.ctx = interaction

        # If the bot is already playing a song...
        if vc.is_playing():

            # Put the requested song in queue
            await vc.queue.put_wait(search)
            return await interaction.send(f"{interaction.user.mention} adicionou `{search.title}` a lista")

        # Create a song card with controls for the current song
        await songCard(search, interaction)

        # Play the requested song
        await vc.play(search)

    # Command to remove the bot from the current voice channel
    # WORKS FOR THE RADIO COMMAND TOO
    @nextcord.slash_command(name="sair", description="Me remove do canal de voz 😔")
    async def sair(self, interaction: Interaction):

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

def setup(client):
    client.add_cog(Youtube(client))