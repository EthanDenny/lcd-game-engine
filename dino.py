from core import GameObject
from lcd_engine import Engine
import random

engine = Engine()

engine.register_sprite("dino", 0)
engine.register_sprite("cactus", 1)
engine.register_sprite("rock", 2)
engine.register_sprite("bird", 3)


class Player(GameObject):
    jump_time = 0

    def __init__(self):
        super().__init__(1, 1)

    def render(self):
        return 0


class Obstacle(GameObject):
    kind = "cactus"

    def __init__(self):
        self.kind = random.choice(["cactus", "rock", "bird"])
        super().__init__(15, 0 if self.kind == "bird" else 1)

    def render(self):
        match self.kind:
            case "cactus":
                return 1
            case "rock":
                return 2
            case "bird":
                return 3
            case _:
                return "X"


def loop():
    engine.state["sound"].playNote(engine.state["soundEffect"])
    engine.state["soundEffect"] = ""

    if engine.state["otimer"] % 4 == 0:
        for obj in engine.get_objects_of(Obstacle):
            obj.x -= 1

    if engine.state["otimer"] == 0:
        engine.new_object(Obstacle())
        engine.state["otimer"] = 20

    engine.state["otimer"] -= 1

    if Engine.player.jump_time > 0:
        Engine.player.jump_time -= 1
    elif Engine.get_button_a():
        Engine.player.jump_time = 8
        Engine.play_sound('dinojump')

    engine.player.y = 0 if engine.player.jump_time > 0 else 1

    for obj in engine.get_objects_of(Obstacle):
        if engine.player.x == obj.x and engine.player.y == obj.y:
            engine.reset()
            engine.player.jump_time = 0


# Start the game

engine.set_state(
    {
        "otimer": 0,  # Obstacle timer
        "music": 'default',
        'sound_names': ["dinojump"]
    }
)
engine.set_player(Player)
engine.run(loop)
