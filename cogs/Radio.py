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
                            source = FFmpegPCMAudio(radio)
                            client.play(source)
                            await interaction.send(content=f"{interaction.user.mention} mudou para a radio `{radioName}`")

                        # If the user cancels the prompt...
                        else:

                            # Dismiss the prompt message
                            await interaction.delete_original_message()

                # If the bot is already playing a radio...
                if (client.is_playing()):

                    # Change the radio channel
                    source = FFmpegPCMAudio(radio)
                    client.source = source
                    await interaction.response.send_message(f"✅ Agora tocando: `{radioName}`")

        # Bot is not in a voice channel...
        else:

            # Connects the bot into the user's voice channel and plays the radio
            source = FFmpegPCMAudio(radio)
            voice = await userVoiceChannel.connect()
            voice.play(source)
            await interaction.response.send_message(f"✅ Tocando `{radioName}` no `{userVoiceChannel.name}`")

def setup(client):
    client.add_cog(Radio(client))