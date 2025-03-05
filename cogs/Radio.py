# Imports
import json
from discord import app_commands, Interaction, FFmpegOpusAudio
from discord.ext import commands
from UI.playerUI import QuitPrompt

radio_list: dict[str, str] = json.load(open("radios.json"))

class Radio(commands.Cog):
    def __init__(self, client):
        self.bot = client


    @commands.Cog.listener()
    async def on_ready(self):
        await self.bot.tree.sync()


    # --- Commands ---
    # Command to call the bot into voice chat and play the radio's audio
    @app_commands.command()
    @app_commands.choices(radio=[
        app_commands.Choice(name=radio, value=url)
        for (radio, url) in radio_list.items()
    ])
    async def radio(self, interaction: Interaction, radio: app_commands.Choice[str]):
        """Me chama para o canal de voz atual para tocar a rádio 😁

        Parameters
        ----------
        radio: app_commands.Choice[str]
            Qual radío devo tocar ?
        """

        # If the user is not in a voice channel...
        if not (interaction.user.voice):
            await interaction.response.send_message(content="⚠️ Você precisar estar em um canal de voz para usar este comando.", ephemeral=True)
            return

        # Getting user's current voice channel
        userVoiceChannel = interaction.user.voice.channel

        # If the bot is already in a voice channel...
        if (interaction.client.voice_clients):

            for client in interaction.client.voice_clients:

                # If the user is not in the same voice channel as the bot...
                if client.channel != userVoiceChannel:
                    return await interaction.response.send_message(content="⚠️ Você precisar estar no mesmo canal de voz para usar este comando.", ephemeral=True)

                # If the client has the queue attribute... (is playing youtube)
                if (hasattr(client, 'queue')):

                    # If the queue is not empty...
                    if not (client.queue.is_empty):

                        # Gets the confirmation prompt to leave
                        view = QuitPrompt()
                        await interaction.send(content="Ainda tem musica na fila, deseja mesmo que eu saia ?", view=view, delete_after=30)

                        # Awating response...
                        await view.wait()
                        if (view.value == None): return

                        # If the user confirms the prompt...
                        elif (view.value == "quit"):

                            # Removes the youtube client
                            client.cleanup()
                            await client.disconnect()

                            # Creates the radio client and plays the selected radio
                            client = await userVoiceChannel.connect()
                            source = FFmpegOpusAudio(radio.value, bitrate=192)
                            client.play(source)
                            await interaction.send(content=f"{interaction.user.mention} mudou para a radio `{radio.name}`") 

                        # If the user cancels the prompt...
                        else:

                            # Dismiss the prompt message
                            await interaction.delete_original_message()

                # If the bot is already playing a radio...
                if (client.is_playing()):

                    # Change the radio channel
                    source = FFmpegOpusAudio(radio.value, bitrate=192)
                    client.source = source
                    await interaction.response.send_message(f"✅ Agora tocando: `{radio.name}`")

        # Bot is not in a voice channel...
        else:

            # Connects the bot into the user's voice channel and plays the radio
            source = FFmpegOpusAudio(radio.value, bitrate=192)
            voice = await userVoiceChannel.connect()
            voice.play(source)
            await interaction.response.send_message(f"✅ Tocando `{radio.name}` no <#{userVoiceChannel.id}>")


async def setup(client):
    await client.add_cog(Radio(client))