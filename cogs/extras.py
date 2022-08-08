from disnake.ext.commands import Cog, slash_command


class Extras(Cog):
    """
        🔗 Extras
    """

    def __init__(self, bot):
        self.bot = bot

    @slash_command(name="ping", description="Check the latency of the bot.")
    async def ping(self, ctx):
        await ctx.send(f"📶 {round(self.bot.latency * 1000)}ms")


def setup(bot):
    bot.add_cog(Extras(bot))
