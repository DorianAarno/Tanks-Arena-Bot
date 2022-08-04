from turtle import distance
import numpy as np
import random
from io import BytesIO
from random import randint
from matplotlib import pyplot as plt

from disnake import *
from disnake.ext.commands import *
from PIL import Image, ImageDraw


G = 9.8

ONGOING_BATTLES = {}
GROUND_LEVEL = 825

def compute_distance(power, angle):
    theta = angle * np.pi/180
    x0 = 0
    v0 = power

    t = 2 * v0 * np.sin(theta) / G    
    xt = x0 + (v0*t*np.cos(theta))

    distance = round((xt - x0) *  2.942)
    if distance > 3000:
        distance = 3000

    return distance

def prepare_attack_image(bg_img, cords, tank_size, distance):
    explosion_lst = ["explosion.png", "explosion2.png", "explosion3.png"]
    
    nozzle = Image.open("assets/nozzle.png")
    nozzle = nozzle.resize((120, 120))
    nozzle = nozzle.transpose(Image.FLIP_LEFT_RIGHT)

    explosion = Image.open(f"assets/{random.choice(explosion_lst)}")
    explosion = explosion.resize((150, 150))
    
    nozzle_x = cords[0] + tank_size[0]
    nozzle_y = int(cords[1] + 10)
    
    explosion_x = int(cords[0] + (distance - 10))
    explosion_y = GROUND_LEVEL - explosion.size[1]
    
    bg_img.paste(nozzle, (nozzle_x, nozzle_y), mask=nozzle)
    bg_img.paste(explosion, (explosion_x, explosion_y), mask=explosion)    

    return bg_img
    

def give_tank_image(path, total_health, current_health=None):
    if current_health is None:
        current_health = total_health
    
    tank =  Image.open(path)
    tank = tank.resize((140, 120))

    x_cord = 0
    y_cord = 0
    height = 5
    width = tank.size[1] - x_cord
    padding = 5 # padding between tank and bar and name

    # gives the health ratio
    health_ratio = width / total_health 
    # gives the bar width
    bar_width = health_ratio * current_health
    
    # Bright Red
    bar_color = (255, 0, 0)
    # White
    bg_color = (255, 255, 255)
    

    im = Image.new("RGBA", (tank.size[0] + 2, tank.size[1] + height + padding), (255, 255, 255, 0))
    draw = ImageDraw.Draw(im)
    
    height += padding
    # make the bar circle at start
    draw.ellipse((x_cord, y_cord, x_cord+height, y_cord+height), fill=bg_color)
    # make the bar circle at the end
    draw.ellipse((x_cord+width, y_cord, x_cord+width+height, y_cord+height), fill=bg_color)
    # fill the middle portion
    draw.rectangle((x_cord+(height/2), y_cord, x_cord+width+(height/2), y_cord+height), fill=bg_color)

    if bar_width > 0:
        width = bar_width
        draw.ellipse((x_cord, y_cord, x_cord+height, y_cord+height), fill=bar_color)
        draw.ellipse((x_cord+width, y_cord, x_cord+width+height, y_cord+height), fill=bar_color)
        draw.rectangle((x_cord+(height/2), y_cord, x_cord+width+(height/2), y_cord+height), fill=bar_color)
 
    tank_x_cord = x_cord # its same as exp bar for aesthetic looks
    height += padding

    im.paste(tank, (tank_x_cord, height + tank_x_cord, tank.size[0] + tank_x_cord , height + (tank.size[1] + tank_x_cord)), mask=tank)

    return im

def set_power(bg_dimensions, power, angle):
    distance = compute_distance(power, angle)
    return f"Power : {power} \nAngle : {angle} \nDistance Covered : {distance}"

class PowerModal(ui.Modal):
    def __init__(self) -> None:
        components = [
            ui.TextInput(
                label="Rate",
                placeholder="Input an integer between 1-100",
                max_length=3,
                style=TextInputStyle.short,
                custom_id="rate"
            ),
            ui.TextInput(
                label="Angle",
                placeholder="Input an integer between 20-80",
                max_length=2,
                style=TextInputStyle.short,
                custom_id="angle"
            )
        ]
        super().__init__(title="Set Power", custom_id="power", components=components)

    async def callback(self, inter: ModalInteraction):
        background = Image.open("assets/background.png")
        bg_width = background.width
        power = None
        angle = None
        for custom_id, value in inter.text_values.items():
            if custom_id == "rate":
                if int(value) <= 100 and int(value) >= 1:
                    power = int(value)
                else:
                    await inter.send("Power needs to be between 1-100", ephemeral=True)
            if custom_id == "angle":
                if int(value) <= 80 and int(value) >= 20:
                    angle = int(value)
                else:
                    await inter.send("Angle needs to be between 20-80", ephemeral=True)
        if power and angle:
            stuff = set_power(bg_width, power, angle)
            
            distance = compute_distance(power, angle)
            battle_dict = ONGOING_BATTLES[inter.message.id]

            p1_cords = battle_dict["p1_cords"]
            tank_size = battle_dict["tank_size"]
            bg_img = battle_dict["bg_img"]
            bg_img.show()
            bg_img = prepare_attack_image(bg_img, p1_cords, tank_size, distance)
            
            background_bytes = BytesIO()
            bg_img.save(background_bytes, "PNG")
            background_bytes.seek(0)
            
            await inter.message.edit(content=stuff, file=File(filename="bg.png", fp=background_bytes))
            #await inter.send("You have attacked", ephemeral=True)

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
    """
        ⚔️ Battle
    """
    def __init__(self, bot):
        self.bot = bot

    @slash_command(name="battle", description="Battle")
    async def battle(self, ctx, opponent: Member):
        """
        Parameters
        ----------
        opponent: User to battle.
        """

        await ctx.response.defer()

        # Opening and preparing all the assets
        background = Image.open("assets/bg.png")

        # made a function to give tank images
        tank_left = give_tank_image("assets/tank_atk.png", 100)
        tank_right = give_tank_image("assets/tank_hp.png", 100)

        print(f"Background Dimensions: {background.width, background.height}")
        # It'll be good if our tank dimensions are same
        print(f"Tank Dimensions: {tank_left.width, tank_left.height}")
        
        # flipping the right tank
        tank_right = tank_right.transpose(Image.FLIP_LEFT_RIGHT)

        random_right_x = random.randint(1, 800)
        random_left_x = random.randint(1, 800)
        
        p1_cords = (random_left_x, (GROUND_LEVEL - tank_left.height))
        p2_cords = (background.width - (tank_right.width + random_right_x), (GROUND_LEVEL - tank_right.height))
        
        background.paste(
            tank_right,
            p2_cords,
            mask=tank_right,
        )
        # We subtracted width to make sure the tank does not go out of the background
        background.paste(
            tank_left, 
            p1_cords, 
            mask=tank_left, 
            )
        #print(p1_cords, p2_cords)
        background_bytes = BytesIO()
        background.save(background_bytes, "PNG")
        background_bytes.seek(0)

        msg = await ctx.edit_original_message(content=f"**{ctx.author.name}** <:VS:1004300296647868427>  **{opponent.name}**", file=File(filename="bg.png", fp=background_bytes), view=ButtonView(self.bot))
        ONGOING_BATTLES[msg.id] = {"p1_cords" : p1_cords, "p2_cords": p2_cords, "tank_size": tank_right.size, "bg_img" : background}

def setup(bot):
    bot.add_cog(Battle(bot))
