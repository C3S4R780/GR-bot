import nextcord
from nextcord import Interaction, SlashOption
from nextcord.ext import commands
import json
import random
import requests

class Reactions(commands.Cog):
    def __init__(self, client):
        self.bot = client

    @commands.Cog.listener()
    async def on_message(self, msg):
        if not msg.author.bot:

            reactions = json.load(open("reactions.json", encoding='utf-8'))
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

        # if " " in palavra:
        #     return await interaction.response.send_message(content="A palavra chave não pode ter espaços", ephemeral=True)

        reactions = open("reactions.json", "r", encoding='utf-8')
        reaction_list = json.load(reactions)
        reactions.close()

        response = "Reação criada com sucesso!"
        if palavra in reaction_list:
            response = "Reação atualizada com sucesso!"

        reaction_list[palavra] = conteudo

        reactions = open("reactions.json", "w", encoding='utf-8')
        json.dump(reaction_list, reactions)
        reactions.close()

        await interaction.response.send_message(content=response, ephemeral=True)

    @nextcord.slash_command(name="remover_reacao", description="Escolha qual reação devo remover.")
    async def remover_reacao(self, interaction: Interaction, palavra: str = SlashOption(description="Qual palavra devo remover ?")):

        reactions = open("reactions.json", "r", encoding='utf-8')
        reaction_list = json.load(reactions)
        reactions.close()

        if (reaction_list.get(palavra) == None):
            return await interaction.response.send_message(content="Reação não encontrada", ephemeral=True)

        del reaction_list[palavra]

        reactions = open("reactions.json", "w", encoding='utf-8')
        json.dump(reaction_list, reactions)
        reactions.close()

        await interaction.response.send_message(content="Reação removida com sucesso!", ephemeral=True)

    @nextcord.slash_command(name="listar_reacao", description="Crio uma lista com todas as reações.")
    async def listar_reacao(self, interaction: Interaction):

        reactions = json.load(open("reactions.json", encoding='utf-8'))
        embed = nextcord.Embed(title="Lista de reações")

        for key, reaction in reactions.items():
            if "http://" in reaction or "https://" in reaction:
                embed.add_field(name=key, value=reaction, inline=False)
            else:
                embed.add_field(name=key, value=f"`{reaction}`", inline=False)

        await interaction.response.send_message(embed=embed, ephemeral=True)

def setup(client):
    client.add_cog(Reactions(client))