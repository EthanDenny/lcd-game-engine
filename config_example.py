#!/usr/bin/env python3
"""
Example configurations for the Enhanced LCD Engine
Copy and modify these configurations for your specific setup
"""

from lcd_engine import LCDConfig, InputConfig, InputType

# ============================================================================
# LCD CONFIGURATIONS
# ============================================================================

# Standard LCD configuration (most common)
STANDARD_LCD_CONFIG = LCDConfig(
    i2c_address=0x27,      # Most common I2C address
    i2c_port=1,            # I2C port 1 (GPIO2, GPIO3)
    cols=16,               # 16 columns
    rows=2,                # 2 rows
    dotsize=8,             # 8x8 character size
    expander="PCF8574",    # I2C expander type
    charmap='A00',         # Character map
    auto_linebreaks=False, # Disable auto line breaks
    backlight_enabled=True, # Enable backlight
    cursor_visible=False,  # Hide cursor
    blink_enabled=False    # Disable cursor blink
)

# Alternative LCD configuration (if 0x27 doesn't work)
ALTERNATIVE_LCD_CONFIG = LCDConfig(
    i2c_address=0x3F,      # Alternative I2C address
    i2c_port=1,
    cols=16,
    rows=2,
    backlight_enabled=True
)

# Custom LCD configuration (for different displays)
CUSTOM_LCD_CONFIG = LCDConfig(
    i2c_address=0x26,      # Custom I2C address
    i2c_port=1,
    cols=20,               # 20 columns (if your LCD supports it)
    rows=4,                # 4 rows (if your LCD supports it)
    backlight_enabled=True
)

# ============================================================================
# INPUT CONFIGURATIONS
# ============================================================================

# Button input configuration (most common)
BUTTON_INPUT_CONFIG = InputConfig(
    input_type=InputType.BUTTONS,
    # Directional buttons (BCM numbering)
    left_pin=17,
    right_pin=18,
    up_pin=22,
    down_pin=23,
    # Action buttons
    button_a_pin=27,
    button_b_pin=24
)

# Joystick input configuration
JOYSTICK_INPUT_CONFIG = InputConfig(
    input_type=InputType.JOYSTICK,
    # Joystick pins (requires ADC)
    joystick_x_pin=26,
    joystick_y_pin=19,
    joystick_center_pin=13
)

# Keyboard input configuration (for development/testing)
KEYBOARD_INPUT_CONFIG = InputConfig(
    input_type=InputType.KEYBOARD
)

# Minimal button configuration (just action buttons)
MINIMAL_BUTTON_CONFIG = InputConfig(
    input_type=InputType.BUTTONS,
    button_a_pin=27,
    button_b_pin=24
)

# ============================================================================
# USAGE EXAMPLES
# ============================================================================

def example_standard_setup():
    """Example of standard setup with buttons"""
    from lcd_engine import Engine
    
    # Initialize with standard configuration
    Engine.initialize(STANDARD_LCD_CONFIG, BUTTON_INPUT_CONFIG)
    
    # Your game code here
    pass

def example_development_setup():
    """Example of development setup with keyboard input"""
    from lcd_engine import Engine
    
    # Initialize with keyboard input for development
    Engine.initialize(STANDARD_LCD_CONFIG, KEYBOARD_INPUT_CONFIG)
    
    # Your game code here
    pass

def example_auto_detect_setup():
    """Example of setup that tries multiple LCD addresses"""
    from lcd_engine import Engine
    
    # Try different LCD configurations
    lcd_configs = [
        LCDConfig(i2c_address=0x27),
        LCDConfig(i2c_address=0x3F),
        LCDConfig(i2c_address=0x26),
    ]
    
    for config in lcd_configs:
        try:
            Engine.initialize(config, BUTTON_INPUT_CONFIG)
            if Engine.lcd_manager and Engine.lcd_manager.is_connected:
                print(f"LCD connected at address 0x{config.i2c_address:02X}")
                break
        except Exception as e:
            print(f"Failed to connect at 0x{config.i2c_address:02X}: {e}")
            continue

# ============================================================================
# GPIO PIN REFERENCE
# ============================================================================

"""
GPIO Pin Reference (BCM numbering):

Common pins for buttons:
- GPIO 17: Left button
- GPIO 18: Right button  
- GPIO 22: Up button
- GPIO 23: Down button
- GPIO 27: Button A (jump/action)
- GPIO 24: Button B (secondary action)

Common pins for joystick:
- GPIO 26: Joystick X-axis (requires ADC)
- GPIO 19: Joystick Y-axis (requires ADC)
- GPIO 13: Joystick center button

I2C pins (fixed):
- GPIO 2: SDA (I2C data)
- GPIO 3: SCL (I2C clock)

Note: For joystick support, you need an ADC (Analog-to-Digital Converter)
like the MCP3008 connected via SPI.
"""

# ============================================================================
# TROUBLESHOOTING CONFIGURATIONS
# ============================================================================

# Configuration for testing without hardware
TESTING_CONFIG = LCDConfig(
    i2c_address=0x27,
    backlight_enabled=True
)

# Configuration for debugging
DEBUG_CONFIG = LCDConfig(
    i2c_address=0x27,
    backlight_enabled=True,
    cursor_visible=True,  # Show cursor for debugging
    blink_enabled=True    # Enable blink for debugging
)

if __name__ == "__main__":
    print("LCD Engine Configuration Examples")
    print("=" * 40)
    print("This file contains example configurations for the LCD Engine.")
    print("Copy and modify these configurations for your specific setup.")
    print("\nAvailable configurations:")
    print("- STANDARD_LCD_CONFIG: Most common setup")
    print("- BUTTON_INPUT_CONFIG: Standard button setup")
    print("- KEYBOARD_INPUT_CONFIG: For development/testing")
    print("- example_standard_setup(): Complete setup example")
    print("- example_development_setup(): Development setup example") 