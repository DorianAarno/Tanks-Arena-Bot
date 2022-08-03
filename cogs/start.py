
from disnake import *
from disnake.ext.commands import *

from disnake import *

class CreatePaginator(ui.View):
    def __init__(self, embeds: list, author: int):
        super().__init__(timeout=None)
        self.embeds = embeds
        self.author = author
        self.CurrentEmbed = 0

    @ui.button(emoji="⬅️", style=ButtonStyle.grey)
    async def previous(self, button, inter):
        await inter.response.defer()
        try:
            if inter.author.id != self.author and self.author != 123:
                return await inter.send("You cannot interact with these buttons.", ephemeral=True)
            
            # If Current Embed is not 0
            if self.CurrentEmbed:
                await inter.edit_original_message(embed=self.embeds[self.CurrentEmbed-1])
                self.CurrentEmbed = self.CurrentEmbed - 1
            else:
                raise()
                
        except:
            await inter.send('Unable to change the page.', ephemeral=True)

    @ui.button(label="Confirm", style=ButtonStyle.green)
    async def confirm(self, button, inter):
        user_selected_tank = self.embeds[self.CurrentEmbed].title

        # Database integration to be done here
        await inter.send(f"You've selected **{user_selected_tank}**.")

        # Stops all the buttons in this view
        self.stop()
    
    @ui.button(emoji="➡️", style=ButtonStyle.grey)
    async def next(self, button, inter):
        await inter.response.defer()
        try:
            if inter.author.id != self.author and self.author != 123:
                return await inter.send("You cannot interact with these buttons.", ephemeral=True)

            await inter.edit_original_message(embed=self.embeds[self.CurrentEmbed+1])
            self.CurrentEmbed += 1
            
        except:
            await inter.send('Unable to change the page.', ephemeral=True)

class Starter(Cog):
    def __init__(self, bot):
        self.bot = bot

    @slash_command()
    async def start(self, ctx):
        await ctx.response.defer()

        atk_tank = Embed(title="Attack Tank", description="Gives you advantage over **Attacks**.", color=Color.blurple())
        # I didn't use File as during pagination it was causing I/O based error
        atk_tank.set_thumbnail(url="https://media.discordapp.net/attachments/1003927928519802955/1004276059363102830/tank_atk.gif")

        hp_tank = Embed(title="HP Tank", description="Gives you advantage over **HP**.", color=Color.blurple())
        # I didn't use File as during pagination it was causing I/O based error
        hp_tank.set_thumbnail(url="https://media.discordapp.net/attachments/1003927928519802955/1004276059845431366/tank_hp.gif")

        embeds = [atk_tank, hp_tank]
        await ctx.send(embed=embeds[0], view=CreatePaginator(embeds, ctx.author.id))

def setup(bot):
    bot.add_cog(Starter(bot))