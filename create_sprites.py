#!/usr/bin/env python3
"""
Sprite Generator for Space Invaders Game
Creates the necessary sprite assets for the game
"""

from PIL import Image, ImageDraw
import os

def create_sprite(name, pattern, filename):
    """Create a sprite image from a pattern"""
    # Create 5x8 image (LCD character size)
    img = Image.new('RGBA', (5, 8), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # Draw pattern
    for y, row in enumerate(pattern):
        for x, pixel in enumerate(row):
            if pixel:
                draw.point((x, y), fill=(255, 255, 255, 255))
    
    # Save image
    if not os.path.exists('assets'):
        os.makedirs('assets')
    
    img.save(f'assets/{filename}.png')
    print(f"Created {filename}.png")

def main():
    """Create all sprites for Space Invaders"""
    print("Creating Space Invaders sprites...")
    
    # Player ship sprite
    ship_pattern = [
        [0, 0, 1, 0, 0],
        [0, 0, 1, 0, 0],
        [0, 1, 1, 1, 0],
        [0, 1, 1, 1, 0],
        [1, 1, 1, 1, 1],
        [1, 1, 1, 1, 1],
        [0, 1, 1, 1, 0],
        [0, 0, 1, 0, 0]
    ]
    create_sprite("ship", ship_pattern, "ship")
    
    # Alien type 1 sprite
    alien1_pattern = [
        [0, 1, 0, 1, 0],
        [1, 0, 1, 0, 1],
        [0, 1, 1, 1, 0],
        [1, 0, 0, 0, 1],
        [0, 1, 1, 1, 0],
        [0, 0, 1, 0, 0],
        [0, 1, 0, 1, 0],
        [0, 0, 0, 0, 0]
    ]
    create_sprite("alien1", alien1_pattern, "alien1")
    
    # Alien type 2 sprite
    alien2_pattern = [
        [0, 1, 0, 1, 0],
        [1, 0, 1, 0, 1],
        [0, 1, 1, 1, 0],
        [1, 0, 0, 0, 1],
        [0, 1, 1, 1, 0],
        [0, 0, 1, 0, 0],
        [0, 1, 0, 1, 0],
        [0, 0, 0, 0, 0]
    ]
    create_sprite("alien2", alien2_pattern, "alien2")
    
    # Player bullet sprite
    bullet_pattern = [
        [0, 0, 0, 0, 0],
        [0, 0, 1, 0, 0],
        [0, 0, 1, 0, 0],
        [0, 0, 1, 0, 0],
        [0, 0, 1, 0, 0],
        [0, 0, 1, 0, 0],
        [0, 0, 1, 0, 0],
        [0, 0, 0, 0, 0]
    ]
    create_sprite("bullet", bullet_pattern, "bullet")
    
    # Alien bullet sprite
    alien_bullet_pattern = [
        [0, 0, 0, 0, 0],
        [0, 0, 1, 0, 0],
        [0, 1, 1, 1, 0],
        [0, 0, 1, 0, 0],
        [0, 0, 1, 0, 0],
        [0, 1, 1, 1, 0],
        [0, 0, 1, 0, 0],
        [0, 0, 0, 0, 0]
    ]
    create_sprite("alien_bullet", alien_bullet_pattern, "alien_bullet")
    
    # Explosion sprite
    explosion_pattern = [
        [0, 1, 0, 1, 0],
        [1, 0, 1, 0, 1],
        [0, 1, 0, 1, 0],
        [1, 0, 1, 0, 1],
        [0, 1, 0, 1, 0],
        [1, 0, 1, 0, 1],
        [0, 1, 0, 1, 0],
        [0, 0, 0, 0, 0]
    ]
    create_sprite("explosion", explosion_pattern, "explosion")
    
    print("All sprites created successfully!")
    print("Sprites created:")
    print("- ship.png (Player ship)")
    print("- alien1.png (Alien type 1)")
    print("- alien2.png (Alien type 2)")
    print("- bullet.png (Player bullet)")
    print("- alien_bullet.png (Alien bullet)")
    print("- explosion.png (Explosion effect)")

if __name__ == "__main__":
    main() 