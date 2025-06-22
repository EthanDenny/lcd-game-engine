#!/usr/bin/env python3
"""
Space Invaders Game for Enhanced LCD Engine
A complete space shooter game with one playable level
"""

from lcd_engine import Engine, GameObject, LCDConfig, InputConfig, InputType
import random
import math
import time
from typing import Optional, List, Dict, Any, cast

# Initialize the engine with configuration
lcd_config = LCDConfig(
    i2c_address=0x27,  # Will auto-detect if needed
    backlight_enabled=True,
    cursor_visible=False
)

input_config = InputConfig(
    input_type=InputType.BUTTONS,  # Use buttons, will fallback to keyboard if needed
    left_pin=17,
    right_pin=18,
    button_a_pin=27,  # Fire button
    button_b_pin=24   # Pause/restart button
)

# Initialize the engine
Engine.initialize(lcd_config, input_config)

# Register sprites
Engine.register_sprite("ship", 0)      # Player ship
Engine.register_sprite("alien1", 1)    # Alien type 1
Engine.register_sprite("alien2", 2)    # Alien type 2
Engine.register_sprite("bullet", 3)    # Player bullet
Engine.register_sprite("alien_bullet", 4)  # Alien bullet
Engine.register_sprite("explosion", 5) # Explosion effect

class Player(GameObject):
    """Player ship class"""
    
    def __init__(self) -> None:
        super().__init__(8, 1)  # Start in center bottom
        self.speed: float = 2.0
        self.fire_cooldown: float = 0
        self.fire_rate: float = 0.3  # Seconds between shots
        self.lives: int = 3
        self.invulnerable: bool = False
        self.invulnerable_time: float = 0
        self.blink_timer: float = 0
    
    def render(self) -> int:
        if self.invulnerable and int(self.blink_timer * 10) % 2 == 0:
            return 0  # Blink when invulnerable
        return 0  # Ship sprite
    
    def update(self, delta_time: float) -> None:
        # Handle movement
        joystick = Engine.get_joystick()
        if joystick.left and self.x > 0:
            self.x -= self.speed * delta_time * 60
        if joystick.right and self.x < 15:
            self.x += self.speed * delta_time * 60
        
        # Keep player in bounds
        self.x = max(0, min(15, self.x))
        
        # Handle firing
        if self.fire_cooldown > 0:
            self.fire_cooldown -= delta_time
        
        if Engine.get_button_a() and self.fire_cooldown <= 0:
            self.fire_bullet()
            self.fire_cooldown = self.fire_rate
        
        # Update invulnerability
        if self.invulnerable:
            self.invulnerable_time -= delta_time
            self.blink_timer += delta_time
            if self.invulnerable_time <= 0:
                self.invulnerable = False
                self.blink_timer = 0
    
    def fire_bullet(self):
        """Fire a bullet"""
        bullet = PlayerBullet(int(self.x), int(self.y))
        Engine.new_object(bullet)
    
    def take_damage(self):
        """Handle player taking damage"""
        if not self.invulnerable:
            self.lives -= 1
            self.invulnerable = True
            self.invulnerable_time = 2.0  # 2 seconds invulnerability
            return True
        return False

class Alien(GameObject):
    """Alien enemy class"""
    
    def __init__(self, x: int, y: int, alien_type: int = 1) -> None:
        super().__init__(x, y)
        self.alien_type: int = alien_type
        self.speed: float = 0.5
        self.direction: int = 1
        self.move_timer: float = 0
        self.move_interval: float = 1.0  # Move every second
        self.fire_chance: float = 0.01  # 1% chance to fire per frame
        self.points: int = 10 if alien_type == 1 else 20
    
    def render(self) -> int:
        return self.alien_type  # Alien1 or Alien2 sprite
    
    def update(self, delta_time: float) -> None:
        # Movement
        self.move_timer += delta_time
        if self.move_timer >= self.move_interval:
            self.x += self.direction
            self.move_timer = 0
            
            # Check if aliens need to change direction and move down
            aliens = Engine.get_objects_of(Alien)
            edge_hit = False
            
            for alien in aliens:
                if (self.direction > 0 and alien.x >= 15) or (self.direction < 0 and alien.x <= 0):
                    edge_hit = True
                    break
            
            if edge_hit:
                self.direction *= -1
                self.y += 0.5  # Move down
                
                # Check if aliens reached the bottom
                if self.y >= 1:
                    Engine.state["game_over"] = True
        
        # Random firing
        if random.random() < self.fire_chance:
            self.fire_bullet()
    
    def fire_bullet(self):
        """Fire a bullet"""
        bullet = AlienBullet(int(self.x), int(self.y))
        Engine.new_object(bullet)

class PlayerBullet(GameObject):
    """Player bullet class"""
    
    def __init__(self, x, y):
        super().__init__(x, y)
        self.speed = 3.0
        self.active = True
    
    def render(self):
        if not self.active:
            return 0  # Empty space
        return 3  # Bullet sprite
    
    def update(self, delta_time: float) -> None:
        if not self.active:
            return
        
        # Move up
        self.y -= self.speed * delta_time * 60
        
        # Remove if off screen
        if self.y < -1:
            self.active = False
            Engine.delete_object(self)
        
        # Check collision with aliens
        aliens = Engine.get_objects_of(Alien)
        for alien in aliens:
            if (abs(self.x - alien.x) < 0.5 and 
                abs(self.y - alien.y) < 0.5):
                # Hit alien
                self.active = False
                Engine.delete_object(self)
                Engine.delete_object(alien)
                
                # Add points - proper type casting
                alien_obj = cast(Alien, alien)
                Engine.state["score"] += alien_obj.points
                
                # Create explosion
                explosion = Explosion(int(alien.x), int(alien.y))
                Engine.new_object(explosion)
                
                # Check if all aliens destroyed
                remaining_aliens = Engine.get_objects_of(Alien)
                if len(remaining_aliens) == 0:
                    Engine.state["level_complete"] = True
                break

class AlienBullet(GameObject):
    """Alien bullet class"""
    
    def __init__(self, x, y):
        super().__init__(x, y)
        self.speed = 1.5
        self.active = True
    
    def render(self):
        if not self.active:
            return 0  # Empty space
        return 4  # Alien bullet sprite
    
    def update(self, delta_time: float) -> None:
        if not self.active:
            return
        
        # Move down
        self.y += self.speed * delta_time * 60
        
        # Remove if off screen
        if self.y > 2:
            self.active = False
            Engine.delete_object(self)
        
        # Check collision with player
        player = Engine.player
        if player and (abs(self.x - player.x) < 0.5 and 
                      abs(self.y - player.y) < 0.5):
            # Hit player
            self.active = False
            Engine.delete_object(self)
            
            # Cast player to Player type properly
            player_obj = cast(Player, player)
            if player_obj.take_damage():
                # Create explosion
                explosion = Explosion(int(player.x), int(player.y))
                Engine.new_object(explosion)
                
                # Check game over
                if player_obj.lives <= 0:
                    Engine.state["game_over"] = True

class Explosion(GameObject):
    """Explosion effect class"""
    
    def __init__(self, x, y):
        super().__init__(x, y)
        self.lifetime = 0.5  # 0.5 seconds
        self.active = True
    
    def render(self):
        if not self.active:
            return 0  # Empty space
        return 5  # Explosion sprite
    
    def update(self, delta_time):
        if not self.active:
            return
        
        self.lifetime -= delta_time
        if self.lifetime <= 0:
            self.active = False
            Engine.delete_object(self)

class ScoreDisplay(GameObject):
    """Score display object"""
    
    def __init__(self):
        super().__init__(0, 0)
        self.last_score = 0
    
    def render(self):
        return 0  # Handled specially in game loop
    
    def update(self, delta_time):
        pass

def create_alien_formation() -> None:
    """Create the initial alien formation"""
    # Create 3 rows of aliens
    for row in range(3):
        for col in range(8):
            x = col * 2 + 1  # Space aliens out
            y = int(row * 0.5)    # Ensure y is an integer
            alien_type = 1 if row < 2 else 2  # Different types for different rows
            alien = Alien(x, y, alien_type)
            Engine.new_object(alien)

def display_game_info() -> None:
    """Display game information on LCD"""
    if Engine.lcd_manager and Engine.lcd_manager.is_connected:
        player = Engine.player
        if not player:
            return
        
        # Cast player to Player type for type safety
        player_obj = cast(Player, player)
        
        # Display score and lives on top row
        score = Engine.state.get("score", 0)
        lives = player_obj.lives
        
        score_text = f"Score:{score:04d}"
        lives_text = f"Lives:{lives}"
        
        Engine.lcd_manager.write_string(score_text, 0, 0)
        Engine.lcd_manager.write_string(lives_text, 0, 10)
        
        # Display game over or level complete message
        if Engine.state.get("game_over", False):
            Engine.lcd_manager.write_string("GAME OVER", 1, 4)
        elif Engine.state.get("level_complete", False):
            Engine.lcd_manager.write_string("LEVEL COMPLETE!", 1, 2)

def check_game_state() -> None:
    """Check and handle game state changes"""
    # Handle level completion
    if Engine.state.get("level_complete", False):
        if Engine.get_button_b():  # Restart game
            restart_game()
    
    # Handle game over
    if Engine.state.get("game_over", False):
        if Engine.get_button_b():  # Restart game
            restart_game()

def restart_game() -> None:
    """Restart the game"""
    Engine.reset()
    Engine.state.update({
        "score": 0,
        "game_over": False,
        "level_complete": False,
        "paused": False
    })
    
    # Create new player
    player = Player()
    Engine.set_player(player)
    
    # Create alien formation
    create_alien_formation()
    
    # Create score display
    score_display = ScoreDisplay()
    Engine.new_object(score_display)

def game_loop() -> None:
    """Main game loop"""
    # Handle pause/restart
    if Engine.get_button_b():
        if not Engine.state.get("paused", False):
            Engine.state["paused"] = True
        else:
            Engine.state["paused"] = False
    
    # Skip updates if paused
    if Engine.state.get("paused", False):
        return
    
    # Check game state
    check_game_state()
    
    # Update score
    if "score" not in Engine.state:
        Engine.state["score"] = 0

def main() -> None:
    """Main game function"""
    print("Starting Space Invaders...")
    print("Controls:")
    print("- Left/Right: Move ship")
    print("- Button A: Fire")
    print("- Button B: Pause/Restart")
    
    # Set initial game state
    Engine.set_state({
        "score": 0,
        "game_over": False,
        "level_complete": False,
        "paused": False
    })
    
    # Create player
    player = Player()
    Engine.set_player(player)
    
    # Create alien formation
    create_alien_formation()
    
    # Create score display
    score_display = ScoreDisplay()
    Engine.new_object(score_display)
    
    # Custom game loop that includes display updates
    def enhanced_game_loop():
        game_loop()
        display_game_info()
    
    # Run the game
    try:
        Engine.run(enhanced_game_loop, max_fps=15)
    except KeyboardInterrupt:
        print("\nGame stopped by user")
    finally:
        final_score = Engine.state.get("score", 0)
        print(f"Game ended. Final score: {final_score}")

if __name__ == "__main__":
    main() 