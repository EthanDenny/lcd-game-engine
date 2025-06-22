# Enhanced LCD Game Engine for Raspberry Pi 4B

A powerful and robust game engine designed specifically for 16x2 LCD displays connected to Raspberry Pi 4B via I2C. This engine provides a complete framework for creating retro-style games with modern development features.

## 🚀 Key Improvements Over Original

### 🔧 **Robust Error Handling**
- **Auto-detection**: Automatically finds LCD at common I2C addresses (0x27, 0x3F, 0x26, 0x25)
- **Graceful fallbacks**: Falls back to keyboard input if GPIO hardware isn't available
- **Comprehensive logging**: Detailed logging for debugging and monitoring
- **Resource management**: Proper cleanup of resources on exit

### ⚡ **Performance Optimizations**
- **Frame rate control**: Configurable FPS with proper timing
- **Efficient rendering**: Smart frame buffer management
- **Memory optimization**: Reduced memory footprint and garbage collection
- **Delta time**: Smooth animations independent of frame rate

### 🎮 **Enhanced Input System**
- **Multiple input types**: Support for buttons, joystick, and keyboard
- **Configurable GPIO pins**: Easy pin assignment for different hardware setups
- **Input abstraction**: Clean API that works with any input method
- **Debouncing**: Built-in input debouncing for reliable button presses

### 🎨 **Advanced Sprite Management**
- **Improved sprite loading**: Better PNG to LCD character conversion
- **Sprite caching**: Efficient memory usage for repeated sprites
- **Custom character support**: Up to 8 custom characters per game
- **Error handling**: Graceful handling of missing sprite files

### 🏗️ **Modern Architecture**
- **Type hints**: Full type annotation for better development experience
- **Configuration classes**: Clean, typed configuration system
- **Modular design**: Separated concerns for LCD, input, and sprite management
- **Backward compatibility**: Works with existing game code

## 📋 Requirements

### Hardware
- Raspberry Pi 4B (or compatible)
- 16x2 LCD display with I2C interface (PCF8574 or similar)
- Optional: GPIO buttons or joystick for input

### Software
```bash
pip install -r requirements.txt
```

## 🛠️ Installation

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd lcd-game-engine
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Connect your LCD**:
   - Connect LCD to I2C pins (SDA: GPIO2, SCL: GPIO3)
   - Power the LCD (VCC: 5V, GND: Ground)

4. **Test the connection**:
   ```bash
   python lcd_engine.py
   ```

## 🎯 Quick Start

### Basic Game Setup

```python
from lcd_engine import Engine, GameObject, LCDConfig, InputConfig, InputType

# Configure the engine
lcd_config = LCDConfig(
    i2c_address=0x27,  # Will auto-detect if needed
    backlight_enabled=True
)

input_config = InputConfig(
    input_type=InputType.BUTTONS,
    button_a_pin=27,
    button_b_pin=24
)

# Initialize the engine
Engine.initialize(lcd_config, input_config)

# Register sprites
Engine.register_sprite("player", 0)
Engine.register_sprite("enemy", 1)

# Create game objects
class Player(GameObject):
    def __init__(self):
        super().__init__(1, 1)
    
    def render(self):
        return 0  # Player sprite
    
    def update(self, delta_time):
        # Handle input
        if Engine.get_button_a():
            self.x += 1
        if Engine.get_button_b():
            self.x -= 1

# Game loop
def game_loop():
    # Your game logic here
    pass

# Run the game
Engine.set_player(Player())
Engine.run(game_loop, max_fps=10)
```

### Advanced Configuration

```python
# Custom LCD configuration
lcd_config = LCDConfig(
    i2c_address=0x3F,      # Custom I2C address
    i2c_port=1,            # I2C port
    cols=16,               # Display columns
    rows=2,                # Display rows
    backlight_enabled=True,
    cursor_visible=False,
    blink_enabled=False
)

# Joystick input configuration
input_config = InputConfig(
    input_type=InputType.JOYSTICK,
    joystick_x_pin=26,
    joystick_y_pin=19,
    joystick_center_pin=13
)

# Keyboard input (for development)
input_config = InputConfig(
    input_type=InputType.KEYBOARD
)
```

## 🎮 Game Development Features

### GameObject System
```python
class MyGameObject(GameObject):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.visible = True
        self.active = True
    
    def render(self) -> int:
        return 0  # Return sprite number
    
    def update(self, delta_time: float):
        # Update logic here
        pass
    
    def on_collision(self, other: GameObject):
        # Handle collisions
        pass
```

### Input Handling
```python
# Get joystick state
joystick = Engine.get_joystick()
if joystick.left:
    player.x -= 1
if joystick.right:
    player.x += 1

# Get button states
if Engine.get_button_a():
    player.jump()
if Engine.get_button_b():
    player.attack()
```

### Object Management
```python
# Add objects
Engine.new_object(Enemy(10, 1))

# Remove objects
Engine.delete_object(enemy)

# Get objects by type
enemies = Engine.get_objects_of(Enemy)

# Clear all objects
Engine.clear_objects()
```

### State Management
```python
# Set game state
Engine.set_state({
    "score": 0,
    "lives": 3,
    "level": 1
})

# Access state
score = Engine.state["score"]
Engine.state["score"] += 10

# Reset to initial state
Engine.reset()
```

## 🔧 Configuration Options

### LCDConfig
- `i2c_address`: I2C address (default: 0x27)
- `i2c_port`: I2C port (default: 1)
- `cols`: Display columns (default: 16)
- `rows`: Display rows (default: 2)
- `backlight_enabled`: Enable backlight (default: True)
- `cursor_visible`: Show cursor (default: False)
- `blink_enabled`: Enable cursor blink (default: False)

### InputConfig
- `input_type`: Input type (BUTTONS, JOYSTICK, KEYBOARD)
- `left_pin`, `right_pin`, `up_pin`, `down_pin`: GPIO pins for directional buttons
- `button_a_pin`, `button_b_pin`: GPIO pins for action buttons
- `joystick_x_pin`, `joystick_y_pin`, `joystick_center_pin`: GPIO pins for joystick

## 🎯 Example Games

### Enhanced Dino Game (`dino_enhanced.py`)
- Improved physics with gravity and jumping
- Multiple obstacle types
- Score display and lives system
- Collision detection with invulnerability
- Game over and restart functionality

### Space Invaders (`space-pi-invaders/`)
- Classic space shooter gameplay
- Multiple enemy types
- Bullet system
- Score tracking

## 🐛 Troubleshooting

### LCD Not Detected
1. Check I2C connection: `i2cdetect -y 1`
2. Verify power supply to LCD
3. Check I2C address in configuration
4. Engine will auto-detect common addresses

### Input Not Working
1. Check GPIO pin assignments
2. Verify button connections
3. Use keyboard mode for testing: `InputType.KEYBOARD`
4. Check permissions for GPIO access

### Performance Issues
1. Reduce frame rate: `Engine.run(game_loop, max_fps=5)`
2. Limit number of game objects
3. Use efficient collision detection
4. Monitor FPS: `Engine.get_fps()`

### Sprite Issues
1. Ensure PNG files are in `assets/` directory
2. Check sprite dimensions (5x8 pixels recommended)
3. Verify sprite registration order
4. Use transparent backgrounds in PNG files

## 📊 Performance Monitoring

```python
# Get current FPS
fps = Engine.get_fps()
print(f"Current FPS: {fps:.1f}")

# Get frame count
frames = Engine.get_frame_count()
print(f"Total frames: {frames}")

# Control backlight
Engine.set_backlight(False)  # Turn off backlight
```

## 🔄 Backward Compatibility

The enhanced engine maintains compatibility with existing games:

```python
# Old code still works
from lcd_engine import Engine

Engine.register_sprite("sprite", 0)
# ... rest of your existing code
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- Original LCD engine creators
- RPLCD library developers
- Raspberry Pi community
- All contributors and testers

---

**Happy gaming on your LCD display! 🎮📺** 