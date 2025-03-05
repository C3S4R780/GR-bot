import inspect
import random
import discord
from discord import app_commands, Interaction, Member
from discord.ui import View, Button
from discord.ext import commands
from asyncio import sleep

main_interaction: Interaction = None
player1: Member = None
player2: Member = None
shoot: bool = False

class DuelPrompt(View):
    def __init__(self):
        super().__init__(timeout=30)
        self.value = None


    async def valid_duelist(self) -> bool:
        global main_interaction, player2

        if main_interaction.user.id == player2.id:
            return True

        await main_interaction.followup.send(
            content=f"Esta decisão está nas mãos de {player2.display_name}.",
            ephemeral=True
        )
        return False


    @discord.ui.button(emoji="✅")
    async def accept(self, button: Button, interaction: Interaction):
        if not (await self.valid_duelist()):
            return

        self.value = "accept"
        self.stop()


    @discord.ui.button(emoji="❌")
    async def decline(self, button: Button, interaction: Interaction):
        if not await self.valid_duelist(): return

        self.value = False
        self.stop()


class DuelControls(View):
    def __init__(self):
        super().__init__(timeout=30)
        self.value = None


    @discord.ui.button(emoji="<:arma:1108453180062314656>")
    async def shoot(self, button: Button, interaction: Interaction):
        global main_interaction, player1, player2, shoot

        if not shoot and self.value != None:
            shoot = True
            self.value = "shoot"
            self.stop()

            if main_interaction.user.id == player1.id:
                return await main_interaction.followup.send(f"{player1.mention} ganhou!")

            elif main_interaction.user.id == player2.id:
                return await main_interaction.followup.send(f"{player2.mention} ganhou!")

            else: return


class Duel(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self.ctx_menu = app_commands.ContextMenu(
            name="Duelar",
            callback=self.duelar,
        )
        self.bot.tree.add_command(self.ctx_menu)


    @commands.Cog.listener()
    async def on_ready(self):
        await self.bot.tree.sync()


    async def duelar(self, interaction: Interaction, user: Member) -> None:
        if user.bot:
            return await interaction.response.send_message(
                "Não é possivel duelar contra bots.",
                ephemeral=True
            )

        global main_interaction, player1, player2, shoot

        main_interaction = interaction
        player1 = interaction.user
        player2 = user
        shoot = False

        if player1.id == player2.id:
            return await interaction.response.send_message(
                "Não é possivel duelar com você mesmo, Esquisito.",
                ephemeral=True
            )

        # await interaction.response.send_message("⠀", ephemeral=True, delete_after=0.1)

        view = DuelPrompt()
        await interaction.response.send_message(f"{user.display_name}, {interaction.user.display_name} está te desafiando para um duelo, aceita ?", view=view, delete_after=30)

        await view.wait()
        if (view.value == None): return

        elif (view.value == "accept"):
            view = DuelControls()
            await interaction.followup.send(f"> {player1.display_name} VS {player2.display_name}\n**(Mouse aqui)** Preparar...")
            await sleep(random.randint(3, 10))
            await interaction.followup.edit_message(f"> {player1.display_name} VS {player2.display_name}\n**ATIRAR!!!**", view=view)

            await view.wait()

            if (view.value == None):
                return
            else:
                return await interaction.followup.delete_message(
                    interaction.message.id
                )

        else:
            return await interaction.followup.send(f"{user.display_name} recusou o duelo.")


async def setup(client):
    await client.add_cog(Duel(client))