from core import GameObject
from py_engine import Engine

engine = Engine()


class Player(GameObject):
    def __init__(self, x=0, y=0):
        super().__init__(x, y)

    def render(self):
        return "@"


class Enemy(GameObject):
    def __init__(self, x=0, y=0, health=1):
        super().__init__(x, y)
        self.health = health


class Kobold(Enemy):
    def __init__(self, x=0, y=0):
        super().__init__(x, y, 2)

    def render(self):
        return "K"


def loop():
    old_player_pos = [engine.player.x, engine.player.y]

    def reset_player_pos():
        engine.player.x = old_player_pos[0]
        engine.player.y = old_player_pos[1]

    js = engine.get_joystick()

    if js.left:
        engine.player.x = max(0, engine.player.x - 1)
    if js.right:
        engine.player.x = min(15, engine.player.x + 1)
    if js.up:
        engine.player.y = max(0, engine.player.y - 1)
    if js.down:
        engine.player.y = min(1, engine.player.y + 1)

    for enemy in engine.get_objects_of(Enemy):
        if enemy.x == engine.player.x and enemy.y == engine.player.y:
            enemy.health -= 1
            reset_player_pos()

            if enemy.health == 0:
                engine.delete_object(enemy)


engine.new_object(Kobold(x=7, y=0))
engine.new_object(Kobold(x=12, y=1))
engine.set_player(Player)
engine.run(loop)
