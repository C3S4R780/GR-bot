# Imports
import nextcord
from nextcord import Interaction, FFmpegPCMAudio, SlashOption
from nextcord.ext import commands
import json

class Radio(commands.Cog):

    def __init__(self, client):
        self.bot = client

    # Get list of radios
    radios = json.load(open("radios.json"))

    # --- Commands ---
    # Command to call the bot into voice chat and play the radio's audio
    @nextcord.slash_command(name="tocar", description="Me chama para o canal de voz atual para tocar a rádio 😁")
    async def tocar(self, interaction: Interaction, radio:str = SlashOption(name="radio", description="Qual rádio devo tocar ?", choices=radios)):

        # If the user is not in a voice channel...
        if not (interaction.user.voice):
            await interaction.response.send_message(content="⚠️ Você precisar estar em um canal de voz para usar este comando.", ephemeral=True)
            return

        # Getting user's current voice channel
        userVoiceChannel = interaction.user.voice.channel

        # If the bot is already in a voice channel...
        if (interaction.client.voice_clients):
            for client in interaction.client.voice_clients:

                # If its the same channel as the user...
                if client.channel == userVoiceChannel:
                    await interaction.response.send_message(content="⚠️ Já estou tocando nesse canal.", ephemeral=True)

                else:
                    # Getting the user's roles
                    roles = [];
                    for role in interaction.user.roles:
                        roles.append(role.name)

                    # If the user as the 'DJ' role...
                    if "DJ" in roles:

                        # Move the bot to the user's current voice channel
                        await interaction.response.send_message(content="🏃 Indo para o canal: " + userVoiceChannel.name, delete_after=20)
                        await client.move_to(userVoiceChannel)

                    else:
                        # Deny the action of changing the bot's current voice channel
                        await interaction.response.send_message(content="⚠️ Você não tem permissão para me mover de canal", ephemeral=True)

        else:
            # Connects the bot into the user's voice channel and plays the audio
            source = FFmpegPCMAudio(radio)
            voice = await userVoiceChannel.connect()
            voice.play(source)
            await interaction.response.send_message(content="✅ Tocando no canal: " + userVoiceChannel.name, delete_after=20)

    # Command to remove the bot from the current voice channel
    @nextcord.slash_command(name="sair", description="Me remove do canal de voz 😔")
    async def sair(self, interaction: Interaction):

        # If the bot is connected to a voice channel...
        if (interaction.client.voice_clients):
            for client in interaction.client.voice_clients:

                # If the user is not connected to the same voice channel...
                if (client.channel != interaction.user.voice.channel):
                    await interaction.response.send_message(content="⚠️ Você não está no mesmo canal para me remover.", ephemeral=True)

                else:
                    # Clears audio buffers and removes the bot from the voice channel
                    client.cleanup()
                    await client.disconnect()
                    await interaction.response.send_message(content="❤️ Até a proxima.", delete_after=20)

        else:
            # Warns the user that the bot is not connected to a voice channel
            await interaction.response.send_message(content="⚠️ Ainda não estou em nenhum canal de voz.", ephemeral=True)

    @nextcord.slash_command(name="mudar", description="Escolha qual rádio devo tocar agora 😁")
    async def mudar(self, interaction: Interaction, radio:str = SlashOption(name="radio", description="Qual rádio devo tocar ?",choices=radios)):

        # If the bot is connected to a voice channel...
        if (interaction.client.voice_clients):

            # If the user is not connected to the same voice channel...
            if (self.bot.channel != interaction.user.voice.channel):
                await interaction.response.send_message(content="⚠️ Você não está no mesmo canal para mudar a radio.", ephemeral=True)
                return

            for client in interaction.client.voice_clients:
                source = FFmpegPCMAudio(radio)
                client.stop()
                client.play(source)
                await interaction.response.send_message(content="✅ Rádio alterada com sucesso!", ephemeral=True)
        else:
            # Warns the user that the bot is not connected to a voice channel
            await interaction.response.send_message(content="⚠️ Ainda não estou em nenhum canal de voz.", ephemeral=True)

def setup(client):
    client.add_cog(Radio(client))