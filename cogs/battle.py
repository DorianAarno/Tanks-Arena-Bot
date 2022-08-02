from disnake import *
from disnake.ext.commands import *
from PIL import Image

class Battle(Cog):
    def __init__(self, bot):
        self.bot = bot

    @slash_command()
    async def battle(self, ctx, opponent: Member):
        """
        Parameters
        ----------
        opponent: User to battle.
        """

        # Opening and preparing all the assets
        background = Image.open('assets/background.png')
        tank_left = Image.open('assets/tank.png')
        tank_right = Image.open('assets/tank.png')

        background.paste(tank_left, (0,0))
        background.paste(tank_right, (background.width,0))
        background.show()



def setup(bot):
    bot.add_cog(Battle(bot))