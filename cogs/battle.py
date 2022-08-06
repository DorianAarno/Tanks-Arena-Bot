import numpy as np
import random
from io import BytesIO
from random import randint, uniform

# from matplotlib import pyplot as plt

from disnake import *
from disnake.ext.commands import *
from PIL import Image, ImageDraw


G = 9.8

ONGOING_BATTLES = {}
GROUND_LEVEL = 825

# TODO: edit tank image after damage


def compute_distance(power, angle, msg_id):
    theta = angle * np.pi / 180
    x0 = 0
    v0 = power

    t = 2 * v0 * np.sin(theta) / G
    xt = x0 + (v0 * t * np.cos(theta))

    distance = round((xt - x0) * ONGOING_BATTLES[msg_id]["CONSTANT"])
    # if distance > 3000:
    #     distance = 3000

    return distance


def prepare_attack_image(cords, tank_size, distance, battle_dict):
    explosion_lst = ["explosion.png", "explosion2.png", "explosion3.png"]

    nozzle = Image.open("assets/nozzle.png")
    nozzle = nozzle.resize((120, 120))
    if cords[0] <= 800:
        nozzle = nozzle.transpose(Image.FLIP_LEFT_RIGHT)

    explosion = Image.open(f"assets/{random.choice(explosion_lst)}")
    explosion = explosion.resize((150, 150))

    if cords[0] <= 800:
        nozzle_x = cords[0] + tank_size[0]
    else:
        nozzle_x = cords[0] - tank_size[0]
    nozzle_y = int(cords[1] + 10)

    if cords[0] <= 800:
        explosion_x = int(cords[0] + (distance))
    else:
        explosion_x = int(cords[0] - (distance))
    explosion_y = GROUND_LEVEL - explosion.size[1]

    # Image will be regenerated to edit the HP bar
    p1_max_hp = battle_dict["p1_tank"]["max_hp"]
    p1_hp = battle_dict["p1_tank"]["hp"]
    print("p1: ", p1_max_hp, p1_hp)

    p2_max_hp = battle_dict["p2_tank"]["max_hp"]
    p2_hp = battle_dict["p2_tank"]["hp"]
    print("p2: ", p2_max_hp, p2_hp)

    # TODO: Find out ratio of HP and make sure HP bar works properly
    tank_left = give_tank_image(f"assets/{battle_dict['p1_tank']['tank']}.png", p1_max_hp, p1_hp)
    tank_right = give_tank_image(f"assets/{battle_dict['p2_tank']['tank']}.png", p2_max_hp, p2_hp)
    background = Image.open("assets/bg.png")

    tank_right = tank_right.transpose(Image.FLIP_LEFT_RIGHT)

    background.paste(
        tank_right, battle_dict["p2_tank"]["coords"], mask=tank_right,
    )
    # We subtracted width to make sure the tank does not go out of the background
    background.paste(
        tank_left, battle_dict["p1_tank"]["coords"], mask=tank_left,
    )

    if cords[0] <= 800:
        if nozzle_x + 30 < explosion_x:
            background.paste(nozzle, (nozzle_x, nozzle_y), mask=nozzle)
    else:
        if nozzle_x - 30 > explosion_x:
            background.paste(nozzle, (nozzle_x, nozzle_y), mask=nozzle)

    background.paste(explosion, (explosion_x, explosion_y), mask=explosion)

    return background


def give_tank_image(path, total_health, current_health=None):
    if current_health is None:
        current_health = total_health

    tank = Image.open(path)
    tank = tank.resize((140, 120))

    x_cord = 0
    y_cord = 0
    height = 5
    width = tank.size[1] - x_cord
    padding = 5  # padding between tank and bar and name

    # gives the health ratio
    health_ratio = width / total_health
    # gives the bar width
    bar_width = health_ratio * current_health

    # Bright Red
    bar_color = (255, 0, 0)
    # White
    bg_color = (255, 255, 255)

    im = Image.new(
        "RGBA", (tank.size[0] + 2, tank.size[1] + height + padding), (255, 255, 255, 0)
    )
    draw = ImageDraw.Draw(im)

    height += padding
    # make the bar circle at start
    draw.ellipse((x_cord, y_cord, x_cord + height, y_cord + height), fill=bg_color)
    # make the bar circle at the end
    draw.ellipse(
        (x_cord + width, y_cord, x_cord + width + height, y_cord + height),
        fill=bg_color,
    )
    # fill the middle portion
    draw.rectangle(
        (x_cord + (height / 2), y_cord, x_cord + width + (height / 2), y_cord + height),
        fill=bg_color,
    )

    if bar_width > 0:
        width = bar_width
        draw.ellipse((x_cord, y_cord, x_cord + height, y_cord + height), fill=bar_color)
        draw.ellipse(
            (x_cord + width, y_cord, x_cord + width + height, y_cord + height),
            fill=bar_color,
        )
        draw.rectangle(
            (
                x_cord + (height / 2),
                y_cord,
                x_cord + width + (height / 2),
                y_cord + height,
            ),
            fill=bar_color,
        )

    tank_x_cord = x_cord  # its same as exp bar for aesthetic looks
    height += padding

    im.paste(
        tank,
        (
            tank_x_cord,
            height + tank_x_cord,
            tank.size[0] + tank_x_cord,
            height + (tank.size[1] + tank_x_cord),
        ),
        mask=tank,
    )

    return im


def set_power(power, angle, msg_id):
    distance = compute_distance(power, angle, msg_id)
    return f"Power : {power} \nAngle : {angle} \nDistance Covered : {distance}"


async def get_tanks(bot, p1, p2):
    # Later change to fetch the default tank
    data_p1 = await bot.fetchrow(f"SELECT * FROM user_tanks WHERE user_id = {p1.id}")
    data_p2 = await bot.fetchrow(f"SELECT * FROM user_tanks WHERE user_id = {p2.id}")

    return (data_p1, data_p2)


def consume_hp(victim_hp, victim_defence, attack):
    return victim_hp - (attack - victim_defence)


class PowerModal(ui.Modal):
    def __init__(self) -> None:
        components = [
            ui.TextInput(
                label="Rate",
                placeholder="Input an integer between 1-100",
                max_length=3,
                style=TextInputStyle.short,
                custom_id="rate",
            ),
            ui.TextInput(
                label="Angle",
                placeholder="Input an integer between 20-80",
                max_length=2,
                style=TextInputStyle.short,
                custom_id="angle",
            ),
        ]
        super().__init__(title="Set Power", custom_id="power", components=components)

    async def callback(self, inter: ModalInteraction):
        battle_dict = ONGOING_BATTLES[inter.message.id]

        if inter.author.id != battle_dict["turn"].id:
            return await inter.send("It's not your turn yet!", ephemeral=True)

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
            stuff = set_power(power, angle, inter.message.id)

            distance = compute_distance(power, angle, inter.message.id)

            p1_cords = battle_dict["p1_tank"]["coords"]
            p2_cords = battle_dict["p2_tank"]["coords"]

            if battle_dict["p1_tank"]["author"].id == inter.author.id:
                battle_dict["turn"] = battle_dict["p2_tank"]["author"]
                attacker = "p1"
            else:
                battle_dict["turn"] = battle_dict["p1_tank"]["author"]
                attacker = "p2"

            if attacker == "p1":
                attacker_coords = p1_cords
                defender_coords = p2_cords

                # This iteration is an estimate to get coordinates around the tank
                # This may cover some extra coordinates to cover the dimensions of the explosion
                if distance + attacker_coords[0] + battle_dict["tank_size"][0] in [
                    x
                    for x in range(
                        defender_coords[0] - 10,
                        defender_coords[0] + battle_dict["tank_size"][0] + 68,
                    )
                ]:
                    # Consume HP code here
                    hp = battle_dict["p1_tank"]["hp"]
                    defence = battle_dict["p1_tank"]["def"]
                    p2_atk = battle_dict["p2_tank"]["atk"]
                    battle_dict["p1_tank"]["hp"] = consume_hp(hp, defence, p2_atk)
                    print("hit")

            else:
                attacker_coords = p2_cords
                defender_coords = p1_cords

                # This iteration is an estimate to get coordinates around the tank
                # This may cover some extra coordinates to cover the dimensions of the explosion
                if distance + (3000 - attacker_coords[0]) + battle_dict["tank_size"][
                    0
                ] in [
                    x
                    for x in range(
                        (3000 - defender_coords[0]) - 10,
                        (3000 - defender_coords[0]) + battle_dict["tank_size"][0] + 68,
                    )
                ]:
                    # Consume HP code here
                    hp = battle_dict["p2_tank"]["hp"]
                    defence = battle_dict["p2_tank"]["def"]
                    p1_atk = battle_dict["p1_tank"]["atk"]
                    battle_dict["p2_tank"]["hp"] = consume_hp(hp, defence, p1_atk)
                    print("hit")

            tank_size = battle_dict["tank_size"]

            bg_img = prepare_attack_image(
                attacker_coords, tank_size, distance, battle_dict
            )

            background_bytes = BytesIO()
            bg_img.save(background_bytes, "PNG")
            background_bytes.seek(0)

            await inter.send("You have attacked!", ephemeral=True)

            await inter.message.edit(
                content=stuff,
                file=File(filename="bg.png", fp=background_bytes),
                attachments=[],
            )


class ButtonView(ui.View):
    def __init__(self, bot):
        super().__init__()
        self.bot = bot

    @ui.button(style=ButtonStyle.blurple, label="Attack")
    async def atk_button(self, btn, inter: MessageInteraction):
        await inter.response.send_modal(PowerModal())


class Battle(Cog):
    """
        ⚔️ Battle
    """

    def __init__(self, bot):
        self.bot = bot

    @slash_command(name="battle", description="Battle")
    async def battle(self, ctx: CommandInteraction, opponent: Member):
        """
        Parameters
        ----------
        opponent: User to battle.
        """

        await ctx.response.defer()

        if opponent.bot or opponent.id == ctx.author.id:
            return await ctx.send(
                "You cannot have a battle with a bot or with yourself!"
            )

        # Opening and preparing all the assets
        background = Image.open("assets/bg.png")

        # made a function to give tank images
        p1_tank, p2_tank = await get_tanks(self.bot, ctx.author, opponent)
        if not p1_tank:
            return await ctx.send(
                f"**{ctx.author.name}** does not own any tank. Run `/start` to select your first battle tank!"
            )
        elif not p2_tank:
            return await ctx.send(
                f"**{opponent.name}** does not own any tank. Run `/start` to select your first battle tank!"
            )
        tank_left = give_tank_image(f"assets/{p1_tank[1]}.png", 100)
        tank_right = give_tank_image(f"assets/{p2_tank[1]}.png", 100)

        print(f"Background Dimensions: {background.width, background.height}")
        # It'll be good if our tank dimensions are same
        print(f"Tank Dimensions: {tank_left.width, tank_left.height}")

        # flipping the right tank
        tank_right = tank_right.transpose(Image.FLIP_LEFT_RIGHT)

        random_right_x = random.randint(1, 800)
        random_left_x = random.randint(1, 800)

        p1_cords = (random_left_x, (GROUND_LEVEL - tank_left.height))
        p2_cords = (
            background.width - (tank_right.width + random_right_x),
            (GROUND_LEVEL - tank_right.height),
        )

        background.paste(
            tank_right, p2_cords, mask=tank_right,
        )
        # We subtracted width to make sure the tank does not go out of the background
        background.paste(
            tank_left, p1_cords, mask=tank_left,
        )
        # print(p1_cords, p2_cords)
        background_bytes = BytesIO()
        background.save(background_bytes, "PNG")
        background_bytes.seek(0)

        msg = await ctx.edit_original_message(
            content=f"**{ctx.author.name}** <:VS:1004300296647868427>  **{opponent.name}**",
            file=File(filename="bg.png", fp=background_bytes),
            view=ButtonView(self.bot),
        )
        ONGOING_BATTLES[msg.id] = {
            "p1_tank": {
                "tank": p1_tank[1],
                "coords": p1_cords,
                "max_hp": p1_tank[2],
                "hp": p1_tank[2],
                "atk": p1_tank[3],
                "def": p1_tank[4],
                "author": ctx.author,
            },
            "p2_tank": {
                "tank": p2_tank[1],
                "coords": p2_cords,
                "max_hp": p2_tank[2],
                "hp": p2_tank[2],
                "atk": p2_tank[3],
                "def": p2_tank[4],
                "author": opponent,
            },
            "tank_size": tank_right.size,
            "bg_img": background,
            "CONSTANT": round(uniform(2.942, 3.3), 3),
            "turn": ctx.author,
        }


def setup(bot):
    bot.add_cog(Battle(bot))
