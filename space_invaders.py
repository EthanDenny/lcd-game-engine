from core import GameObject
from py_engine import Engine


engine = Engine()


engine.register_sprite("player", 0)
engine.register_sprite("alien", 1)
engine.register_sprite("bullet", 2)


class Player(GameObject):
    def __init__(self, x=7, y=1):
        super().__init__(x, y)

    def render(self):
        return 0


class Alien(GameObject):
    def __init__(self, x=5, y=0):
        super().__init__(x, y)

    def render(self):
        return 1


class Bullet(GameObject):
    def __init__(self, x, y):
        super().__init__(x, y)

    def render(self):
        return 2


def loop():
    js = engine.get_joystick()
    bullets = engine.get_objects_of(Bullet)

    # Move player
    if js.left and engine.player.x > 0:
        engine.player.x -= 1
    if js.right and engine.player.x < 15:
        engine.player.x += 1

    # Move bullet up
    for bullet in bullets:
        bullet.y -= 1

        marked_for_deletion = False

        if bullet.y < 0:
            marked_for_deletion = True
        else:
            for alien in engine.get_objects_of(Alien):
                if bullet.x == alien.x and bullet.y == alien.y:
                    engine.delete_object(alien)
                    marked_for_deletion = True

        if marked_for_deletion:
            engine.delete_object(bullet)

    # Fire bullet
    if engine.get_button_a() and len(bullets) == 0:
        engine.new_object(Bullet(engine.player.x, engine.player.y))


engine.new_object(Alien())
engine.set_player(Player)
engine.run(loop)
