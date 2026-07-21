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
from discord import Intents, CustomActivity
from discord.ext import commands
from apiKeys import BOTTOKEN


class GrBot(commands.Bot):
    def __init__(self):
        super().__init__(
            command_prefix="!",
            intents=Intents.all(),
            activity=CustomActivity(name="⚡ STAY RUNNING 🥊")
        )


    async def on_ready(self):
        # os.system("cls")
        print("GR-Bot online!")


    async def setup_hook(self):
        for filename in os.listdir("./cogs"):
            if (filename.endswith(".py")):
                await self.load_extension(f"cogs.{filename[:-3]}")


GrBot().run(BOTTOKEN)
