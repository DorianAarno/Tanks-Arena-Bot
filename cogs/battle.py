from io import BytesIO
from random import randint

from disnake import *
from disnake.ext.commands import *
from PIL import Image, ImageDraw


def give_tank_image(path, name, total_health, current_health=None):
    if current_health is None:
        current_health = total_health
    
    tank =  Image.open(path)
    tank = tank.resize((50, 50))

    x_cord = 0
    y_cord = 0
    height = 5
    width = tank.size[1] - x_cord

    # gives the health ratio
    health_ratio = width / total_health 
    # gives the bar width
    bar_width = health_ratio * current_health
    
    # Green
    bar_color = (176, 255, 120)
    # White
    bg_color = (255, 255, 255)
    
    # We create a new transparent image
    im = Image.new("RGBA", (tank.size[0], tank.size[1] + 10), (255, 255, 255, 0))
    
    # We draw the hp bar on fix place
    draw = ImageDraw.Draw(im)
    
    # make first background circle
    draw.ellipse((x_cord, y_cord, x_cord+height, y_cord+height), fill=bg_color)
    # make the last brackground circla
    draw.ellipse((x_cord+width, y_cord, x_cord+width+height, y_cord+height), fill=bg_color)
    # fill the middle portion
    draw.rectangle((x_cord+(height/2), y_cord, x_cord+width+(height/2), y_cord+height), fill=bg_color)

    if bar_width > 0:
        # set to actual health ratio
        width = bar_width - 1
        # Same stuff as above
        draw.ellipse((x_cord, y_cord, x_cord+height, y_cord+height), fill=bar_color)
        draw.ellipse((x_cord+width, y_cord, x_cord+width+height, y_cord+height), fill=bar_color)
        draw.rectangle((x_cord+(height/2), y_cord, x_cord+width+(height/2), y_cord+height), fill=bar_color)

    # Set the x cord for tank 
    tank_x_cord = x_cord # its same as exp bar for aesthetic looks

    # Some padding between bar and tank
    padding = im.size[1] - (height + tank.size[1]) 
    height += padding
    
    # finally paste the tank
    im.paste(tank, (tank_x_cord, height + tank_x_cord, tank.size[0] + tank_x_cord , height + (tank.size[0] + tank_x_cord)))

    return im

def set_power(user_input, bg_dimensions):
    return user_input

class PowerModal(ui.Modal):
    def __init__(self) -> None:
        components = [
            ui.TextInput(
                label="Rate",
                placeholder="Input an integer between 1-100",
                max_length=3,
                style=TextInputStyle.short,
                custom_id="rate"
            )
        ]

        super().__init__(title="Set Power", custom_id="power", components=components)

    async def callback(self, inter: ModalInteraction):
        background = Image.open("assets/background.png")
        bg_width = background.width
        for custom_id, value in inter.text_values.items():
            if custom_id == "rate":
                if int(value) <= 100 and int(value) >= 1:
                    await inter.send(set_power(int(value), bg_width))
                else:
                    await inter.send("Power needs to be between 1-100", ephemeral=True)


class Button(ui.Button):
    def __init__(self, bot, label):
        super().__init__(style=ButtonStyle.blurple, label=label)
        self.bot = bot
    
    async def callback(self, inter: MessageInteraction):
        await inter.response.send_modal(PowerModal())

class ButtonView(ui.View):
    def __init__(self, bot):
        super().__init__()
        self.bot = bot
        self.add_item(Button(bot, 'Power'))
        self.add_item(Button(bot, 'Attack'))

class Battle(Cog):
    def __init__(self, bot):
        self.bot = bot

    @slash_command()
    async def battle(self, ctx, opponent: Member):
        """
        Parameters
        ----------
        opponent: User to battle.
        """

        await ctx.response.defer()

        # Opening and preparing all the assets
        background = Image.open("assets/background.png")

        # made a function to give tank images
        tank_left = give_tank_image("assets/tank.png", {ctx.author.name}, 100)
        tank_right = give_tank_image("assets/tank_right.png", "Bot", 100)

        print(f"Background Dimenstions: {background.width, background.height}")
        # It'll be good if our tank dimensions are same
        print(f"Tank Dimenstions: {tank_left.width, tank_left.height}")

        background.paste(
            tank_right,
            (background.width - tank_right.width, background.height - tank_right.width),
        )
        # We subtracted width to make sure the tank does not go out of the background
        background.paste(tank_left, (0, background.height - tank_left.width))

        background_bytes = BytesIO()
        background.save(background_bytes, "PNG")
        background_bytes.seek(0)

        await ctx.send(file=File(filename="bg.png", fp=background_bytes), view=ButtonView(self.bot))


def setup(bot):
    bot.add_cog(Battle(bot))
