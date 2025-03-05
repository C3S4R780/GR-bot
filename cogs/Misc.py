import os
import random
import urllib.request
from discord import app_commands, Interaction, File
from discord.ext import commands
from asyncio import sleep
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def load_img(url, filename) -> str:
    opener = urllib.request.build_opener()
    opener.addheaders = [('User-Agent', 'Chrome')]
    urllib.request.install_opener(opener)
    urllib.request.urlretrieve(url, f"./imgs/{filename}")
    return f'./imgs/{filename}'


async def scrap_burning_font(msg: str) -> str:
    options = webdriver.ChromeOptions()
    options.add_argument('--no-sandbox')
    options.add_argument('headless')
    options.add_argument("--headless")
    options.add_argument('--disable-gpu')
    options.add_argument('--disable-infobars')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--remote-debugging-port=9222')

    driver = webdriver.Chrome(options=options)
    wait = WebDriverWait(driver, 20)

    driver.get('https://cooltext.com/Logo-Design-Burning')
    current_url = driver.current_url

    query = driver.find_element(By.XPATH, '/html/body/table/tbody/tr[2]/td[2]/div[1]/div/form/div[1]/table/tbody/tr[1]/td[2]/textarea')

    query.send_keys(msg)
    await sleep(3)

    actions = ActionChains(driver)
    actions.send_keys(Keys.TAB * 4)
    actions.send_keys(Keys.ENTER)
    actions.perform()

    wait.until(EC.url_changes(current_url))

    img = driver.find_element(By.XPATH, '/html/body/table/tbody/tr[2]/td[2]/center[1]/a/img')
    img_url = img.get_attribute('src')

    driver.quit()

    return load_img(img_url, f"{msg}.gif")

class Misc(commands.Cog):
    def __init__(self, client: commands.Bot):
        self.bot = client


    @commands.Cog.listener()
    async def on_ready(self):
        await self.bot.tree.sync()


    @app_commands.command()
    async def diga(self, interaction: Interaction, mensagem: str):
        """Me faça dizer algo 😁

        Parameters
        -----------
        mensagem: str
            O que devo dizer ?
        """

        # Responds the interaction with an empty message and deletes it right after
        await interaction.response.send_message(content="⠀", ephemeral=True, delete_after=0.1)

        # Get the current channel
        channel = self.bot.get_channel(interaction.channel_id)

        # Simulate the bot typing for 1 to 4 seconds
        async with channel.typing():
            await sleep(random.randint(1, 4))

        # Send the specified message, as the bot, to the current channel
        return await channel.send(content=mensagem)


    @app_commands.command()
    async def putu(self, interaction: Interaction, mensagem: str):
        """Mande uma mensagem com fonte flamejante pra mostrar o quão puto vc ta 😡

        Parameters
        -----------
        mensagem: str
            A mensagem a ser escrita em fonte flamejante...
        """
        await interaction.response.defer(thinking=True)

        img = await scrap_burning_font(mensagem)
        await interaction.followup.send(file=File(img))

        for file in os.scandir('./imgs'):
            os.remove(file.path)


async def setup(client):
    await client.add_cog(Misc(client))
