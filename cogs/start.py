import json
from random import randint

from disnake import *
from disnake.ext.commands import *


class CreatePaginator(ui.View):
    def __init__(self, bot, embeds: list, author: int, tank_data: dict):
        super().__init__(timeout=None)
        self.bot = bot
        self.embeds = embeds
        self.author = author
        self.tank_data = tank_data
        self.CurrentEmbed = 0

    @ui.button(emoji="⬅️", style=ButtonStyle.grey)
    async def previous(self, button, inter):
        await inter.response.defer()
        try:
            if inter.author.id != self.author and self.author != 123:
                return await inter.send(
                    "You cannot interact with these buttons.", ephemeral=True
                )

            # If Current Embed is not 0
            if self.CurrentEmbed:
                await inter.edit_original_message(
                    embed=self.embeds[self.CurrentEmbed - 1]
                )
                self.CurrentEmbed = self.CurrentEmbed - 1
            else:
                raise ()

        except:
            await inter.send("Unable to change the page.", ephemeral=True)

    @ui.button(label="Confirm", style=ButtonStyle.green)
    async def confirm(self, button, inter):
        user_selected_tank = self.embeds[self.CurrentEmbed].title
        tank_type = user_selected_tank.replace(" Tank", "")

        # Database integration
        tank_stats_range = self.tank_data[tank_type]["STATS"]
        hp = randint(tank_stats_range["HP"]["min"], tank_stats_range["HP"]["max"])
        attack = randint(
            tank_stats_range["ATTACK"]["min"], tank_stats_range["ATTACK"]["max"]
        )
        defence = randint(
            tank_stats_range["DEFENCE"]["min"], tank_stats_range["DEFENCE"]["max"]
        )

        await self.bot.execute(
            "INSERT INTO user_tanks(user_id, tank_type, hp, atk, def) VALUES($1, $2, $3, $4, $5)",
            inter.author.id,
            tank_type,
            hp,
            attack,
            defence,
        )

        tank_quality = (
            (hp + defence + attack)
            / (
                tank_stats_range["HP"]["max"]
                + tank_stats_range["ATTACK"]["max"]
                + tank_stats_range["DEFENCE"]["max"]
            )
        ) * 100

        await inter.send(
            f"You've successfully selected **{user_selected_tank}**. \n\n**HP:** {hp} \n**Attack:** {attack} \n**Defence:** {defence}\n**TQ:** {tank_quality:,.2f}%"
        )

        # Stops all the buttons in this view
        self.stop()

    @ui.button(emoji="➡️", style=ButtonStyle.grey)
    async def next(self, button, inter):
        await inter.response.defer()
        try:
            if inter.author.id != self.author and self.author != 123:
                return await inter.send(
                    "You cannot interact with these buttons.", ephemeral=True
                )

            await inter.edit_original_message(embed=self.embeds[self.CurrentEmbed + 1])
            self.CurrentEmbed += 1

        except:
            await inter.send("Unable to change the page.", ephemeral=True)


class Starter(Cog):
    """
        ⏳ Start
    """

    def __init__(self, bot):
        self.bot = bot

    @slash_command(name="start", description="start")
    async def start(self, ctx):
        await ctx.response.defer()

        # General data about tanks will be present in this json
        with open("assets/tanks.json") as f:
            tank_data = json.load(f)

        data = await self.bot.fetchrow(
            "SELECT * FROM user_tanks WHERE user_id = $1", ctx.author.id
        )
        if data:
            embed = Embed(title="You've already selected a starter!", color=Color.red())
            embed.set_thumbnail(url=tank_data[data[1]]["GIF"])

            return await ctx.send(embed=embed)

        atk_tank = Embed(
            title="KNISPEL Tank",
            description="Gives you advantage over **Attacks**.",
            color=Color.blurple(),
        )
        # I didn't use File as during pagination it was causing I/O based error
        atk_tank.set_thumbnail(url=tank_data["KNISPEL"]["GIF"])

        hp_tank = Embed(
            title="ABRAMS Tank",
            description="Gives you advantage over **HP**.",
            color=Color.blurple(),
        )
        # I didn't use File as during pagination it was causing I/O based error
        hp_tank.set_thumbnail(url=tank_data["ABRAMS"]["GIF"])

        embeds = [atk_tank, hp_tank]
        await ctx.send(
            embed=embeds[0],
            view=CreatePaginator(self.bot, embeds, ctx.author.id, tank_data),
        )


def setup(bot):
    bot.add_cog(Starter(bot))
