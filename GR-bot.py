"""
           GGGGGGGGGGGGGGGG   RRRRRRRRRRRRRRRRRRRRRRR
      GGGGG:::::::::::::GGG   R::::::::::::::::::::::RR
    GG::::::::::::::::::GGG   R::::::::RRRRRRRR::::::::R
  G:::::::G       GGGGGGGGG   R::::::::R       R::::::::RR
 G:::::::G                    R::::::::R       R::::::::RR
 G:::::::G                    R::::::::RRRRRRRR::::::::R
 G:::::::G    GGGGGGGGGGGGG   R:::::::::::::::::::::RRR
 G:::::::G    G:::::::::GGG   R::::::::RRRRRRRR::::::::R
 G:::::::G    GGGGG:::::GGG   R::::::::R       R::::::::RR
  G:::::::G       G:::::GGG   R::::::::R       R::::::::RR
    GG::::::::::::::::::GGG   R::::::::R       R::::::::RR
      GGGGG::::::GGG::::GGG   R::::::::R       R::::::::RR
           GGGGGG   GGGGGGG   RRRRRRRRRR       RRRRRRRRRRR
"""

# Imports
import os
import json
import pytz
import wavelink
from discord import Intents, CustomActivity, File
from discord.errors import HTTPException
from discord.ext import commands, tasks
from keep_alive import keep_alive
from asyncio import sleep, run
from datetime import datetime
from apiKeys import BOTTOKEN

with open("sextou.json") as file:
    sent = json.load(file)


class GrBot(commands.Bot):
    def __init__(self):
        super().__init__(
            command_prefix="/",
            intents=Intents.all(),
            activity=CustomActivity(name="⚡ STAY RUNNING 🥊")
        )


    async def on_ready(self):
        os.system("cls")
        print("GR-Bot online!")
        await self.tree.sync()
        self.sextou_loop.start()


    async def setup_hook(self):
        # print("initiating wavelink pool...")
        # await wavelink.Pool.connect(
        #     nodes=[wavelink.Node(
        #         client=self,
        #         uri="lavalink1.skybloxsystems.com",
        #         password="s4DarqP$&y"
        #     )],
        # )

        for filename in os.listdir("./cogs"):
            if (filename.endswith(".py")):
                await self.load_extension(f"cogs.{filename[:-3]}")


    @tasks.loop(seconds=30, reconnect=True)
    async def sextou_loop(self):
        global sent
        hoje = datetime.now(pytz.timezone('America/Sao_Paulo'))

        if hoje.weekday() == 4:
            if hoje.hour >= 8 and not sent['sent']:
                channel = self.get_channel(821937691167162382)
                await channel.send("@everyone", file=File('video/sextou_porra.mp4'))
                sent['sent'] = True

        else:
            sent['sent'] = False

        with open("sextou.json", "w") as file:
            json.dump(sent, file)


async def main():
    if __name__ == "__main__":
        async with GrBot() as bot:
            try:
                await bot.start(BOTTOKEN)

            except HTTPException as e:
                if e.status == 429:
                    print("RATE LIMITED - RESTARTING...")
                    sleep(10)
                    os.system("python main.py")
                    os.system('kill 1')


run(main())
