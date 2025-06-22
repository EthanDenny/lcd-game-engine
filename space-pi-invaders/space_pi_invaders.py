from RPLCD.i2c import CharLCD  
from gpiozero import Button
import time

# LCD Setup (Adjust address if needed)
lcd = CharLCD(i2c_expander="PCF8574", address=0x27, port=1, cols=16, rows=2, dotsize=8, charmap='A00', auto_linebreaks=False)


# Button Setup (GPIO pins)
left_btn = Button(17)
right_btn = Button(18)
fire_btn = Button(27)

# Game State
player_pos = 7
bullet_pos = None
alien_pos = 5
alien_alive = True

# Sprites

ship_sprite = [
0B00000,
0B00000,
0B00000,
0B00000,
0B00000,
0B00100,
0B01110,
0B11011
]

ship_bullet_sprite = [
0B00000,
0B00100,
0B00100,
0B00000,
0B00000,
0B00100,
0B01110,
0B11011
]

bullet_down_sprite = [
0B00000,
0B00000,
0B00000,
0B00000,
0B00000,
0B00100,
0B00100,
0B00000
]

bullet_up_sprite = [
0B00000,
0B00100,
0B00100,
0B00000,
0B00000,
0B00000,
0B00000,
0B00000
]

alien1_1_sprite = [
0B01010,
0B10101,
0B01110,
0B10001,
0B00000,
0B00000,
0B00000,
0B00000
]

alien1_2_sprite = [
0B01010,
0B10101,
0B01110,
0B01010,
0B00000,
0B00000,
0B00000,
0B00000
]

alien1_1_bullet_sprite = [
0B01010,
0B10101,
0B01110,
0B10001,
0B00000,
0B00100,
0B00100,
0B00000
]

alien1_2_bullet_sprite = [
0B01010,
0B10101,
0B01110,
0B01010,
0B00000,
0B00100,
0B00100,
0B00000
]

lcd.create_char(0, ship_sprite)
lcd.create_char(1, alien1_1_sprite)
lcd.create_char(2, ship_bullet_sprite)

def draw():
    lcd.clear()

    # Row 0: Alien
    if alien_alive:
        lcd.cursor_pos = (0, alien_pos)
        lcd.write_string(chr(1))  # alien

    # Row 0: Bullet
    if bullet_pos is not None and bullet_pos < 2:
        lcd.cursor_pos = (0, player_pos)
        lcd.write_string(chr(2))  # bullet

    # Row 1: Player
    lcd.cursor_pos = (1, player_pos)
    lcd.write_string(chr(0))  # player

def update():
    global player_pos, bullet_pos, alien_alive

    # Move player
    if left_btn.is_pressed and player_pos > 0:
        player_pos -= 1
    if right_btn.is_pressed and player_pos < 15:
        player_pos += 1

    # Fire bullet
    if fire_btn.is_pressed and bullet_pos is None:
        bullet_pos = player_pos

    # Move bullet up
    if bullet_pos is not None:
        if bullet_pos == alien_pos and alien_alive:
            alien_alive = False
            bullet_pos = None
        else:
            bullet_pos = None  # bullet moves up once only

try:
    while True:
        update()
        draw()
        time.sleep(0.2)

except KeyboardInterrupt:
    lcd.clear()
    print("Game stopped.")