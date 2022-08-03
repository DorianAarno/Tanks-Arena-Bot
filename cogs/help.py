from disnake import *
from disnake.ext.commands import *

class HelpButton(ui.Button):
    def __init__(self, bot, ctx, label, embed):
        self.bot = bot
        self.ctx = ctx
        self.embed = embed
        super().__init__(
            style=ButtonStyle.gray,
            label = label
            )
    async def callback(self, inter: MessageInteraction):
        await inter.response.defer()
        await inter.edit_original_message(embed=self.embed)

class HelpView(ui.View):
    def __init__(self, bot, ctx, labels, embeds):
        super().__init__(timeout=300.0)
        for i, label in enumerate(labels):
            self.add_item(HelpButton(bot, ctx, label, embeds[i]))

class Help(Cog):
    def __init__(self, bot):
        self.bot = bot

    async def help(self, ctx):
        main = Embed(title="📔 Help Menu", description=f"• All commands are slash commands.\n• Detailed description of every command can be found while executing it.", color=Color.blurple())
        # main.set_footer(icon_url=self.bot.user.avatar.url, text="Tank Arena")
        embeds = [
            main
        ]
        labels = ['🏠 Home']
        for command in self.bot.slash_commands:
            if command.cog.qualified_name in ["Help"]:
                continue
            description = command.body.description
            if not description or description == None or description == "":
                description = "No description provided."
            if command.cog.description not in [x.title for x in embeds]:
                e = Embed(title=command.cog.description, description="", color=Color.blurple())
                # e.set_footer(icon_url=self.bot.user.avatar.url, text="Tank Arena")
                embeds.append(e)
                labels.append(command.cog.description)
            for embed in embeds:
                if embed.title == command.cog.description:
                    embed.description += f"`/{command.qualified_name}`\n"
        await ctx.send(embed=embeds[0], view=HelpView(self.bot, ctx, labels, embeds))
    
    @slash_command(name="help", description="See all available features.")
    async def help_slash(self, ctx):
        await self.help(ctx)
    
def setup(bot):
    bot.add_cog(Help(bot))