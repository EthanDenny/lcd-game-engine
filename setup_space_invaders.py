#!/usr/bin/env python3
"""
Setup script for Space Invaders Game
This script prepares everything needed to run the game
"""

import os
import sys
import subprocess

def check_dependencies():
    """Check if required dependencies are installed"""
    print("Checking dependencies...")
    
    required_packages = [
        'Pillow',
        'RPLCD', 
        'smbus2',
        'numpy',
        'gpiozero'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package.lower().replace('-', '_'))
            print(f"✓ {package}")
        except ImportError:
            print(f"✗ {package} (missing)")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"\nMissing packages: {', '.join(missing_packages)}")
        print("Install them with: pip install -r requirements.txt")
        return False
    
    print("All dependencies are installed!")
    return True

def create_sprites():
    """Create the sprite assets"""
    print("\nCreating sprite assets...")
    
    try:
        # Import and run the sprite creation script
        from create_sprites import main as create_sprites_main
        create_sprites_main()
        return True
    except Exception as e:
        print(f"Error creating sprites: {e}")
        return False

def check_hardware():
    """Check if running on Raspberry Pi with proper hardware"""
    print("\nChecking hardware...")
    
    # Check if running on Raspberry Pi
    try:
        with open('/proc/cpuinfo', 'r') as f:
            if 'Raspberry Pi' in f.read():
                print("✓ Running on Raspberry Pi")
            else:
                print("⚠ Not running on Raspberry Pi (keyboard mode will be used)")
    except:
        print("⚠ Cannot detect hardware (keyboard mode will be used)")
    
    # Check I2C
    try:
        result = subprocess.run(['i2cdetect', '-y', '1'], 
                              capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            print("✓ I2C is available")
            # Look for LCD addresses
            if '27' in result.stdout or '3f' in result.stdout:
                print("✓ LCD detected on I2C bus")
            else:
                print("⚠ No LCD detected on I2C bus")
        else:
            print("✗ I2C not available")
    except:
        print("⚠ Cannot check I2C (keyboard mode will be used)")

def show_instructions():
    """Show setup instructions"""
    print("\n" + "="*50)
    print("SPACE INVADERS SETUP COMPLETE!")
    print("="*50)
    
    print("\n🎮 GAME CONTROLS:")
    print("- Left/Right: Move ship")
    print("- Button A: Fire")
    print("- Button B: Pause/Restart")
    
    print("\n🖥️  HARDWARE SETUP:")
    print("1. Connect LCD to I2C pins (SDA: GPIO2, SCL: GPIO3)")
    print("2. Power LCD (VCC: 5V, GND: Ground)")
    print("3. Connect buttons (optional):")
    print("   - Left: GPIO 17")
    print("   - Right: GPIO 18") 
    print("   - Fire: GPIO 27")
    print("   - Pause: GPIO 24")
    
    print("\n🚀 RUNNING THE GAME:")
    print("1. With hardware: python space_invaders.py")
    print("2. Keyboard mode: The game will automatically use keyboard if no hardware is detected")
    print("   - WASD: Move ship")
    print("   - Space: Fire")
    print("   - Enter: Pause/Restart")
    
    print("\n🔧 TROUBLESHOOTING:")
    print("- If LCD doesn't work, check I2C connection: i2cdetect -y 1")
    print("- If buttons don't work, the game will use keyboard input")
    print("- For development, use keyboard mode for easier testing")
    
    print("\n📁 FILES CREATED:")
    print("- assets/ship.png")
    print("- assets/alien1.png") 
    print("- assets/alien2.png")
    print("- assets/bullet.png")
    print("- assets/alien_bullet.png")
    print("- assets/explosion.png")

def main():
    """Main setup function"""
    print("Space Invaders Game Setup")
    print("="*30)
    
    # Check dependencies
    if not check_dependencies():
        print("\nPlease install missing dependencies first.")
        return False
    
    # Create sprites
    if not create_sprites():
        print("\nFailed to create sprites.")
        return False
    
    # Check hardware
    check_hardware()
    
    # Show instructions
    show_instructions()
    
    print("\n✅ Setup complete! You can now run the game.")
    return True

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nSetup interrupted by user.")
    except Exception as e:
        print(f"\nSetup failed: {e}")
        sys.exit(1) 