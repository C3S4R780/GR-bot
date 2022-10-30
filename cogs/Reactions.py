import nextcord
from nextcord import Interaction, SlashOption
from nextcord.ext import commands
import random
import requests
from apiKeys import JSONTOKEN

async def edit_reactions(interaction: Interaction, type: str, palavra: str, conteudo: str = ""):
    """
        JSON API: https://jsonbin.io/app/
    """
    headers = {
        'Content-Type': 'application/json',
        'X-Master-Key': JSONTOKEN
    }
    reactions = requests.get("https://api.jsonbin.io/v3/b/6353165c65b57a31e69e4b36?meta=false", headers=headers).json()

    if type == "add":
        response = "Reação criada com sucesso!"
        if palavra in reactions:
            response = "Reação atualizada com sucesso!"
        reactions[palavra] = conteudo

    if type == "del":
        if (reactions.get(palavra) == None):
            return await interaction.response.send_message(content="Reação não encontrada", ephemeral=True)
        del reactions[palavra]
        response = "Reação removida com sucesso!"

    req = requests.put("https://api.jsonbin.io/v3/b/6353165c65b57a31e69e4b36", json=reactions, headers=headers)

    if req.status_code == 200:
        await interaction.response.send_message(content=response, ephemeral=True)
    else:
        await interaction.response.send_message(content=f"Deu ruim, chama o <@614093922339127316>\n`Reactions.py: Error {req.status_code}`")

class Reactions(commands.Cog):
    def __init__(self, client):
        self.bot = client

    @commands.Cog.listener()
    async def on_message(self, msg):

        if not msg.author.bot:

            if "<@995790616745234482>" in msg.content:
                channel = self.bot.get_channel(msg.channel.id)
                await channel.send("Falou comigo?")

            headers = {
                'X-Master-Key': JSONTOKEN
            }
            reactions = requests.get("https://api.jsonbin.io/v3/b/6353165c65b57a31e69e4b36?meta=false", headers=headers).json()
            for reaction in reactions:
                if reaction.lower() in msg.content.lower():
                    channel = self.bot.get_channel(msg.channel.id)
                    await channel.send(reactions[reaction])

            if (random.randint(1,20) == 1):
                emojiList = ["😭", "👀", "🏳️‍🌈", "<:oxi:844587774137073674>", "<:kkkkkk:844588632655790081>", "<:fodase:933420784158904393>", "<:hmm:844586895946416158>"]
                await msg.add_reaction(emojiList[random.randint(0, 6)])

            if (random.randint(1,40) == 1):
                joke = requests.get("https://api-charadas.herokuapp.com/puzzle?lang=ptbr").json()
                channel = self.bot.get_channel(msg.channel.id)
                await channel.send(f"{msg.author.mention}, {joke.get('question')}\n **{joke.get('answer')}**")

            if (random.randint(1,1000) == 1):
                dm = await msg.author.create_dm()
                await dm.send("Mano, tu é ?? 🏳️‍🌈")

    @nextcord.slash_command(name="adicionar_reacao", description="Sempre que eu ver a palavra chave, irei reagir com o conteudo informado.")
    async def adicionar_reacao(self, interaction: Interaction, palavra: str = SlashOption(description="Qual palavra devo procurar ?"), conteudo: str = SlashOption(description="O que devo dizer ao reagir ?")):

        await edit_reactions(interaction,"add",palavra,conteudo)

    @nextcord.slash_command(name="remover_reacao", description="Escolha qual reação devo remover.")
    async def remover_reacao(self, interaction: Interaction, palavra: str = SlashOption(description="Qual palavra devo remover ?")):

        await edit_reactions(interaction,"del",palavra)

    @nextcord.slash_command(name="listar_reacao", description="Crio uma lista com todas as reações.")
    async def listar_reacao(self, interaction: Interaction):

        headers = {
            'Content-Type': 'application/json',
            'X-Master-Key': JSONTOKEN
        }
        reactions = requests.get("https://api.jsonbin.io/v3/b/6353165c65b57a31e69e4b36?meta=false", headers=headers).json()
        embed = nextcord.Embed(title="Lista de reações")

        for key, reaction in reactions.items():
            if "http://" in reaction or "https://" in reaction:
                embed.add_field(name=key, value=reaction, inline=False)
            else:
                embed.add_field(name=key, value=f"`{reaction}`", inline=False)

        await interaction.response.send_message(embed=embed, ephemeral=True)

def setup(client):
    client.add_cog(Reactions(client))
