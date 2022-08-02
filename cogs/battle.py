
from disnake import *
from disnake.ext.commands import *
from PIL import Image
from io import BytesIO

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
        
        await ctx.response.defer()

        # Opening and preparing all the assets
        background = Image.open('assets/background.png')
        tank_left = Image.open('assets/tank.png')
        tank_right = Image.open('assets/tank_right.png')
        print(f"Background Dimenstions: {background.width, background.height}")
        # It'll be good if our tank dimensions are same
        print(f"Tank Dimenstions: {tank_left.width, tank_left.height}")

        background.paste(tank_right, (background.width - tank_right.width, background.height - tank_right.width)) 
        # We subtracted width to make sure the tank does not go out of the background
        background.paste(tank_left, (0, background.height - tank_left.width))

        background_bytes = BytesIO()
        background.save(background_bytes, "PNG")
        background_bytes.seek(0)

        await ctx.send(file=File(filename="bg.png", fp=background_bytes))



def setup(bot):
    bot.add_cog(Battle(bot))