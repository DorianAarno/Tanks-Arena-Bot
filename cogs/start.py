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
        serial = self.tank_data[tank_type]["SERIAL"]

        tank_stats = self.bot.determine_stats(
            tank_stats_range, self.tank_data[tank_type]["ADVANTAGE"]
        )
        hp = tank_stats[0]
        attack = tank_stats[1]
        defence = tank_stats[2]

        hp_max = tank_stats_range["HP"]["max"]
        atk_max = tank_stats_range["ATTACK"]["max"]
        def_max = tank_stats_range["DEFENCE"]["max"]

        await self.bot.execute(
            "INSERT INTO user_tanks(user_id, tank_type, serial, hp, atk, def) VALUES($1, $2, $3, $4, $5, $6)",
            inter.author.id,
            tank_type,
            serial,
            hp,
            attack,
            defence,
        )
        await self.bot.execute(
            "INSERT OR IGNORE INTO users(user_id, money) VALUES($1, $2)",
            inter.author.id,
            0,
        )

        tank_quality = self.bot.get_TQ(tank_stats_range, hp, defence, attack)

        await inter.send(
            f"You've successfully selected **{user_selected_tank}**. \n\n**HP:** {hp}  TQ: ({hp}/{hp_max})\n**Attack:** {attack}  TQ: ({attack}/{atk_max})\n**Defence:** {defence}  TQ: ({defence}/{def_max})\n**Total TQ:** {tank_quality:,.2f}%"
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

    @slash_command()
    async def tanks(self, ctx: CommandInteraction):
        """
        Parent Command
        """
        pass

    @tanks.sub_command()
    async def show(self, ctx: CommandInteraction):
        """
        Show your tanks
        """
        with open("assets/tanks.json") as f:
            tank_data = json.load(f)

        data = await self.bot.fetch(
            "SELECT * FROM user_tanks WHERE user_id = $1", ctx.author.id
        )
        if len(data) < 1:
            embed = Embed(
                title="You dont have any tanks! Choose one now from `/start`",
                color=Color.red(),
            )
            return await ctx.send(embed=embed)

        embed = Embed(description="Your Tanks~\n\n", color=Color(0x2E3135))
        if ctx.author.avatar:
            embed.set_author(name=ctx.author.name, icon_url=ctx.author.avatar.url)
        else:
            embed.set_author(name=ctx.author.name)
        for n, tank in enumerate(data):
            id, tank_type, hp, attack, defence = tank
            tank_stats_range = tank_data[tank_type]["STATS"]
            tank_quality = self.bot.get_TQ(tank_stats_range, hp, attack, defence)
            embed.description += f"**{n+1}.** {tank_type} Tank | {tank_quality}%\n"
        await ctx.send(embed=embed)

    @tanks.sub_command()
    async def info(self, ctx: CommandInteraction, serial: str):
        with open("assets/tanks.json") as f:
            tank_data = json.load(f)

        serial = serial.upper()
        data = await self.bot.fetchrow(
            "SELECT * FROM user_tanks WHERE user_id = $1 AND tank_type = $2",
            ctx.author.id,
            serial,
        )
        if len(data) < 1:
            embed = Embed(
                title="You dont have that tank! Use `/tank show` to view your tanks.",
                color=Color.red(),
            )
            return await ctx.send(embed=embed)

        id, tank_type, hp, attack, defence = data

        embed = Embed(title=f"{tank_type} Tank", color=Color(0x2E3135))
        if ctx.author.avatar:
            embed.set_author(name=ctx.author.name, icon_url=ctx.author.avatar.url)
        else:
            embed.set_author(name=ctx.author.name)

        tank_stats_range = tank_data[tank_type]["STATS"]
        tank_quality = self.bot.get_TQ(tank_stats_range, hp, attack, defence)

        hp_max = tank_data[tank_type]["STATS"]["HP"]["max"]
        atk_max = tank_data[tank_type]["STATS"]["ATTACK"]["max"]
        def_max = tank_data[tank_type]["STATS"]["DEFENCE"]["max"]

        embed.set_thumbnail(url=tank_data[tank_type]["GIF"])

        embed.description = f"Stats - \n**HP:** {hp}  TQ: ({hp}/{hp_max})\n **Attack:** {attack}  TQ: ({attack}/{atk_max})**Defence:** {defence}  TQ: ({defence}/{def_max})\n\n **Total TQ:** {tank_quality:,.2f}%"
        await ctx.send(embed=embed)

    @tanks.sub_command()
    async def market(self, ctx: CommandInteraction):
        """
        Open up Tank Market
        """
        with open("assets/tanks.json") as f:
            tank_data = json.load(f)

        embed = Embed(title=f"Tanks", color=Color.dark_green())
        for tank_name in tank_data:
            tank = tank_data[tank_name]
            embed.add_field(
                name="\u200b",
                value=f"🔹**{tank_name} Tank** \n>>> Advantage: **`{tank['ADVANTAGE']}`** \n**Cost: `{tank['COST']}`**",
                inline=False,
            )

        await ctx.response.send_message(embed=embed)

    @tanks.sub_command()
    async def buy(self, ctx: CommandInteraction, serial: str):
        """
        Buy a tank from market
        """
        with open("assets/tanks.json") as f:
            tank_data = json.load(f)

        serial = serial.upper()
        tank_type = None
        for tank in tank_data:
            if tank == serial:
                tank_type = tank

        if tank_type is None:
            embed = Embed(
                title="Uh oh.. No tank of this serial exist.", color=Color.red()
            )
            return await ctx.send(embed=embed)

        money = await self.bot.fetchval(
            "SELECT money FROM users WHERE user_id = $1", ctx.author.id
        )
        if money is None:
            embed = Embed(
                title="Please choose a tank from `/start` and play a match to continue!",
                color=Color.red(),
            )
            return await ctx.send(embed=embed)

        cost = tank_data[tank_type]["COST"]
        if money < cost:
            embed = Embed(
                title="You dont have enough money to buy this tank", color=Color.red()
            )
            return await ctx.send(embed=embed)

        tank_stats_range = tank_data[tank_type]["STATS"]

        tank_stats = self.bot.determine_stats(
            tank_stats_range, tank_data[tank_type]["ADVANTAGE"]
        )
        hp = tank_stats[0]
        attack = tank_stats[1]
        defence = tank_stats[2]

        hp_max = tank_stats_range["HP"]["max"]
        atk_max = tank_stats_range["ATTACK"]["max"]
        def_max = tank_stats_range["DEFENCE"]["max"]

        await self.bot.execute(
            "INSERT INTO user_tanks(user_id, tank_type, serial, hp, atk, def) VALUES($1, $2, $3, $4, $5, $6)",
            ctx.author.id,
            tank_type,
            serial,
            hp,
            attack,
            defence,
        )
        await self.bot.execute(
            "UPDATE users SET money = money - $1 WHERE user_id = $2",
            cost,
            ctx.author.id,
        )

        tank_quality = self.bot.get_TQ(tank_stats_range, hp, defence, attack)
        embed = Embed(
            description=f"You've successfully bought **{tank_type}** Tank. \n\n**HP:** {hp}  TQ: ({hp}/{hp_max})\n**Attack:** {attack}  TQ: ({attack}/{atk_max})\n**Defence:** {defence}  TQ: ({defence}/{def_max})\n**Total TQ:** {tank_quality:,.2f}%",
            color=Color(0x2E3135),
        )
        await ctx.send(embed=embed)
        
    @tanks.sub_command()
    async def remove(self, ctx: CommandInteraction, serial: str):
        """
        Remove a tank from your inventory
        """
        serial = serial.upper()
        data = await self.bot.fetchrow(
            "SELECT * FROM user_tanks WHERE user_id = $1 AND tank_type = $2",
            ctx.author.id,
            serial,
        )
        if data:
            await self.bot.execute(
                "DELETE FROM user_tanks WHERE user_id = $1 AND tank_type = $2",
                ctx.author.id, serial
            )
            content = "Tank have been removed succesfully!"
        else:
            content = "uh oh.. You dont own that tank"
        
        embed = Embed(
                title=content, color=Color.red()
            )
        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(Starter(bot))
