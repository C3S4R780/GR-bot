import nextcord
from nextcord.ext import commands
import os
import openai
from asyncio import sleep

openai.api_key = os.environ['OPENAI_KEY']

def trim_msg(msg):
    msg = msg.content.replace("GR", "", 1)
    if msg and msg[0] == ",":
        msg = msg.replace(",", "", 1)

    return msg.strip()


class OpenAi(commands.Cog):
    def __init__(self, client):
        self.bot = client

    @commands.Cog.listener()
    async def on_message(self, msg):

        if msg.author.bot: return

        if msg.content == "GR": return

        if "GR" in msg.content:
            ctx = trim_msg(msg)

            if msg.channel.type == nextcord.ChannelType.public_thread:
                thread = msg.channel
                history = []

                await thread.trigger_typing()

                async for message in thread.history(limit=6):
                    role = "user"
                    ctx = trim_msg(message)

                    if message.author.bot: role = "assistant"

                    history.insert(0, {"role":role,"content":ctx})
                
                response = openai.ChatCompletion.create(
                    model="gpt-3.5-turbo",
                    temperature=0.5,
                    messages=history
                )

                await thread.send(response.choices[0].message.content)

                if 'vlw' in msg.content.lower():
                    await thread.send("Fechando o topico...")
                    await sleep(10)
                    return await thread.delete()

            else:
                await msg.channel.trigger_typing()
                
                response = openai.ChatCompletion.create(
                    model="gpt-3.5-turbo",    
                    temperature=0.5,
                    messages=[{
                        "role": "user",
                        "content": ctx
                    }]
                )
                
                prompt = await msg.reply(content=response.choices[0].message.content, mention_author=False)

                if "vlw" not in msg.content.lower():
                    await prompt.add_reaction("💬")

    @commands.Cog.listener()
    async def on_reaction_add(self, reaction, user):

        if user.bot: return
        
        if str(reaction.emoji) == "💬":
            last_user_msg = ""

            async for message in reaction.message.channel.history():
                if message.author.id == user.id and "GR" in message.content:
                    last_user_msg = message
                    break
    
            thread = await last_user_msg.create_thread(name=trim_msg(last_user_msg).replace("?", ""))
            
            await thread.send(f"{user.mention}\n{reaction.message.content}")
            await reaction.message.delete()

    # @nextcord.slash_command(name="gerar_imagem", description="Irei gerar uma imagem apartir de seu texto")
    # async def gerar_imagem(self, interaction: Interaction, texto: str = SlashOption(description="Descreva como a imagem devera ser criada")):

    #     response = await interaction.send("Carregando imagem...")

    #     async with interaction.channel.typing():
    #         request = openai.Image.create(
    #           prompt=texto,
    #         )
    #         embed = nextcord.Embed(description=f"_**{texto}**_ por {interaction.user.mention}")
    #         embed.set_image(request['data'][0]['url'])

    #     await response.edit(content="", embed=embed)


def setup(client):
    client.add_cog(OpenAi(client))
