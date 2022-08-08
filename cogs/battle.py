import numpy as np
import random
import json
from io import BytesIO
from random import uniform, choice

# from matplotlib import pyplot as plt

from disnake import *
from disnake.ext.commands import *
from PIL import Image, ImageDraw


G = 9.8

ONGOING_BATTLES = {}
GROUND_LEVEL = 825

# TODO: Confirm challenge by opponent, give out coins in the end, edit get_tanks to fetch the default tank


def compute_distance(power, angle, msg_id):
    theta = angle * np.pi / 180
    x0 = 0
    v0 = power

    t = 2 * v0 * np.sin(theta) / G
    xt = x0 + (v0 * t * np.cos(theta))

    distance = round((xt - x0) * ONGOING_BATTLES[msg_id]["CONSTANT"])

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

    p2_max_hp = battle_dict["p2_tank"]["max_hp"]
    p2_hp = battle_dict["p2_tank"]["hp"]

    tank_left = give_tank_image(f"assets/{battle_dict['p1_tank']['tank']}.png", p1_max_hp, p1_hp)
    tank_right = give_tank_image(f"assets/{battle_dict['p2_tank']['tank']}.png", p2_max_hp, p2_hp)
    background = Image.open("assets/bg.png")

    tank_right = tank_right.transpose(Image.FLIP_LEFT_RIGHT)

    background.paste(
        tank_right, battle_dict["p2_tank"]["coords"], mask=tank_right,
    )
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

    # gives the bar_width
    bar_width = (current_health / total_health) * 100

    total_possible_width = 100

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
        (x_cord + total_possible_width, y_cord, x_cord + total_possible_width + height, y_cord + height),
        fill=bg_color,
    )
    # fill the middle portion
    draw.rectangle(
        (x_cord + (height / 2), y_cord, x_cord + total_possible_width + (height / 2), y_cord + height),
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


def give_remarks(author, attacker_coords, defender_coords, distance, battle_dict):

    hit = confirm_hit(attacker_coords, defender_coords, distance, battle_dict)

    if hit:
        remarks = [f"Brutal! **{author.name}** dealt damage!", "That's a hit!", "No mercy!", "Keep it up soldier!", ]
        return choice(remarks)
    
    if attacker_coords[0] <= 800:
        distance += attacker_coords[0] 
        distance += battle_dict['tank_size'][0]
        attacker_coords = (2200 + attacker_coords[0], attacker_coords[1])
    else:
        distance += 3000 - attacker_coords[0]
        distance = distance - battle_dict['tank_size'][0]
    
    
    if attacker_coords[0] in [x for x in range(
        distance, distance+201
    )]:
        remarks = [
            'Close call!',
            "Almost there! keep adjusting",
            "That's right! You can do it",
        ]
        return choice(remarks)

    else:
        remarks = [
            "Adjustment is the key to success. Keep adjusting the power and angle until you find the perfect one!",
            "Don't let your opponent figure out the adjustments before you!",
            "Every tank has it's own special stat, some might be good in attack while others in defence or HP. ",
            "**Did You know?** \nEvery tank's name makes sense if you search it up."
        ]
        return choice(remarks)


async def get_tanks(bot, p1, p2):
    # TODO Later change to fetch the default tank
    data_p1 = await bot.fetch(f"SELECT * FROM user_tanks WHERE user_id = {p1.id}")
    tank_p1 = data_p1[0]
    if len(data_p1) > 1:
        battle_tank = await bot.fetchval(
            "SELECT battle_tank FROM users WHERE user_id = ?",
            p1.id
        )
        t_type, hp, atck, defe = json.loads(battle_tank)
        for d in data_p1:
            if d[1] == t_type and d[3] == hp and d[4] == atck and d[5] == defe:
                tank_p1 = d
    data_p2 = await bot.fetch(f"SELECT * FROM user_tanks WHERE user_id = {p2.id}")
    tank_p2 = data_p2[0]
    if len(data_p2) > 1:
        battle_tank = await bot.fetchval(
            "SELECT battle_tank FROM users WHERE user_id = ?",
            p2.id
        )
        t_type, hp, atck, defe = json.loads(battle_tank)
        for d in data_p2:
            if d[1] == t_type and d[3] == hp and d[4] == atck and d[5] == defe:
                tank_p2 = d

    return (tank_p1, tank_p2)


def consume_hp(self, battle_dict, player):
    if player == 'p1':
        enemy = 'p2'
    else:
        enemy = 'p1'

    hp = battle_dict[f"{enemy}_tank"]["hp"]
    defence = battle_dict[f"{enemy}_tank"]["def"]
    player_atk = battle_dict[f"{player}_tank"]["atk"]

    battle_dict[f"{enemy}_tank"]["hp"] = hp - (player_atk - defence)

    if battle_dict[f'{enemy}_tank']['hp'] <= 0:
        self.game_over = True



def confirm_hit(attacker_coords, defender_coords, distance, battle_dict):
    # This iteration is an estimate to get coordinates around the tank
    # This may cover some extra coordinates to cover the dimensions of the explosion

    if distance + attacker_coords[0] + battle_dict["tank_size"][0] in [
        x
        for x in range(
            defender_coords[0] - 10,
            defender_coords[0] + battle_dict["tank_size"][0] + 68,
        )
    ]:
        return True
        

class PowerModal(ui.Modal):
    def __init__(self) -> None:
        self.game_over = False
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

                if confirm_hit(attacker_coords, defender_coords, distance, battle_dict,):
                    consume_hp(self, battle_dict, 'p1')

            else:
                attacker_coords = p2_cords
                defender_coords = p1_cords

                if confirm_hit((3000 - attacker_coords[0], attacker_coords[1]), (3000 - defender_coords[0], defender_coords[1]), distance, battle_dict, ):
                    consume_hp(self, battle_dict, 'p2')


            tank_size = battle_dict["tank_size"]

            bg_img = prepare_attack_image(
                attacker_coords, tank_size, distance, battle_dict
            )

            background_bytes = BytesIO()
            bg_img.save(background_bytes, "PNG")
            background_bytes.seek(0)

            await inter.send("You have successfully attacked!", ephemeral=True)

            await inter.message.edit(
                content=give_remarks(inter.author, attacker_coords, defender_coords, distance, battle_dict),
                file=File(filename="bg.png", fp=background_bytes),
                attachments=[],
            )

            if self.game_over:
                await inter.message.edit(
                    f"{inter.author.mention} has won the game!",
                    view=None
                )


class ButtonView(ui.View):
    def __init__(self, bot):
        super().__init__()
        self.bot = bot

    @ui.button(style=ButtonStyle.blurple, label="Attack")
    async def atk_button(self, btn, inter: MessageInteraction):
        await inter.response.send_modal(PowerModal())

class ConfirmationButtons(ui.View):
    def __init__(self, authorid):
        super().__init__(timeout=120.0)
        self.value = None
        self.authorid = authorid
    @ui.button(emoji="✖️", style=ButtonStyle.red)
    async def first_button(self, button, inter):
        if inter.author.id != self.authorid:
            return await inter.send("You cannot interact with these buttons.", ephemeral=True)
        self.value = False
        for button in self.children:
            button.disabled = True
        await inter.response.edit_message(view=self)
        self.stop()
    @ui.button(emoji="✔️", style=ButtonStyle.green)
    async def second_button(self, button, inter):
        if inter.author.id != self.authorid:
            return await inter.send("You cannot interact with these buttons.", ephemeral=True)
        self.value = True
        for button in self.children:
            button.disabled = True
        await inter.response.edit_message(view=self)
        self.stop()


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

        view = ConfirmationButtons(opponent.id)
        msg = await ctx.send(f"{opponent.mention} You've been invited to a battle by {ctx.author.mention}!", view=view)
        await view.wait()
        if view.value is None:
            await ctx.edit_original_message(content="Timed Out.")
            return
        elif not view.value:
            await ctx.edit_original_message(content=f"{opponent.mention} rejected the battle invitation.")
            return 

        # Opening and preparing all the assets
        background = Image.open("assets/bg.png")

        tank_left = give_tank_image(f"assets/{p1_tank[1]}.png", 100)
        tank_right = give_tank_image(f"assets/{p2_tank[1]}.png", 100)

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

        background.paste(
            tank_left, p1_cords, mask=tank_left,
        )
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
                "max_hp": p1_tank[3],
                "hp": p1_tank[3],
                "atk": p1_tank[4],
                "def": p1_tank[5],
                "author": ctx.author,
            },
            "p2_tank": {
                "tank": p2_tank[1],
                "coords": p2_cords,
                "max_hp": p2_tank[3],
                "hp": p2_tank[3],
                "atk": p2_tank[4],
                "def": p2_tank[5],
                "author": opponent,
            },
            "tank_size": tank_right.size,
            "bg_img": background,
            "CONSTANT": round(uniform(2.942, 3.3), 3),
            "turn": ctx.author,
        }


def setup(bot):
    bot.add_cog(Battle(bot))
