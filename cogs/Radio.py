# Imports
import nextcord
from nextcord import Interaction, FFmpegPCMAudio, SlashOption
from nextcord.ext import commands
import json
from UI.playerUI import QuitPrompt

# Get list of radios
radios = json.load(open("radios.json"))

class Radio(commands.Cog):

    def __init__(self, client):
        self.bot = client

    # --- Commands ---
    # Command to call the bot into voice chat and play the radio's audio
    @nextcord.slash_command(name="radio", description="Me chama para o canal de voz atual para tocar a rádio 😁")
    async def radio(self, interaction: Interaction, radio:str = SlashOption(name="radio", description="Qual rádio devo tocar ?", choices=radios)):

        # If the user is not in a voice channel...
        if not (interaction.user.voice):
            await interaction.response.send_message(content="⚠️ Você precisar estar em um canal de voz para usar este comando.", ephemeral=True)
            return

        # Getting user's current voice channel
        userVoiceChannel = interaction.user.voice.channel

        # Get the name of the selected radio
        radioName = ""
        for key in radios.keys():
            if (radios[key] == radio):
                radioName = key

        # If the bot is already in a voice channel...
        if (interaction.client.voice_clients):
            for client in interaction.client.voice_clients:

                # If its the same channel as the user...
                if client.channel == userVoiceChannel:

                    if (hasattr(client, 'queue')):
                        if not (client.queue.is_empty):
                            view = QuitPrompt()
                            await interaction.send(content="Ainda tem musica na fila, deseja mesmo que eu saia ?", view=view, delete_after=30)
                            await view.wait()

                            if (view.value == None):
                                return
                            elif (view.value == "quit"):
                                client.cleanup()
                                await client.disconnect()
                                client = await userVoiceChannel.connect()
                                source = FFmpegPCMAudio(radio)
                                client.play(source)
                                await interaction.send(content=f"{interaction.user.mention} mudou para a radio `{radioName}`")
                            else:
                                await interaction.delete_original_message()

                    # If the bot is already playing a radio...
                    if (client.is_playing()):

                        # Change the radio channel
                        source = FFmpegPCMAudio(radio)
                        client.source = source
                        await interaction.response.send_message(f"✅ Agora tocando: `{radioName}`")

        else:
            # Connects the bot into the user's voice channel and plays the audio
            source = FFmpegPCMAudio(radio)
            voice = await userVoiceChannel.connect()
            voice.play(source)
            await interaction.response.send_message(f"✅ Tocando `{radioName}` no `{userVoiceChannel.name}`")

def setup(client):
    client.add_cog(Radio(client))