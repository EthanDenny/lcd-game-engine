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

# Custom Characters
player_char = [
    0b00100,
    0b01110,
    0b11111,
    0b00100,
    0b01110,
    0b10101,
    0b00100,
    0b01010
]

alien_char = [
    0b01110,
    0b10101,
    0b11111,
    0b11011,
    0b11111,
    0b10101,
    0b01010,
    0b00100
]

bullet_char = [
    0b00100,
    0b00100,
    0b00100,
    0b00100,
    0b00000,
    0b00000,
    0b00000,
    0b00000
]

lcd.create_char(0, player_char)
lcd.create_char(1, alien_char)
lcd.create_char(2, bullet_char)

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