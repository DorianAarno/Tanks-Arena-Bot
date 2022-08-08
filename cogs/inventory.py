
from disnake import *
from disnake.ext.commands import *

class Inventory(Cog):
    """
        📥 Inventory
    """
    def __init__(self, bot):
        self.bot = bot

    @slash_command()
    async def inventory(self, ctx: CommandInteraction):
        """
        See all your tanks!
        """

        data = await self.bot.fetch(
            "SELECT * FROM user_tanks WHERE user_id = $1", ctx.author.id
        )
        if len(data) < 1:
            embed = Embed(
                title="You do not have any tanks! Choose one now from `/start`",
                color=Color.red(),
            )
            return await ctx.send(embed=embed)

        embed = Embed(description="", color=Color.blurple())
        if ctx.author.avatar:
            embed.set_author(name=ctx.author.name, icon_url=ctx.author.avatar.url)
        else:
            embed.set_author(name=ctx.author.name)
        for n, tank in enumerate(data):
            id, name, hp, attack, defence, serial = tank
            tank_stats_range = self.bot.get_tank_details(name)['STATS']
            tank_quality = self.bot.get_TQ(tank_stats_range, hp, attack, defence)
            embed.description += f"**{n+1}.** {name} Tank | {tank_quality}%\n"
        
        # TODO: This will need pagination later on
        await ctx.send(embed=embed)
    

def setup(bot):
    bot.add_cog(Inventory(bot))