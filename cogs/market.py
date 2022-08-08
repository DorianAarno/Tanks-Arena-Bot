from disnake import *
from disnake.ext.commands import *


class Market(Cog):
    """
        🛒 MarketPlace (Coming Soon)
    """

    def __init__(self, bot):
        self.bot = bot

    @slash_command(description="Buy new tanks from the marketplace!")
    async def market(self, ctx: CommandInteraction):
        await ctx.send("Coming Soon!")

    # @tanks.sub_command()
    # async def market(self, ctx: CommandInteraction):
    #     """
    #     Open up Tank Market
    #     """
    #     with open("assets/tanks.json") as f:
    #         tank_data = json.load(f)

    #     embed = Embed(title=f"Tanks", color=Color.dark_green())
    #     for tank_name in tank_data:
    #         tank = tank_data[tank_name]
    #         embed.add_field(
    #             name="\u200b",
    #             value=f"🔹**{tank_name} Tank** \n>>> Advantage: **`{tank['ADVANTAGE']}`** \n**Cost: `{tank['COST']}`**",
    #             inline=False,
    #         )

    #     await ctx.response.send_message(embed=embed)

    # @tanks.sub_command()
    # async def buy(self, ctx: CommandInteraction, serial: str):
    #     """
    #     Buy a tank from market
    #     """
    #     with open("assets/tanks.json") as f:
    #         tank_data = json.load(f)

    #     serial = serial.upper()
    #     tank_type = None
    #     for tank in tank_data:
    #         if tank == serial:
    #             tank_type = tank

    #     if tank_type is None:
    #         embed = Embed(
    #             title="Uh oh.. No tank of this serial exist.", color=Color.red()
    #         )
    #         return await ctx.send(embed=embed)

    #     money = await self.bot.fetchval(
    #         "SELECT money FROM users WHERE user_id = $1", ctx.author.id
    #     )
    #     if money is None:
    #         embed = Embed(
    #             title="Please choose a tank from `/start` and play a match to continue!",
    #             color=Color.red(),
    #         )
    #         return await ctx.send(embed=embed)

    #     cost = tank_data[tank_type]["COST"]
    #     if money < cost:
    #         embed = Embed(
    #             title="You dont have enough money to buy this tank", color=Color.red()
    #         )
    #         return await ctx.send(embed=embed)

    #     tank_stats_range = tank_data[tank_type]["STATS"]

    #     tank_stats = self.bot.determine_stats(
    #         tank_stats_range, tank_data[tank_type]["ADVANTAGE"]
    #     )
    #     hp = tank_stats[0]
    #     attack = tank_stats[1]
    #     defence = tank_stats[2]

    #     hp_max = tank_stats_range["HP"]["max"]
    #     atk_max = tank_stats_range["ATTACK"]["max"]
    #     def_max = tank_stats_range["DEFENCE"]["max"]

    #     await self.bot.execute(
    #         "INSERT INTO user_tanks(user_id, name, serial, hp, atk, def) VALUES($1, $2, $3, $4, $5, $6)",
    #         ctx.author.id,
    #         tank_type,
    #         serial,
    #         hp,
    #         attack,
    #         defence,
    #     )
    #     await self.bot.execute(
    #         "UPDATE users SET money = money - $1 WHERE user_id = $2",
    #         cost,
    #         ctx.author.id,
    #     )

    #     tank_quality = self.bot.get_TQ(tank_stats_range, hp, defence, attack)
    #     embed = Embed(
    #         description=f"You've successfully bought **{tank_type}** Tank. \n\n**HP:** {hp}  TQ: ({hp}/{hp_max})\n**Attack:** {attack}  TQ: ({attack}/{atk_max})\n**Defence:** {defence}  TQ: ({defence}/{def_max})\n**Total TQ:** {tank_quality:,.2f}%",
    #         color=Color(0x2E3135),
    #     )
    #     await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(Market(bot))
