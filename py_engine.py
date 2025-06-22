import pygame
from PIL import Image

from core import Core, JoystickInputs
buzzer: None

class Engine(Core):
    sprites = {}

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

        self.sprites[number] = matrix

    def __render(self, obj):
        result = obj.render()

        if isinstance(result, str):
            img = Image.open(f"assets/font/{result}.png").convert("RGBA").resize((5, 8))

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

            return matrix

        if isinstance(result, int):
            if result in self.sprites:
                return self.sprites[result]
            else:
                raise ValueError(f"Sprite number {result} not registered.")


    def set_sound_config(music_name: str, effect_names = list[str] ):
        sound_effects: dict = {}
        music: dict = {}
        for effect_name in effect_names: 
            with open(f"assets/soundeffects/{effect_name}.txt") as f:
                notes = f.read().strip().split()
                sound_effects[effect_name] = { q : float(notes[q]) for q in range(len(notes))}
                f.close()

            with open(f"assets/music/{music_name}.txt") as f:
                notes = f.read().strip().split()
                music_length = len(notes)
                music = {i: float(notes[i]) for i in range(music_length)}
                f.close()

            Engine.state['music'] = music
            Engine.state['sound_effects'] = sound_effects
            Engine.state['music_length'] = music_length
            Engine.state['current_note_index'] = 0
            Engine.state['current_sound_effect'] = ''

    # play the current note of the soundtrack. cycle to beginning when finished.
    def play_sound(effect_name = ''):
            if(effect_name): 
                effect_notes: list[str] = Engine.state['sound_effects'][effect_name]
                for i in range(len(effect_notes)):
                    # buzzer.play(Tone.from_frequency(effect_notes[i]))  
                    print("JUMP!")
            else: 
                # buzzer.play(Tone.from_frequency(Engine.state['music'][Engine.state['current_note_index']]))
                print(Engine.state['music'][Engine.state['current_note_index']])
                Engine.state['current_note_index'] = (Engine.state['current_note_index'] + 1 ) % Engine.state['music_length']
    class GameObject:
        x = 0
        y = 0

        def __init__(self, x=0, y=0):
            self.x = x
            self.y = y

        def render(self):
            return [
                [1, 1, 1, 1, 1],
                [1, 1, 1, 1, 1],
                [1, 1, 1, 1, 1],
                [1, 1, 1, 1, 1],
                [1, 1, 1, 1, 1],
                [1, 1, 1, 1, 1],
                [1, 1, 1, 1, 1],
            ]

    class JoystickInputs:
        left = False
        right = False
        up = False
        down = False

        def __init__(self, left, right, up, down):
            self.left = left
            self.right = right
            self.up = up
            self.down = down

    def get_joystick():
        keys = pygame.key.get_pressed()
        return JoystickInputs(
            left=keys[pygame.K_a],
            right=keys[pygame.K_d],
            up=keys[pygame.K_w],
            down=keys[pygame.K_s],
        )

    def get_button_a(self):
        keys = pygame.key.get_pressed()
        return keys[pygame.K_j]

    def get_button_b(self):
        keys = pygame.key.get_pressed()
        return keys[pygame.K_l]

    def run(self, loop):
        CELL_WIDTH = 5
        CELL_HEIGHT = 8
        BORDER = 1
        COLS = 16
        ROWS = 2

        BG = (8, 90, 110)

        SCALE = 8  # Scale factor

        WINDOW_WIDTH = COLS * (CELL_WIDTH + BORDER) + BORDER
        WINDOW_HEIGHT = ROWS * (CELL_HEIGHT + BORDER) + BORDER

        pygame.init()
        # Create a small surface for drawing, then scale it up to the window
        lcd_surface = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
        screen = pygame.display.set_mode((WINDOW_WIDTH * SCALE, WINDOW_HEIGHT * SCALE))
        pygame.display.set_caption("16x2 LCD Display")

        def draw_lcd_cell(col, row, bits, bg=BG):
            x = BORDER + (col % 16) * (CELL_WIDTH + BORDER)
            y = BORDER + (row % 2) * (CELL_HEIGHT + BORDER)
            pygame.draw.rect(lcd_surface, bg, (x, y, CELL_WIDTH, CELL_HEIGHT))

            for row_idx in range(CELL_HEIGHT):
                for col_idx in range(CELL_WIDTH):
                    if bits[row_idx][col_idx] == 1:
                        rect = pygame.Rect(x + col_idx, y + row_idx, 1, 1)
                        pygame.draw.rect(lcd_surface, (255, 255, 255), rect)

        def clear_lcd(bg=BG):
            lcd_surface.fill((4, 72, 89))

            for row in range(ROWS):
                for col in range(COLS):
                    draw_lcd_cell(
                        col,
                        row,
                        [[0 for _ in range(CELL_WIDTH)] for _ in range(CELL_HEIGHT)],
                        bg=bg,
                    )

        clear_lcd()
        pygame.display.flip()
        Engine.set_sound_config(Engine.state['music'], Engine.state['sound_names'])
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

            clear_lcd()
            Engine.play_sound()
            loop()

            for obj in self.resolve_positions():
                draw_lcd_cell(obj.x, obj.y, self.__render(obj))

            draw_lcd_cell(self.player.x, self.player.y, self.__render(self.player))

            # Scale up the lcd_surface and blit to the screen
            scaled_surface = pygame.transform.scale(
                lcd_surface, (WINDOW_WIDTH * SCALE, WINDOW_HEIGHT * SCALE)
            )
            screen.blit(scaled_surface, (0, 0))
            pygame.display.flip()
            pygame.time.delay(100)

    def reset():
        Engine.state = Engine.initial_state.copy()
        Engine.set_sound_config(Engine.state['music'], Engine.state['sound_names'])
        Engine.objects = []
