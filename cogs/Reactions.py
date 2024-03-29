# Imports
import nextcord
from nextcord import Interaction, SlashOption
from nextcord.ext import commands
import os
import random
import requests

# Get all reactions
headers = {
    'Content-Type': 'application/json',
    'X-Master-Key': os.environ['JSONTOKEN']
}
reactions = requests.get("https://api.jsonbin.io/v3/b/6353165c65b57a31e69e4b36?meta=false", headers=headers)
if (reactions.status_code == 200):
    reactions = reactions.json()

# Add, edit or delete the specified reaction
async def edit_reactions(interaction: Interaction, type: str, palavra: str, conteudo: str = ""):
    """
        JSON API: https://jsonbin.io/app/
    """

    # Adding a reaction to the list
    if type == "add":
        response = "Reação criada com sucesso!"

        # If the reaction already exists...
        if palavra in reactions:
            response = "Reação atualizada com sucesso!"

        # Add/edit the reaction
        reactions[palavra] = conteudo

    # Deleting a reaction from the list
    if type == "del":

        # If the reaction doesnt exists...
        if (reactions.get(palavra) == None):
            return await interaction.response.send_message(content="Reação não encontrada", ephemeral=True)

        # Remove the reaction from the list
        del reactions[palavra]
        response = "Reação removida com sucesso!"

    # Update the reaction list
    req = requests.put("https://api.jsonbin.io/v3/b/6353165c65b57a31e69e4b36", json=reactions, headers=headers)

    if req.status_code == 200:
        await interaction.response.send_message(content=response, ephemeral=True)
    else:
        await interaction.response.send_message(content=f"Deu ruim, chama o <@{os.environ['DM_ID']}>\n`Reactions.py: Error {req.status_code}`")

class Reactions(commands.Cog):
    def __init__(self, client):
        self.bot = client

    @commands.Cog.listener()
    async def on_message(self, msg):

        if msg.author.bot or msg.channel.type == nextcord.ChannelType.public_thread: return

        if "<@995790616745234482>" in msg.content:
            channel = self.bot.get_channel(msg.channel.id)
            await channel.send("Falou comigo?")

        for reaction in reactions:
            if reaction.lower() in msg.content.lower():
                channel = self.bot.get_channel(msg.channel.id)
                await channel.send(reactions[reaction])

        if (random.randint(1,20) == 1):
            emojiList = ["😭", "👀", "🏳️‍🌈", "<:oxi:844587774137073674>", "<:kkkkkk:844588632655790081>", "<:fodase:933420784158904393>", "<:hmm:844586895946416158>"]
            await msg.add_reaction(emojiList[random.randint(0, 6)])

        if (random.randint(1,1000) == 1):
            dm = await msg.author.create_dm()
            await dm.send("Mano, tu é ?? 🏳️‍🌈")

        # F API de piada
        # if (random.randint(1,40) == 1):
        #     joke = requests.get("https://api-charadas.herokuapp.com/puzzle?lang=ptbr")
        #     if (joke.status_code == 200):
        #         joke = joke.json()
        #         channel = self.bot.get_channel(msg.channel.id)
        #         await channel.send(f"{msg.author.mention}, {joke.get('question')}\n **{joke.get('answer')}**")

    @nextcord.slash_command(name="adicionar_reacao", description="Sempre que eu ver a palavra chave, irei reagir com o conteudo informado.")
    async def adicionar_reacao(self, interaction: Interaction, palavra: str = SlashOption(description="Qual palavra devo procurar ?"), conteudo: str = SlashOption(description="O que devo dizer ao reagir ?")):

        await edit_reactions(interaction,"add",palavra,conteudo)

    @nextcord.slash_command(name="remover_reacao", description="Escolha qual reação devo remover.")
    async def remover_reacao(self, interaction: Interaction, palavra: str = SlashOption(description="Qual palavra devo remover ?")):

        await edit_reactions(interaction,"del",palavra)

    @nextcord.slash_command(name="listar_reacao", description="Crio uma lista com todas as reações.")
    async def listar_reacao(self, interaction: Interaction):

        embed = nextcord.Embed(title="Lista de reações")

        for key, reaction in reactions.items():
            if "http://" in reaction or "https://" in reaction:
                embed.add_field(name=key, value=reaction, inline=False)
            else:
                embed.add_field(name=key, value=f"`{reaction}`", inline=False)

        await interaction.response.send_message(embed=embed, ephemeral=True)

def setup(client):
    client.add_cog(Reactions(client))
