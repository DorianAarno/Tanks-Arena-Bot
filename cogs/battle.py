from disnake import *
from disnake.ext.commands import *

class Battle(Cog):
    def __init__(self, bot):
        self.bot = bot

    

def setup(bot):
    bot.add_cog(Battle(bot))