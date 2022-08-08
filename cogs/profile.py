from disnake import Color, CommandInteraction, Embed
from disnake.ext.commands import Cog, slash_command


class Profile(Cog):
    """
        👤 Profile
    """

    def __init__(self, bot):
        self.bot = bot

    @slash_command()
    async def tanks(self, ctx: CommandInteraction):
        """
        Parent Command
        """
        pass

    @tanks.sub_command()
    async def info(self, ctx: CommandInteraction, serial: int):
        """
        See details about one of your tanks!
        
        Parameters
        ----------
        serial: Enter the serial of the tank based on /inventory
        """

        data = await self.bot.fetchrow(
            "SELECT * FROM user_tanks WHERE user_id = $1 and serial = $2",
            ctx.author.id,
            serial,
        )
        if not data:
            embed = Embed(
                title="You dont have that tank! Use `/inventory` to view your tanks.",
                color=Color.red(),
            )
            return await ctx.send(embed=embed)

        id, name, hp, attack, defence, serial = data

        embed = Embed(title=f"{name} Tank", color=Color.blurple())
        if ctx.author.avatar:
            embed.set_author(name=ctx.author.name, icon_url=ctx.author.avatar.url)
        else:
            embed.set_author(name=ctx.author.name)

        tank_data = self.bot.get_tank_details(name)

        tank_quality = self.bot.get_TQ(tank_data["STATS"], hp, attack, defence)

        hp_max = tank_data["STATS"]["HP"]["max"]
        atk_max = tank_data["STATS"]["ATTACK"]["max"]
        def_max = tank_data["STATS"]["DEFENCE"]["max"]

        embed.set_thumbnail(url=tank_data["GIF"])

        embed.description = f"**HP:** {hp}  TQ: ({hp}/{hp_max}) \n**Attack:** {attack}  TQ: ({attack}/{atk_max}) \n**Defence:** {defence}  TQ: ({defence}/{def_max})\n\n **Total TQ:** {tank_quality}%"
        await ctx.send(embed=embed)

    @tanks.sub_command()
    async def dispose(self, ctx: CommandInteraction, serial: int):
        """
        Dispose a tank from your inventory.
        
        Parameters
        ----------
        serial: Enter the serial of the tank based on /inventory
        """
        # Making sure it's not user's last tank
        data = await self.bot.fetch(
            "SELECT * FROM user_tanks WHERE user_id = $1", ctx.author.id,
        )
        if len(data) == 1:
            return await ctx.send("You cannot dispose your last tank.")

        # Moving ahead with dispose command
        data = await self.bot.fetchrow(
            "SELECT * FROM user_tanks WHERE user_id = $1 and serial = $2",
            ctx.author.id,
            serial,
        )

        embed = Embed(title="You do not own a tank of that serial.", color=Color.red())

        if not data:
            return await ctx.send(embed=embed)

        id, name, hp, attack, defence, serial = data
        await self.bot.execute(
            "DELETE FROM user_tanks WHERE user_id = $1 and serial = $2",
            ctx.author.id,
            serial,
        )
        embed.title = f"{name} Tank has been removed succesfully!"
        embed.color = Color.green()
        embed.set_thumbnail(url=self.bot.get_tank_details(name)["GIF"])

        await ctx.send(embed=embed)

    @tanks.sub_command()
    async def set(self, ctx: CommandInteraction, serial: int):
        """
        Set a tank as default for your battles!
        
        Parameters
        ----------
        serial: Enter the serial of the tank based on /inventory
        """

        data = await self.bot.fetchrow(
            "SELECT * FROM user_tanks WHERE user_id = $1 AND serial = $2",
            ctx.author.id,
            serial,
        )

        embed = Embed(title="You do not own a tank of that serial", color=Color.red())

        if not data:
            return await ctx.send(embed=embed)

        serial = data[5]

        await self.bot.execute(
            "UPDATE users SET battle_tank = $1 WHERE user_id = $2",
            serial,
            ctx.author.id,
        )
        embed.title = f"{data[1]} Tank is ready for battle!"
        embed.color = Color.green()
        embed.set_thumbnail(url=self.bot.get_tank_details(data[1])["GIF"])

        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(Profile(bot))
