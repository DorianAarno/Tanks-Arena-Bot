
from disnake import *
from disnake.ext.commands import *


class CreatePaginator(ui.View):
    def __init__(self, bot, embeds: list, author: int,):
        super().__init__(timeout=None)
        self.bot = bot
        self.embeds = embeds
        self.author = author
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
        name = user_selected_tank.replace(" Tank", "")

        # Database integration
        tank_stats_range = self.bot.get_tank_details(name)["STATS"]

        tank_stats = self.bot.determine_stats(
            tank_stats_range,  self.bot.get_tank_details(name)["ADVANTAGE"]
        )
        hp = tank_stats[0]
        attack = tank_stats[1]
        defence = tank_stats[2]

        hp_max = tank_stats_range["HP"]["max"]
        atk_max = tank_stats_range["ATTACK"]["max"]
        def_max = tank_stats_range["DEFENCE"]["max"]

        await self.bot.execute(
            "INSERT INTO user_tanks(user_id, name, hp, atk, def, serial) VALUES($1, $2, $3, $4, $5, $6)",
            inter.author.id,
            name,
            hp,
            attack,
            defence,
            1,
        )
        await self.bot.execute(
            "INSERT OR IGNORE INTO users(user_id, money, battle_tank) VALUES($1, $2, $3)",
            inter.author.id,
            0,
            1
        )

        tank_quality = self.bot.get_TQ(tank_stats_range, hp, defence, attack)

        await inter.send(
            f"You've successfully selected **{user_selected_tank}**. \n\n**HP:** {hp}  TQ: ({hp}/{hp_max})\n**Attack:** {attack}  TQ: ({attack}/{atk_max})\n**Defence:** {defence}  TQ: ({defence}/{def_max})\n**Total TQ:** {tank_quality}%"
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

    @slash_command(name="start", description="Start your tank arena journey!")
    async def start(self, ctx: CommandInteraction):
        await ctx.response.defer()

        data = await self.bot.fetchrow(
            "SELECT * FROM user_tanks WHERE user_id = $1", ctx.author.id
        )
        if data:
            id, name, hp, attack, defence, serial = data
            embed = Embed(title="You've already selected a starter!", color=Color.red())
            embed.set_thumbnail(url=self.bot.get_tank_details(name)["GIF"])

            return await ctx.send(embed=embed)

        atk_tank = Embed(
            title="KNISPEL Tank",
            description="Gives you advantage over **Attacks**.",
            color=Color.blurple(),
        )

        atk_tank.set_thumbnail(url=self.bot.get_tank_details("KNISPEL")["GIF"])

        hp_tank = Embed(
            title="ABRAMS Tank",
            description="Gives you advantage over **HP**.",
            color=Color.blurple(),
        )

        hp_tank.set_thumbnail(url=self.bot.get_tank_details("ABRAMS")["GIF"])

        embeds = [atk_tank, hp_tank]
        await ctx.send(
            embed=embeds[0],
            view=CreatePaginator(self.bot, embeds, ctx.author.id,),
        )

def setup(bot):
    bot.add_cog(Starter(bot))
