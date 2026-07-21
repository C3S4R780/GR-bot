import os
import json
import openai
import discord
from discord import app_commands, Interaction, ChannelType, Message
from discord.ext import commands
from ollama import AsyncClient
from asyncio import sleep
from enum import Enum


client = AsyncClient(host='http://localhost:11434')

with open('behavior.txt', 'r', encoding='utf-8') as file:
    behavior = file.read()

Members = Enum('Members', [
    ("614093922339127316", "Cezinha"),
    ("530607879627997185", "Matheuzin"),
    ("294965660184739840", "Nandin"),
    ("612318925408960512", "Vitú"),
    ("1074100566126497832", "Vitão")
])


def trim_msg(msg):
    msg = msg.content.replace("GR", "", 1)
    if msg and msg[0] == ",":
        msg = msg.replace(",", "", 1)

    return msg.strip()


async def ai_response(msg: Message, history = []):
    message = await msg.channel.send('Pensante...')
    full_response = ""
    buffer = ""

    history.insert(0, {
        "role": "system",
        "content": behavior
    })

    try:
        stream = await client.chat(
            model='qwen3:8b',
            messages=history,
            stream=True,
        )

        async for chunk in stream:
            content = chunk['message']['content']
            full_response += content
            buffer += content

            if len(buffer) >= 40:
                await message.edit(content=f"{full_response} ▌")
                await sleep(0.5)
                buffer = ""

        await message.edit(content=full_response)

    except Exception as e:
        print(f"Error: {e}")
        await message.edit(content="⚠️ An error occurred while contacting Ollama.")


class OpenAi(commands.Cog):
    def __init__(self, client):
        self.bot = client


    @commands.Cog.listener()
    async def on_message(self, msg: Message):
        if msg.author.bot or msg.content == "GR": return

        history = []

        if msg.channel.type == ChannelType.private:
            dm = msg.channel

            async for message in dm.history(limit=6):
                role = "assistant" if message.author.bot else "user"
                content = message.content if message.author.bot else f'({Members[str(msg.author.id)].value}){message.content}'

                history.insert(0, {"role": role, "content": content})

            return await ai_response(msg, history)

        if "GR" in msg.content:
            return await ai_response(msg, [{
                "role": "assistant" if msg.author.bot else "user",
                "content": f'({Members[str(msg.author.id)].value}){msg.content}'
            }])

    @commands.Cog.listener()
    async def on_reaction_add(self, reaction, user):

        if user.bot: return

        if str(reaction.emoji) == "💬":
            last_user_msg = ""

            async for message in reaction.message.channel.history():
                if message.author.id == user.id and "GR" in message.content:
                    last_user_msg = message
                    break

            thread = await last_user_msg.create_thread(name=trim_msg(last_user_msg)[:99].replace("?", ""))

            await thread.send(f"{user.mention}\n{reaction.message.content}")
            await reaction.message.delete()

    # @app_commands.command(name="personalidade", description="Descreva como devo responder futuras mensagens")
    # async def personalidade(self, interaction: Interaction, prompt: str):
    #     """Descreva como devo responder futuras mensagens 😁"""

    #     await interaction.response.defer()

    #     with open("behaviour.json", "w") as behaviourFile:
    #         if interaction.channel.type == ChannelType.private:
    #             behaviourList[str(interaction.user.id)] = prompt
    #         else:
    #             behaviourList['0'] = prompt

    #         json.dump(behaviourList, behaviourFile)

    #     await interaction.response.send_message("Personalidade alterada com sucesso!", ephemeral=True)


    # @discord.slash_command(name="gerar_imagem", description="Irei gerar uma imagem apartir de seu texto")
    # async def gerar_imagem(self, interaction: Interaction, texto: str = SlashOption(description="Descreva como a imagem devera ser criada")):

    #     response = await interaction.response.send_message("Carregando imagem...")

    #     async with interaction.channel.typing():
    #         request = openai.Image.create(
    #           prompt=texto,
    #         )
    #         embed = discord.Embed(description=f"_**{texto}**_ por {interaction.user.mention}")
    #         embed.set_image(request['data'][0]['url'])

    #     await response.edit(content="", embed=embed)


async def setup(client):
    await client.add_cog(OpenAi(client))