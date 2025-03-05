import os
from typing import List
import discord
import random
import requests
import urllib.request
from discord import app_commands, Interaction, Message
from discord.ext import commands
from PIL import Image, ImageDraw, ImageFilter, ImageEnhance, ImageFont

lol_version = requests.get("https://ddragon.leagueoflegends.com/realms/br.json").json()['v']
lol_root_cdn = "https://ddragon.leagueoflegends.com/cdn"
lol_current_cdn = f"{lol_root_cdn}/{lol_version}"

champ_list = requests.get(f"{lol_current_cdn}/data/pt_BR/champion.json").json()['data']
champ_list["Wukong"] = champ_list.pop("MonkeyKing")
champ_names = list(champ_list.keys())


async def champ_search(interaction: Interaction, name: str) -> List[app_commands.Choice[str]]:
    if not name:
        return [
            app_commands.Choice(name=champ, value=champ)
            for champ in random.choices(champ_names, k=10)
        ]

    return [
        app_commands.Choice(name=champ, value=champ)
        for champ in champ_names if champ.lower().startswith(name.lower())
    ]


def load_img(url, filename) -> str:
    opener = urllib.request.build_opener()
    opener.addheaders = [('User-Agent', 'Chrome')]
    urllib.request.install_opener(opener)
    urllib.request.urlretrieve(url, f"./imgs/{filename}")
    return f'./imgs/{filename}'


class ImageGeneration(commands.Cog):
    def __init__(self, client):
        self.bot = client
        self.ctx_menu = app_commands.ContextMenu(
            name="Filosofar",
            callback=self.filosofar,
        )
        self.bot.tree.add_command(self.ctx_menu)


    @commands.Cog.listener()
    async def on_ready(self):
        await self.bot.tree.sync()


    @app_commands.command()
    @app_commands.autocomplete(champ_name=champ_search)
    async def roleta_lol(self, interaction: Interaction, champ_name: str = None):
        """Te desafio a fazer uma build extremamente idiota (ou não) com um campeão, itens e runas aleatorias

        Parameters
        ----------
        campeão: str
            Escolha um campeão digitando o nome
        """
        global lol_root_cdn, lol_current_cdn, champ_list

        await interaction.response.defer()

        icon_size = 125
        rune_size = 75
        stat_size = 55

        if champ_name:
            champ_data = champ_list[champ_name]
        else:
            champ_name, champ_data = random.choice(list(champ_list.items()))

        splash = Image.open(load_img(
            f"{lol_root_cdn}/img/champion/centered/{champ_data.get('id')}_0.jpg",
            f"{champ_data.get('id')}_0.jpg"
        )).convert("RGBA")

        items = requests.get(f"{lol_current_cdn}/data/pt_BR/item.json").json()["data"]
        item_icon_base_url = f"{lol_current_cdn}/img/item"
        item_list = [
            item for item in items
            if items[item].get("requiredAlly")  is None and
            items[item].get("requiredChampion") is None and
            items[item].get("inStore")          is None and
            not "Consumable" in items[item].get("tags") and
            not "Trinket"    in items[item].get("tags") and
            not "Vision"     in items[item].get("tags") and
            not "Lane"       in items[item].get("tags") and
            not "GoldPer"    in items[item].get("tags") and
            not "Jungle"     in items[item].get("tags") and
            items[item].get("maps").get("11") == True   and
            items[item].get("maps").get("12") == True
        ]

        # mythics = [
        #     item for item in item_list
        #     if items[item].get('description').find("Mythic") != -1
        # ]

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

        # mythic = random.choice(mythics)
        # mythic_icon_url = f"{item_icon_base_url}/{items[mythic].get('image').get('full')}"
        # with Image.open(load_img(
        #     mythic_icon_url,
        #     items[mythic].get('image').get('full')
        # )) as mythic_icon:
        #     mythic_icon = mythic_icon.resize((icon_size, icon_size), Image.Resampling.LANCZOS)
        #     splash.paste(mythic_icon)

        row = 0
        column = 0
        inventory = []
        for i in range(5):
            legendary = random.choice(legendaries)

            while legendary in inventory:  # Prevent duplicate items
                legendary = random.choice(legendaries)

            inventory.append(legendary)
            legendary_icon_name = items[legendary].get('image').get('full')

            with Image.open(load_img(
                f"{item_icon_base_url}/{legendary_icon_name}",
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
            f"{item_icon_base_url}/{boot_icon_name}",
            boot_icon_name
        )) as boot_icon:
            boot_icon = boot_icon.resize((icon_size, icon_size), Image.Resampling.LANCZOS)
            splash.paste(boot_icon, (icon_size*2, icon_size*row))

        rune_pages = requests.get(f"{lol_current_cdn}/data/pt_BR/runesReforged.json").json()
        rune_icon_base_url = f"{lol_root_cdn}/img"
        primary_page = random.choice(rune_pages)
        secondary_page = random.choice(rune_pages)

        while primary_page.get('name') == secondary_page.get('name'):
            secondary_page = random.choice(rune_pages)

        main_rune = random.choice(primary_page.get('slots')[0].get('runes'))
        with Image.open(load_img(
            f"{rune_icon_base_url}/{main_rune.get('icon')}",
            main_rune.get('icon').split("/")[-1]
        )) as main_rune_icon:
            main_rune_icon = main_rune_icon.resize((icon_size, icon_size), Image.Resampling.LANCZOS)
            splash.paste(main_rune_icon, (1045, 0), main_rune_icon.convert("RGBA"))

        column = 995
        for i in range(1, 4):
            rune = random.choice(primary_page.get('slots')[i].get('runes'))
            with Image.open(load_img(
                f"{rune_icon_base_url}/{rune.get('icon')}",
                rune.get('icon').split("/")[-1]
            )) as rune_icon:
                rune_icon = rune_icon.resize((rune_size, rune_size), Image.Resampling.LANCZOS)
                splash.paste(rune_icon, (column, 120), rune_icon.convert("RGBA"))
                column += rune_size

        column = 1030
        prev_rune_row = 0
        for i in range(2):
            random_rune_row = random.randint(1, 3)
            while prev_rune_row == random_rune_row:
                random_rune_row = random.randint(1, 3)
            prev_rune_row = random_rune_row

            rune = random.choice(secondary_page.get('slots')[random_rune_row].get('runes'))
            with Image.open(load_img(
                f"{rune_icon_base_url}/{rune.get('icon')}",
                rune.get('icon').split("/")[-1]
            )) as rune_icon:
                rune_icon = rune_icon.resize((rune_size, rune_size), Image.Resampling.LANCZOS)
                splash.paste(rune_icon, (column, 200), rune_icon.convert("RGBA"))
                column += rune_size

        stat_mods = {
            0: ["AdaptiveForceIcon", "AttackSpeedIcon",   "CDRScalingIcon"],
            1: ["AdaptiveForceIcon", "MovementSpeedIcon", "HealthPlusIcon"],
            2: ["HealthScalingIcon", "TenacityIcon",      "HealthPlusIcon"]
        }

        column = 1025
        for i in range(0, len(stat_mods)):
            random_stat = f"StatMods{random.choice(stat_mods[i])}.png"
            with Image.open(load_img(
                f"{rune_icon_base_url}/perk-images/StatMods/{random_stat}",
                random_stat
            )) as stat_icon:
                stat_icon = stat_icon.resize((stat_size, stat_size), Image.Resampling.LANCZOS)
                splash.paste(stat_icon, (column, 275), stat_icon.convert("RGBA"))
                column += stat_size

        summoner_spells = requests.get(f"{lol_current_cdn}/data/pt_BR/summoner.json").json()['data']
        rift_spells = [
            spell for spell in summoner_spells
            if "CLASSIC" in summoner_spells[spell]['modes']
        ]
        spells = random.sample(rift_spells, 2)
        for i in range(0, len(spells)):
            with Image.open(load_img(
                f"{lol_current_cdn}/img/spell/{spells[i]}.png",
                f"{spells[i]}.png"
            )) as spell_icon:
                spell_icon = spell_icon.resize((icon_size, icon_size), Image.Resampling.LANCZOS)
                splash.paste(spell_icon, (1280-(icon_size*(i+1)), 720-icon_size))

        splash.save(f"./imgs/build.png")

        await interaction.send(content=f"# {champ_name}", file=discord.File("./imgs/build.png"))

        for file in os.scandir('./imgs'):
            os.remove(file.path)


    async def filosofar(self, interaction: Interaction, msg: Message):
        if not msg.content:
            return await interaction.send("Esta mensagem não possue texto.", ephemeral=True)

        await interaction.response.defer()

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

        await interaction.send(file=discord.File("./imgs/quote.png"))

        # for file in os.scandir('./imgs'):
        #     os.remove(file.path)

async def setup(client):
    await client.add_cog(ImageGeneration(client))