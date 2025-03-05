# Imports
import os
import random
import requests
from discord import (
    app_commands,
    Client,
    Interaction,
    Message,
    ChannelType,
    Embed
)
from discord.ext import commands
from apiKeys import JSONTOKEN, DM_ID

# Get all reactions
headers = {
    'Content-Type': 'application/json',
    'X-Master-Key': JSONTOKEN
}
reactions = requests.get(
    "https://api.jsonbin.io/v3/b/6353165c65b57a31e69e4b36?meta=false",
    headers=headers
)
if reactions.status_code == 200 : reactions = reactions.json()

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
    req = requests.put(
        "https://api.jsonbin.io/v3/b/6353165c65b57a31e69e4b36",
        json=reactions,
        headers=headers
    )

    if req.status_code == 200:
        await interaction.response.send_message(content=response, ephemeral=True)
    else:
        await interaction.response.send_message(content=f"Deu ruim, chama o <@{DM_ID}>\n`Reactions.py: Error {req.status_code}`")

class Reactions(commands.Cog):
    def __init__(self, client: Client):
        self.bot = client


    @commands.Cog.listener()
    async def on_ready(self):
        await self.bot.tree.sync()


    @commands.Cog.listener()
    async def on_message(self, msg: Message):

        if msg.author.bot or msg.channel.type == ChannelType.public_thread: return

        if "<@995790616745234482>" in msg.content:
            channel = self.bot.get_channel(msg.channel.id)
            await channel.send("Falou comigo?")

        for reaction in reactions:
            if reaction.lower() in msg.content.lower().split():
                channel = self.bot.get_channel(msg.channel.id)
                await channel.send(reactions[reaction])

        if (random.randint(1,10) == 1):
            emojiList = [
                "😍", "😡", "😎", "🤓", "😔", "😭", "👀", "🏳️‍🌈", "🙏", "💀", "🤨",
                "<:oxi:844587774137073674>", "<:kkkkkk:844588632655790081>", "<:fodase:933420784158904393>", "<:hmm:844586895946416158>", "<:why:879890992742948934>", "<:withered:1074511835115573278>", "<:rammusOk:968525457974775879>", "<:uwu:844586224231383050>", "<:nando:880505240007352410>", "<:fml:844584183996219403>", "<:ahegao:844313243317043230>", "<:fuhua:862531780800282625>"
            ]
            await msg.add_reaction(random.choice(emojiList))

        if (random.randint(1,1000) == 1):
            dm = await msg.author.create_dm()
            await dm.send("Mano, tu é ?? 🏳️‍🌈")


        # Enviar uma mensagem se houver 3 ocorrencias da mesma por 3 usuarios diferentes
        msgList = []
        userList = []
        async for message in msg.channel.history(limit=3):
            if message.author.bot or message.author.id in userList: continue
            userList.append(message.author.id)
            msgList.append(message.content)

        if len(msgList) == 3 and len(set(msgList)) == 1:
            await msg.channel.send(msgList[0])

        # F API de piada
        # if (random.randint(1,40) == 1):
        #     joke = requests.get("https://api-charadas.herokuapp.com/puzzle?lang=ptbr")
        #     if (joke.status_code == 200):
        #         joke = joke.json()
        #         channel = self.bot.get_channel(msg.channel.id)
        #         await channel.send(f"{msg.author.mention}, {joke.get('question')}\n **{joke.get('answer')}**")


    @app_commands.command()
    async def adicionar_reacao(self, interaction: Interaction, palavra: str, conteudo: str):
        """Sempre que eu ver a palavra chave, irei reagir com o conteudo informado.

        Parameters
        -----------
        palavra: str
            Qual palavra devo procurar ?
        conteudo: str
            O que devo dizer/mostrar ao reagir ?
        """
        await edit_reactions(interaction, "add", palavra,conteudo)


    @app_commands.command()
    async def remover_reacao(self, interaction: Interaction, palavra: str):
        """Escolha qual reação devo remover.

        Parameters
        -----------
        palavra: str
            Qual palavra devo remover ?
        """
        await edit_reactions(interaction, "del", palavra)


    @app_commands.command()
    async def listar_reacao(self, interaction: Interaction):
        """Mostro uma lista com todas as reações."""
        embed = Embed(title="Lista de reações")

        for key, reaction in reactions.items():
            if "http://" in reaction or "https://" in reaction:
                embed.add_field(name=key, value=reaction, inline=False)
            else:
                embed.add_field(name=key, value=f"`{reaction}`", inline=False)

        await interaction.response.send_message(embed=embed, ephemeral=True)


async def setup(client):
    await client.add_cog(Reactions(client))
