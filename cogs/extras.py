from disnake.ext.commands import Cog, slash_command
from disnake import Embed, Color

class Extras(Cog):
    """
        🔗 Extras
    """

    def __init__(self, bot):
        self.bot = bot

    @slash_command(name="ping", description="Check the latency of the bot.")
    async def ping(self, ctx):
        await ctx.send(f"📶 {round(self.bot.latency * 1000)}ms")

    @slash_command(description="Invite the bot to other servers.")
    async def invite(self, ctx):
        embed = Embed(
            title="Bot Links",
            description="[Invite me](https://discord.com/oauth2/authorize?client_id=1003954779346718720&permissions=2147863616&scope=bot%20applications.commands) \n[Support Server](https://discord.gg/D7C4jEkz)",
            color=Color.blurple()
        )
        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(Extras(bot))
