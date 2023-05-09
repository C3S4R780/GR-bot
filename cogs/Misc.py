import os
import random
import requests
import urllib.request
import textwrap
import nextcord
from nextcord import Interaction, SlashOption, Message
from nextcord.ext import commands
from asyncio import sleep
from PIL import Image, ImageDraw, ImageFilter, ImageEnhance, ImageFont

def load_img(url, filename):
    opener = urllib.request.build_opener()
    opener.addheaders = [('User-Agent', 'Chrome')]
    urllib.request.install_opener(opener)
    urllib.request.urlretrieve(url, f"./imgs/{filename}")
    return f'./imgs/{filename}'

class Misc(commands.Cog):
    def __init__(self, client):
        self.bot = client

    @commands.Cog.listener()
    async def on_message(self, msg):

        if not msg.channel.type == nextcord.ChannelType.private: return
        if msg.author.bot: return

        my_dm = await self.bot.fetch_user(os.environ['DM_ID'])
        await my_dm.send(
            f"`{msg.author.mention} | {msg.author.display_name}: {msg.content}`"
        )

    # Command to make the bot say something
    @nextcord.slash_command(name="diga", description="Me faça dizer algo 😁")
    async def diga(self, interaction: Interaction, msg: str = SlashOption(name="texto", description="O que devo dizer ?"), user_id = SlashOption(name="enviar_para", description="Envia esta mensagem para a DM do usuario selecionado", required=False)):

        # Responds the interaction with an empty message and deletes it right after
        await interaction.send(content="⠀", ephemeral=True, delete_after=0.1)

        if interaction.channel.type == nextcord.ChannelType.private:
            if user_id and user_id != f"<@{os.environ['DM_ID']}>":
                await interaction.send(f"Você: `{msg}`")

        # If a user was given...
        if user_id:

            # Extract the specified user id from the string
            try:
                user_id = int(user_id.translate({ord(i): None for i in '<@>'}))
            except ValueError:
                return await interaction.send(content="para de trola e manda um usuario valido pora", ephemeral=True)

            # Get the speficied user
            user = nextcord.Client.get_user(self.bot, user_id)

            # Skip command if the specified user is a bot
            if user.bot: return await interaction.send(content="Num vo manda DM pra bot caraio", ephemeral=True)

            # Creates a new DM instance and sends the message to it
            user_dm = await user.create_dm()
            return await user_dm.send(msg)

        # Get the current channel
        channel = self.bot.get_channel(interaction.channel_id)

        # Simulate the bot typing for 1 to 4 seconds
        async with channel.typing():
            await sleep(random.randint(1,4))

        # Send the specified message, as the bot, to the current channel
        return await channel.send(msg)

    @nextcord.slash_command(name="roleta_lol", description="Te desafio a fazer uma build extremamente idiota (ou não) com um campeão, itens e runas aleatorias")
    async def roleta_lol(self, interaction: Interaction):

                                    ###############################################
                                    ##    TODO: Add random summoner's spells     ##
                                    ###############################################
        
        response = await interaction.send(content="Carregando...")
        icon_size = 125
        rune_size = 65
        stat_size = 35
        version = requests.get("https://ddragon.leagueoflegends.com/realms/br.json").json()['v']
        champs = requests.get(f"https://ddragon.leagueoflegends.com/cdn/{version}/data/pt_BR/champion.json").json()['data']
        champ_name, champ_data = random.choice(list(champs.items()))
        
        splash = Image.open(load_img(
            f"https://ddragon.leagueoflegends.com/cdn/img/champion/centered/{champ_data.get('id')}_0.jpg",
            f"{champ_data.get('id')}_0.jpg"
        ))
        
        items = requests.get(f"https://ddragon.leagueoflegends.com/cdn/{version}/data/pt_BR/item.json").json()['data']
        item_icon_base_url = f"https://ddragon.leagueoflegends.com/cdn/{version}/img/item/"
        item_list = [
            item for item in items
            if items[item].get('requiredAlly') is None and
            items[item].get('requiredChampion') is None and
            items[item].get('inStore') is None and
            not "Consumable" in items[item].get('tags') and
            not "Trinket" in items[item].get('tags') and
            not "Lane" in items[item].get('tags') and
            not "Jungle" in items[item].get('tags')
        ]
        mythics = [
            item for item in item_list
            if items[item].get('description').find("Mythic") != -1
        ]
        legendaries = [
            item for item in item_list
            if items[item].get('into') is None and
            "Boots" not in items[item].get('tags') and
            items[item].get('description').find("Mythic") == -1
        ]
        boots = [
            item for item in item_list
            if items[item].get('into') is None and
            "Boots" in items[item].get('tags')
        ]
        
        mythic = random.choice(mythics)
        mythic_icon_url = f"{item_icon_base_url}{items[mythic].get('image').get('full')}"
        with Image.open(load_img(
            mythic_icon_url,
            items[mythic].get('image').get('full')
        )) as mythic_icon:
            mythic_icon = mythic_icon.resize((icon_size, icon_size), Image.Resampling.LANCZOS)
            splash.paste(mythic_icon)

        row = 0
        column = 1
        for i in range(1, 5):
            legendary = random.choice(legendaries)
            legendary_icon_name = items[legendary].get('image').get('full')
            with Image.open(load_img(
                f"{item_icon_base_url}{legendary_icon_name}",
                legendary_icon_name
            )) as legendary_icon:
                if i == 3: 
                    row += 1
                    column = 0
                legendary_icon = legendary_icon.resize((icon_size, icon_size), Image.Resampling.LANCZOS)
                splash.paste(legendary_icon, (icon_size*column, icon_size*row))
                column += 1

        boot = random.choice(boots)
        boot_icon_name = items[boot].get('image').get('full')
        with Image.open(load_img(
            f"{item_icon_base_url}{boot_icon_name}",
            boot_icon_name
        )) as boot_icon:
            boot_icon = boot_icon.resize((icon_size, icon_size), Image.Resampling.LANCZOS)
            splash.paste(boot_icon, (icon_size*2, icon_size*row))

        rune_pages = requests.get(f"https://ddragon.leagueoflegends.com/cdn/{version}/data/pt_BR/runesReforged.json").json()
        rune_icon_base_url = "https://ddragon.leagueoflegends.com/cdn/img/"
        primary_page = random.choice(rune_pages)
        secondary_page = random.choice(rune_pages)

        if primary_page.get('name') == secondary_page.get('name'):
            secondary_page = random.choice(rune_pages)

        main_rune = random.choice(primary_page.get('slots')[0].get('runes'))
        with Image.open(load_img(
            f"{rune_icon_base_url}{main_rune.get('icon')}",
            main_rune.get('icon').split("/")[-1]
        )) as main_rune_icon:
            main_rune_icon = main_rune_icon.resize((icon_size, icon_size), Image.Resampling.LANCZOS)
            splash.paste(main_rune_icon, (1035, 0))

        column = 1000
        for i in range(1, 4):
            rune = random.choice(primary_page.get('slots')[i].get('runes'))
            with Image.open(load_img(
                f"{rune_icon_base_url}{rune.get('icon')}",
                rune.get('icon').split("/")[-1]
            )) as rune_icon:
                rune_icon = rune_icon.resize((rune_size, rune_size), Image.Resampling.LANCZOS)
                splash.paste(rune_icon, (column, 125))
                column += rune_size

        column = 1035
        for i in range(2):
            x = random.randint(1, 3)
            rune = random.choice(secondary_page.get('slots')[x].get('runes'))
            with Image.open(load_img(
                f"{rune_icon_base_url}{rune.get('icon')}",
                rune.get('icon').split("/")[-1]
            )) as rune_icon:
                rune_icon = rune_icon.resize((rune_size, rune_size), Image.Resampling.LANCZOS)
                splash.paste(rune_icon, (column, 190))
                column += rune_size

        stat_mods = {
            0: ["AdaptiveForceIcon", "AttackSpeedIcon", "CDRScalingIcon"],
            1: ["AdaptiveForceIcon", "ArmorIcon", "MagicResIcon.MagicResist_Fix"],
            2: ["HealthScalingIcon", "ArmorIcon", "MagicResIcon.MagicResist_Fix"]
        }

        column = 1050
        for i in range(3):
            with Image.open(load_img(
                f"{rune_icon_base_url}perk-images/StatMods/StatMods{random.choice(stat_mods[i])}.png",
                rune.get('icon').split("/")[-1]
            )) as stat_icon:
                stat_icon = stat_icon.resize((stat_size, stat_size), Image.Resampling.LANCZOS)
                splash.paste(stat_icon, (column, 255))
                column += stat_size

        splash.save(f"./imgs/build.png")

        await response.edit(content=f"> **{champ_name}**", file=nextcord.File("./imgs/build.png"))

        for file in os.scandir('./imgs'):
            os.remove(file.path)


    @nextcord.message_command(name="Filosofar")
    async def filosofar(self, interaction: Interaction, msg: Message):
        if not msg.content:
            return await interaction.send("Esta mensagem não possue texto.", ephemeral=True)

        img = Image.new(mode="RGB", size=(1280, 720))
        with Image.open(load_img(
            msg.author.display_avatar.url,
            "pfp.png"
        )) as pfp:
            pfp = pfp.resize((720, 720), Image.Resampling.LANCZOS)
            pfp = pfp.convert("L")
            pfp = ImageEnhance.Brightness(pfp).enhance(0.5)

            mask_im = Image.new("L", pfp.size, 0)
            draw = ImageDraw.Draw(mask_im)
            draw.rectangle((0, 0, pfp.width-100, pfp.height), fill=255)
            mask_im.save('./imgs/mask_circle.jpg')

            mask_im_blur = mask_im.filter(ImageFilter.GaussianBlur(15))
            mask_im_blur.save('./imgs/mask_circle_blur.jpg')
            img.paste(pfp, (-200, 0), mask_im_blur)

        W,H = img.size
        d_img = ImageDraw.Draw(img)
        font = ImageFont.truetype('./UI/fonts/Garamond-MediumItalic.ttf', 72)

        i = 0
        text = '“ '
        for line in msg.content.split(" "):
            if not i==0 and i%4==0: text += "\n"
            text += line+" "
            i += 1
        text += '„'

        _, _, w, h = d_img.textbbox((0, 0), text, font=font)
        d_img.text((((W-w)/2)+200, (H-h)/2), text, font=font)
            
        
        text = f'~ {msg.author.display_name}'
        font = ImageFont.truetype('./UI/fonts/Garamond-MediumItalic.ttf', 38)
        d_img.text((470, H-80), text, font=font)

        img.save("./imgs/quote.png")

        await interaction.send(file=nextcord.File("./imgs/quote.png"))

        for file in os.scandir('./imgs'):
            os.remove(file.path)

def setup(client):
    client.add_cog(Misc(client))