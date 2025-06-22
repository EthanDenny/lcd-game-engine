from PIL import Image
from RPLCD.i2c import CharLCD
from core import Core, JoystickInputs
from gpiozero import TonalBuzzer
from gpiozero.tones import Tone
from gpiozero.exc import BadPinFactory
import time
from gpiozero import Button
from gpiozero import Device
from gpiozero.pins.pigpio import PiGPIOFactory
import smbus

Device.pin_factory = PiGPIOFactory()


lcd = CharLCD(i2c_expander="PCF8574", address=0x27, port=1, cols=16, rows=2, dotsize=8)
a_button = Button(6)
b_button = Button(5)
bus = smbus.SMBus(1)
joystick_address = 0x48


def read_channel(channel):
    if channel > 3 or channel < 0:
        return -1
    bus.write_byte(joystick_address, 0x40 | channel)
    bus.read_byte(joystick_address)  # Dummy read (first read is unreliable)
    return bus.read_byte(joystick_address)


class Engine(Core):
    unrendered_cells = set()

    def register_sprite(self, name, number):
        img = Image.open(f"assets/{name}.png").convert("RGBA").resize((5, 8))

        matrix = []
        for y in range(8):
            row = []
            for x in range(5):
                r, g, b, a = img.getpixel((x, y))
                if a > 0 and r < 128 and g < 128 and b < 128:
                    row.append(1)
                else:
                    row.append(0)
            matrix.append(row)

        byte_map = [int("".join(map(str, row)), 2) for row in matrix]

        lcd.create_char(number, byte_map)

    class Sound:
        def __init__(self, music="default", soundEffects: list[str] = []):
            try:
                self.buzzer: TonalBuzzer = TonalBuzzer(26)
            except BadPinFactory:
                self.buzzer = None
                print("buzzer setup failed")
            self.currentNoteIndex = 0
            self.soundEffects = {}

            for effectName in soundEffects:
                with open(f"assets/soundeffects/{effectName}.txt") as f:
                    notes = f.read().strip().split()
                    self.soundEffects[effectName] = {
                        q: float(notes[q]) for q in range(len(notes))
                    }
                    f.close()

            with open(f"assets/music/{music}.txt") as f:
                notes = f.read().strip().split()
                self.soundtrackLength = len(notes)
                self.musicNotes = {
                    i: float(notes[i]) for i in range(self.soundtrackLength)
                }
                f.close()

        def playSoundEffect(self, effectName: str):
            if not self.buzzer:
                return

            effectNotes: list[str] = self.soundEffects[effectName]
            for i in range(len(effectNotes)):
                # TODO: determine transition step value to reduce choppiness
                self.buzzer.play(Tone.from_frequency(effectNotes[i]))

        # play the current note of the soundtrack. cycle to beginning when finished.
        def playNote(self, effectName=""):
            if not self.buzzer:
                return
            elif effectName:
                self.playSoundEffect(effectName)
            else:
                # TODO: determine transition step value to reduce choppiness
                self.buzzer.play(
                    Tone.from_frequency(self.musicNotes[self.currentNoteIndex])
                )
                self.currentNoteIndex = (
                    self.currentNoteIndex + 1
                ) % self.soundtrackLength

    def get_joystick(self):
        x_val = read_channel(0)  # AIN0 (VRx)
        y_val = read_channel(1)  # AIN1 (VRy)
        x = x_val / 255
        y = y_val / 255
        left = False
        right = False
        up = False
        down = False

        if 0 <= x < 0.2:
            left = True
        if 0.8 < x <= 1:
            right = True
        if 0 <= y < 0.2:
            down = True
        if 0.8 < y <= 1:
            up = True

        return JoystickInputs(
            left=left,
            right=right,
            up=up,
            down=down,
        )

    def get_button_a(self):
        return a_button.is_pressed

    def get_button_b(self):
        return b_button.is_pressed

    def reset_unrendered_cells(self):
        self.unrendered_cells = set((x, y) for x in range(16) for y in range(2))

    def render_cell(self, cell, x, y):
        lcd.cursor_pos = (y % 2, x % 16)
        lcd.write_string(chr(cell) if isinstance(cell, int) else cell)
        self.unrendered_cells.discard((x % 16, y % 2))

    def run(self, loop):
        lcd.clear()

        while True:
            start_time = time.time()

            self.reset_unrendered_cells()

            loop()

            lcd.clear()

            for obj in self.resolve_positions():
                self.render_cell(obj.render(), obj.x, obj.y)

            self.render_cell(self.player.render(), self.player.x, self.player.y)

            for x, y in self.unrendered_cells:
                lcd.cursor_pos = (y, x)
                lcd.write_string(" ")

            self.unrendered_cells.clear()

            elapsed = time.time() - start_time
            if elapsed < 0.1:
                time.sleep(0.1 - elapsed)
