#!/usr/bin/env python3
"""
Enhanced LCD Game Engine for Raspberry Pi 4B
Optimized for 16x2 LCD displays with I2C interface
"""

import time
import logging
import threading
from typing import Dict, List, Optional, Tuple, Any, Callable
from dataclasses import dataclass
from enum import Enum
import smbus2
from PIL import Image
import numpy as np

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class InputType(Enum):
    """Input types for the engine"""
    JOYSTICK = "joystick"
    BUTTONS = "buttons"
    KEYBOARD = "keyboard"

@dataclass
class LCDConfig:
    """Configuration for LCD display"""
    i2c_address: int = 0x27
    i2c_port: int = 1
    cols: int = 16
    rows: int = 2
    dotsize: int = 8
    expander: str = "PCF8574"
    charmap: str = 'A00'
    auto_linebreaks: bool = False
    backlight_enabled: bool = True
    cursor_visible: bool = False
    blink_enabled: bool = False

@dataclass
class InputConfig:
    """Configuration for input devices"""
    input_type: InputType = InputType.BUTTONS
    # GPIO pins for buttons (BCM numbering)
    left_pin: int = 17
    right_pin: int = 18
    up_pin: int = 22
    down_pin: int = 23
    button_a_pin: int = 27
    button_b_pin: int = 24
    # Joystick pins
    joystick_x_pin: int = 26
    joystick_y_pin: int = 19
    joystick_center_pin: int = 13

class LCDManager:
    """Manages LCD display with error handling and optimization"""
    
    def __init__(self, config: LCDConfig):
        self.config = config
        self.lcd = None
        self.is_connected = False
        self.frame_buffer = [[' ' for _ in range(config.cols)] for _ in range(config.rows)]
        self.dirty_cells = set()
        self.custom_chars = {}
        self.char_counter = 0
        
        self._connect_lcd()
    
    def _connect_lcd(self):
        """Connect to LCD with fallback addresses"""
        addresses_to_try = [self.config.i2c_address, 0x3F, 0x26, 0x25]
        
        for address in addresses_to_try:
            try:
                # Test I2C connection
                bus = smbus2.SMBus(self.config.i2c_port)
                bus.read_byte(address)
                bus.close()
                
                # Import RPLCD only after confirming I2C connection
                from RPLCD.i2c import CharLCD
                
                self.lcd = CharLCD(
                    i2c_expander=self.config.expander,
                    address=address,
                    port=self.config.i2c_port,
                    cols=self.config.cols,
                    rows=self.config.rows,
                    dotsize=self.config.dotsize,
                    charmap=self.config.charmap,
                    auto_linebreaks=self.config.auto_linebreaks
                )
                
                # Configure LCD
                self.lcd.backlight_enabled = self.config.backlight_enabled
                self.lcd.cursor_mode = 'hide' if not self.config.cursor_visible else 'line'
                self.lcd.blink_mode = self.config.blink_enabled
                
                self.is_connected = True
                logger.info(f"LCD connected successfully at address 0x{address:02X}")
                return
                
            except Exception as e:
                logger.warning(f"Failed to connect to LCD at address 0x{address:02X}: {e}")
                continue
        
        logger.error("Failed to connect to LCD at any address")
        self.is_connected = False
    
    def clear(self):
        """Clear the LCD and frame buffer"""
        if self.is_connected:
            self.lcd.clear()
        self.frame_buffer = [[' ' for _ in range(self.config.cols)] for _ in range(self.config.rows)]
        self.dirty_cells = set()
    
    def write_string(self, text: str, row: int, col: int):
        """Write string to LCD at specific position"""
        if not self.is_connected:
            return
        
        # Check bounds
        if row < 0 or row >= self.config.rows or col < 0 or col >= self.config.cols:
            return
        
        # Update frame buffer
        for i, char in enumerate(text):
            if col + i < self.config.cols:
                if self.frame_buffer[row][col + i] != char:
                    self.frame_buffer[row][col + i] = char
                    self.dirty_cells.add((row, col + i))
        
        # Write to LCD
        self.lcd.cursor_pos = (row, col)
        self.lcd.write_string(text)
    
    def write_char(self, char: int, row: int, col: int):
        """Write custom character to LCD"""
        if not self.is_connected:
            return
        
        if row < 0 or row >= self.config.rows or col < 0 or col >= self.config.cols:
            return
        
        # Update frame buffer
        if self.frame_buffer[row][col] != char:
            self.frame_buffer[row][col] = char
            self.dirty_cells.add((row, col))
        
        # Write to LCD
        self.lcd.cursor_pos = (row, col)
        self.lcd.write_string(chr(char))
    
    def create_custom_char(self, char_data: List[int]) -> int:
        """Create custom character and return its ID"""
        if not self.is_connected:
            return 0
        
        char_id = self.char_counter % 8  # LCD supports 8 custom characters
        self.lcd.create_char(char_id, char_data)
        self.custom_chars[char_id] = char_data
        self.char_counter += 1
        return char_id
    
    def set_backlight(self, enabled: bool):
        """Control LCD backlight"""
        if self.is_connected:
            self.lcd.backlight_enabled = enabled
        self.config.backlight_enabled = enabled
    
    def cleanup(self):
        """Clean up LCD resources"""
        if self.is_connected:
            self.lcd.clear()
            self.lcd.close()

class InputManager:
    """Manages input devices with abstraction layer"""
    
    def __init__(self, config: InputConfig):
        self.config = config
        self.buttons = {}
        self.joystick_values = {'x': 0, 'y': 0, 'center': False}
        self._setup_inputs()
    
    def _setup_inputs(self):
        """Setup input devices based on configuration"""
        try:
            from gpiozero import Button, MCP3008
            
            if self.config.input_type == InputType.BUTTONS:
                self.buttons = {
                    'left': Button(self.config.left_pin, pull_up=True),
                    'right': Button(self.config.right_pin, pull_up=True),
                    'up': Button(self.config.up_pin, pull_up=True),
                    'down': Button(self.config.down_pin, pull_up=True),
                    'a': Button(self.config.button_a_pin, pull_up=True),
                    'b': Button(self.config.button_b_pin, pull_up=True)
                }
            
            elif self.config.input_type == InputType.JOYSTICK:
                # Setup ADC for joystick if available
                try:
                    self.adc = MCP3008()
                    self.joystick_center = Button(self.config.joystick_center_pin, pull_up=True)
                except:
                    logger.warning("ADC not available, using buttons as fallback")
                    self.config.input_type = InputType.BUTTONS
                    self._setup_inputs()
                    
        except ImportError:
            logger.warning("gpiozero not available, using keyboard fallback")
            self.config.input_type = InputType.KEYBOARD
    
    def get_joystick(self) -> 'JoystickInputs':
        """Get current joystick state"""
        if self.config.input_type == InputType.KEYBOARD:
            # Keyboard fallback
            import pygame
            keys = pygame.key.get_pressed()
            return JoystickInputs(
                left=keys[pygame.K_a] or keys[pygame.K_LEFT],
                right=keys[pygame.K_d] or keys[pygame.K_RIGHT],
                up=keys[pygame.K_w] or keys[pygame.K_UP],
                down=keys[pygame.K_s] or keys[pygame.K_DOWN]
            )
        
        elif self.config.input_type == InputType.BUTTONS:
            return JoystickInputs(
                left=self.buttons.get('left', False).is_pressed,
                right=self.buttons.get('right', False).is_pressed,
                up=self.buttons.get('up', False).is_pressed,
                down=self.buttons.get('down', False).is_pressed
            )
        
        elif self.config.input_type == InputType.JOYSTICK:
            # Read joystick values
            x_val = self.adc.value if hasattr(self, 'adc') else 0.5
            y_val = self.adc.value if hasattr(self, 'adc') else 0.5
            
            return JoystickInputs(
                left=x_val < 0.3,
                right=x_val > 0.7,
                up=y_val < 0.3,
                down=y_val > 0.7
            )
        
        return JoystickInputs(False, False, False, False)
    
    def get_button_a(self) -> bool:
        """Get button A state"""
        if self.config.input_type == InputType.KEYBOARD:
            import pygame
            keys = pygame.key.get_pressed()
            return keys[pygame.K_j] or keys[pygame.K_SPACE]
        
        return self.buttons.get('a', False).is_pressed
    
    def get_button_b(self) -> bool:
        """Get button B state"""
        if self.config.input_type == InputType.KEYBOARD:
            import pygame
            keys = pygame.key.get_pressed()
            return keys[pygame.K_k] or keys[pygame.K_RETURN]
        
        return self.buttons.get('b', False).is_pressed

class SpriteManager:
    """Manages sprite loading, caching, and optimization"""
    
    def __init__(self):
        self.sprites = {}
        self.sprite_cache = {}
        self.char_mapping = {}
    
    def register_sprite(self, name: str, number: int) -> bool:
        """Register a sprite from PNG file"""
        try:
            img = Image.open(f"assets/{name}.png").convert("RGBA").resize((5, 8))
            
            # Convert to binary matrix
            matrix = []
            for y in range(8):
                row = []
                for x in range(5):
                    r, g, b, a = img.getpixel((x, y))
                    # Improved threshold detection
                    if a > 128 and (r + g + b) / 3 < 128:
                        row.append(1)
                    else:
                        row.append(0)
                matrix.append(row)
            
            # Convert to byte array for LCD
            byte_map = []
            for row in matrix:
                byte_val = 0
                for i, bit in enumerate(row):
                    if bit:
                        byte_val |= (1 << (4 - i))
                byte_map.append(byte_val)
            
            self.sprites[number] = {
                'matrix': matrix,
                'bytes': byte_map,
                'name': name
            }
            
            logger.info(f"Sprite '{name}' registered as number {number}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to register sprite '{name}': {e}")
            return False
    
    def get_sprite_bytes(self, number: int) -> List[int]:
        """Get sprite byte data for LCD"""
        if number in self.sprites:
            return self.sprites[number]['bytes']
        return [0] * 8  # Return empty sprite
    
    def get_sprite_matrix(self, number: int) -> List[List[int]]:
        """Get sprite matrix data"""
        if number in self.sprites:
            return self.sprites[number]['matrix']
        return [[0] * 5 for _ in range(8)]  # Return empty sprite

class JoystickInputs:
    """Joystick input state"""
    def __init__(self, left: bool, right: bool, up: bool, down: bool):
        self.left = left
        self.right = right
        self.up = up
        self.down = down

class GameObject:
    """Base class for game objects"""
    def __init__(self, x: int = 0, y: int = 0):
        self.x = x
        self.y = y
        self.visible = True
        self.active = True
    
    def render(self) -> int:
        """Render method - override in subclasses"""
        return 0
    
    def update(self, delta_time: float):
        """Update method - override in subclasses"""
        pass
    
    def on_collision(self, other: 'GameObject'):
        """Collision handler - override in subclasses"""
        pass

class Engine:
    """Enhanced LCD Game Engine"""
    
    # Static variables
    lcd_manager: Optional[LCDManager] = None
    input_manager: Optional[InputManager] = None
    sprite_manager: Optional[SpriteManager] = None
    
    # Game state
    objects: List[GameObject] = []
    player: Optional[GameObject] = None
    state: Dict[str, Any] = {}
    initial_state: Dict[str, Any] = {}
    
    # Performance tracking
    frame_count = 0
    fps = 0
    last_frame_time = 0
    
    # Configuration
    target_fps = 10
    frame_time = 1.0 / target_fps
    
    @classmethod
    def initialize(cls, lcd_config: LCDConfig = None, input_config: InputConfig = None):
        """Initialize the engine with configuration"""
        if lcd_config is None:
            lcd_config = LCDConfig()
        if input_config is None:
            input_config = InputConfig()
        
        cls.lcd_manager = LCDManager(lcd_config)
        cls.input_manager = InputManager(input_config)
        cls.sprite_manager = SpriteManager()
        
        # Initialize pygame for keyboard input if needed
        if input_config.input_type == InputType.KEYBOARD:
            try:
                import pygame
                pygame.init()
                pygame.display.set_mode((800, 600))
                pygame.display.set_caption("LCD Engine - Keyboard Mode")
            except ImportError:
                logger.error("Pygame not available for keyboard input")
        
        logger.info("Engine initialized successfully")
    
    @classmethod
    def register_sprite(cls, name: str, number: int) -> bool:
        """Register a sprite"""
        if cls.sprite_manager is None:
            logger.error("Engine not initialized")
            return False
        return cls.sprite_manager.register_sprite(name, number)
    
    @classmethod
    def get_joystick(cls) -> JoystickInputs:
        """Get joystick input state"""
        if cls.input_manager is None:
            return JoystickInputs(False, False, False, False)
        return cls.input_manager.get_joystick()
    
    @classmethod
    def get_button_a(cls) -> bool:
        """Get button A state"""
        if cls.input_manager is None:
            return False
        return cls.input_manager.get_button_a()
    
    @classmethod
    def get_button_b(cls) -> bool:
        """Get button B state"""
        if cls.input_manager is None:
            return False
        return cls.input_manager.get_button_b()
    
    @classmethod
    def set_state(cls, state: Dict[str, Any]):
        """Set game state"""
        cls.initial_state = state.copy()
        cls.state = state.copy()
    
    @classmethod
    def set_player(cls, obj: GameObject):
        """Set player object"""
        cls.player = obj
    
    @classmethod
    def new_object(cls, obj: GameObject):
        """Add new game object"""
        cls.objects.append(obj)
    
    @classmethod
    def delete_object(cls, obj: GameObject):
        """Remove game object"""
        if obj in cls.objects:
            cls.objects.remove(obj)
    
    @classmethod
    def get_objects_of(cls, class_type: type) -> List[GameObject]:
        """Get objects of specific type"""
        return [obj for obj in cls.objects if isinstance(obj, class_type)]
    
    @classmethod
    def clear_objects(cls):
        """Clear all game objects"""
        cls.objects.clear()
    
    @classmethod
    def run(cls, game_loop: Callable, max_fps: int = 10):
        """Run the game loop with performance optimization"""
        if cls.lcd_manager is None:
            logger.error("Engine not initialized")
            return
        
        cls.target_fps = max_fps
        cls.frame_time = 1.0 / max_fps
        
        logger.info(f"Starting game loop at {max_fps} FPS")
        
        try:
            cls.lcd_manager.clear()
            running = True
            last_time = time.time()
            
            while running:
                current_time = time.time()
                delta_time = current_time - last_time
                
                # Frame rate control
                if delta_time < cls.frame_time:
                    time.sleep(cls.frame_time - delta_time)
                    continue
                
                # Update frame timing
                cls.fps = 1.0 / delta_time if delta_time > 0 else 0
                cls.frame_count += 1
                last_time = current_time
                
                # Clear LCD
                cls.lcd_manager.clear()
                
                # Run game logic
                try:
                    game_loop()
                except Exception as e:
                    logger.error(f"Error in game loop: {e}")
                
                # Update all objects
                for obj in cls.objects[:]:  # Copy list to avoid modification during iteration
                    if obj.active:
                        obj.update(delta_time)
                
                # Render all objects
                for obj in cls.objects:
                    if obj.visible and 0 <= obj.x < 16 and 0 <= obj.y < 2:
                        char_id = obj.render()
                        if isinstance(char_id, int):
                            cls.lcd_manager.write_char(char_id, obj.y, obj.x)
                
                # Render player
                if cls.player and cls.player.visible and 0 <= cls.player.x < 16 and 0 <= cls.player.y < 2:
                    char_id = cls.player.render()
                    if isinstance(char_id, int):
                        cls.lcd_manager.write_char(char_id, cls.player.y, cls.player.x)
                
                # Check for keyboard quit (in keyboard mode)
                if cls.input_manager and cls.input_manager.config.input_type == InputType.KEYBOARD:
                    import pygame
                    for event in pygame.event.get():
                        if event.type == pygame.QUIT:
                            running = False
                
                # Performance logging every 100 frames
                if cls.frame_count % 100 == 0:
                    logger.debug(f"FPS: {cls.fps:.1f}, Objects: {len(cls.objects)}")
        
        except KeyboardInterrupt:
            logger.info("Game interrupted by user")
        except Exception as e:
            logger.error(f"Game loop error: {e}")
        finally:
            cls.cleanup()
    
    @classmethod
    def reset(cls):
        """Reset game state"""
        cls.state = cls.initial_state.copy()
        cls.objects.clear()
        if cls.player:
            cls.player.x = 0
            cls.player.y = 0
    
    @classmethod
    def cleanup(cls):
        """Clean up engine resources"""
        if cls.lcd_manager:
            cls.lcd_manager.cleanup()
        
        if cls.input_manager and cls.input_manager.config.input_type == InputType.KEYBOARD:
            try:
                import pygame
                pygame.quit()
            except:
                pass
        
        logger.info("Engine cleanup completed")
    
    @classmethod
    def set_backlight(cls, enabled: bool):
        """Control LCD backlight"""
        if cls.lcd_manager:
            cls.lcd_manager.set_backlight(enabled)
    
    @classmethod
    def get_fps(cls) -> float:
        """Get current FPS"""
        return cls.fps
    
    @classmethod
    def get_frame_count(cls) -> int:
        """Get total frame count"""
        return cls.frame_count

# Convenience functions for backward compatibility
def register_sprite(name: str, number: int) -> bool:
    return Engine.register_sprite(name, number)

def get_joystick() -> JoystickInputs:
    return Engine.get_joystick()

def get_button_a() -> bool:
    return Engine.get_button_a()

def get_button_b() -> bool:
    return Engine.get_button_b()

def set_state(state: Dict[str, Any]):
    Engine.set_state(state)

def set_player(obj: GameObject):
    Engine.set_player(obj)

def new_object(obj: GameObject):
    Engine.new_object(obj)

def delete_object(obj: GameObject):
    Engine.delete_object(obj)

def get_objects_of(class_type: type) -> List[GameObject]:
    return Engine.get_objects_of(class_type)

def run(game_loop: Callable, max_fps: int = 10):
    Engine.run(game_loop, max_fps)

def reset():
    Engine.reset()

# Auto-initialize if run directly
if __name__ == "__main__":
    Engine.initialize()
    print("LCD Engine initialized. Use Engine.run() to start a game.")
