from core import GameObject
from py_engine import Engine

engine = Engine()

engine.register_sprite("link", 0)
engine.register_sprite("zelda_enemy", 1)


class Player(GameObject):
    def __init__(self, x=0, y=0):
        super().__init__(x, y)

    def render(self):
        return 0


class Sword(GameObject):
    def __init__(self, x=0, y=0, direction="right"):
        super().__init__(x, y)
        self.direction = direction
        self.alive = 2

    def render(self):
        if self.direction == "left":
            return "<"
        elif self.direction == "right":
            return ">"


class Enemy(GameObject):
    def __init__(self, x=0, y=0, health=1):
        super().__init__(x, y)
        self.health = health

    def render(self):
        return 1


def reset_enemies():
    engine.new_object(Enemy(x=2, y=-2))
    engine.new_object(Enemy(x=10, y=-1))
    engine.new_object(Enemy(x=14, y=-1))

    engine.new_object(Enemy(x=3, y=1))
    engine.new_object(Enemy(x=7, y=0))
    engine.new_object(Enemy(x=12, y=1))


def loop():
    for enemy in engine.get_objects_of(Enemy):
        if engine.player.x == enemy.x and engine.player.y == enemy.y:
            engine.reset()
            reset_enemies()

    js = engine.get_joystick()

    if js.left:
        engine.player.x -= 1
        engine.state["sword_dir"] = "left"
    if js.right:
        engine.player.x += 1
        engine.state["sword_dir"] = "right"
    if js.up:
        engine.player.y -= 1
    if js.down:
        engine.player.y += 1

    if engine.get_button_a():
        if len(engine.get_objects_of(Sword)) == 0:
            x = engine.player.x

            if engine.state["sword_dir"] == "left":
                x -= 1
            elif engine.state["sword_dir"] == "right":
                x += 1

            engine.new_object(
                Sword(
                    x=x,
                    y=engine.player.y,
                    direction=engine.state["sword_dir"],
                )
            )

    for sword in engine.get_objects_of(Sword):
        sword.x = engine.player.x
        sword.y = engine.player.y

        if sword.direction == "left":
            sword.x -= 1
        elif sword.direction == "right":
            sword.x += 1

        if sword.alive > 0:
            sword.alive -= 1

            for enemy in engine.get_objects_of(Enemy):
                if sword.x == enemy.x and sword.y == enemy.y:
                    enemy.health -= 1
                    if enemy.health <= 0:
                        engine.delete_object(enemy)
        else:
            engine.delete_object(sword)


engine.set_state(
    {
        "sword_dir": "right",
    }
)
reset_enemies()
engine.set_player(Player)
engine.run(loop)
