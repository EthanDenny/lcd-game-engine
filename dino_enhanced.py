#!/usr/bin/env python3
"""
Enhanced Dino Game for LCD Engine
Demonstrates the improved engine features
"""

from lcd_engine import Engine, GameObject, LCDConfig, InputConfig, InputType
import random
import time

# Initialize the engine with configuration
lcd_config = LCDConfig(
    i2c_address=0x27,  # Try 0x27 first, will auto-detect if needed
    backlight_enabled=True,
    cursor_visible=False
)

input_config = InputConfig(
    input_type=InputType.BUTTONS,  # Use buttons, will fallback to keyboard if needed
    left_pin=17,
    right_pin=18,
    button_a_pin=27,
    button_b_pin=24
)

# Initialize the engine
Engine.initialize(lcd_config, input_config)

# Register sprites
Engine.register_sprite("dino", 0)
Engine.register_sprite("cactus", 1)
Engine.register_sprite("rock", 2)
Engine.register_sprite("bird", 3)

class Player(GameObject):
    """Enhanced player class with better physics"""
    
    def __init__(self):
        super().__init__(1, 1)  # Start at bottom left
        self.jump_time: float = 0
        self.jump_velocity: float = 0
        self.gravity: float = 0.3
        self.jump_power: float = 0.8
        self.on_ground: bool = True
        self.invulnerable: bool = False
        self.invulnerable_time: float = 0
    
    def render(self) -> int:
        return 0  # Dino sprite
    
    def update(self, delta_time: float) -> None:
        # Handle jumping
        if Engine.get_button_a() and self.on_ground:
            self.jump_velocity = self.jump_power
            self.on_ground = False
        
        # Apply gravity
        if not self.on_ground:
            self.jump_velocity -= self.gravity * delta_time * 60  # Scale for 60 FPS
        
        # Update position
        new_y = 1 - self.jump_velocity
        
        # Ground collision
        if new_y >= 1:
            new_y = 1
            self.jump_velocity = 0
            self.on_ground = True
        
        # Update position
        self.y = new_y
        
        # Update invulnerability
        if self.invulnerable:
            self.invulnerable_time -= delta_time
            if self.invulnerable_time <= 0:
                self.invulnerable = False
    
    def on_collision(self, other):
        if not self.invulnerable:
            self.invulnerable = True
            self.invulnerable_time = 2.0  # 2 seconds of invulnerability
            return True
        return False

class Obstacle(GameObject):
    """Enhanced obstacle class with different types"""
    
    def __init__(self, obstacle_type=None):
        if obstacle_type is None:
            obstacle_type = random.choice(["cactus", "rock", "bird"])
        
        self.obstacle_type = obstacle_type
        y_pos = 0 if obstacle_type == "bird" else 1
        super().__init__(15, y_pos)  # Start at right side
        
        self.speed: float = 2.0  # Speed in cells per second
        self.active: bool = True
    
    def render(self) -> int:
        if not self.active:
            return 0  # Empty space
        
        match self.obstacle_type:
            case "cactus":
                return 1
            case "rock":
                return 2
            case "bird":
                return 3
            case _:
                return 0
    
    def update(self, delta_time: float) -> None:
        if self.active:
            # Move left
            new_x = self.x - self.speed * delta_time * 60  # Scale for 60 FPS
            
            # Remove if off screen
            if new_x < -1:
                self.active = False
                Engine.delete_object(self)
            else:
                self.x = new_x

class ScoreDisplay(GameObject):
    """Score display object"""
    
    def __init__(self):
        super().__init__(0, 0)
        self.score = 0
        self.high_score = 0
        self.last_update = 0
    
    def render(self):
        return 0  # This will be handled specially in the game loop
    
    def update(self, delta_time):
        # Update score every second
        self.last_update += delta_time
        if self.last_update >= 1.0:
            self.score += 1
            self.last_update = 0
            
            if self.score > self.high_score:
                self.high_score = self.score

def check_collisions():
    """Check for collisions between player and obstacles"""
    player = Engine.player
    if not player:
        return
    
    for obstacle in Engine.get_objects_of(Obstacle):
        if (abs(player.lcd_x - obstacle.lcd_x) < 1 and 
            abs(player.lcd_y - obstacle.lcd_y) < 1 and 
            obstacle.active):
            
            if player.on_collision(obstacle):
                # Player hit, reset game
                Engine.state["lives"] -= 1
                if Engine.state["lives"] <= 0:
                    # Game over
                    Engine.state["game_over"] = True
                    Engine.state["final_score"] = Engine.state["score"]
                else:
                    # Remove all obstacles and continue
                    for obj in Engine.get_objects_of(Obstacle):
                        Engine.delete_object(obj)
                    Engine.state["obstacle_timer"] = 0

def game_loop():
    """Main game loop"""
    # Skip updates if game over
    if Engine.state.get("game_over", False):
        if Engine.get_button_b():  # Restart game
            Engine.reset()
            Engine.state["lives"] = 3
            Engine.state["score"] = 0
            Engine.state["game_over"] = False
            Engine.state["final_score"] = 0
            Engine.state["obstacle_timer"] = 60  # Reset timer
            Engine.set_player(Player())
        return

    # Update score every 10 frames
    if Engine.get_frame_count() % 10 == 0:
        Engine.state["score"] = Engine.state.get("score", 0) + 1
    
    # Spawn obstacles
    if Engine.state["obstacle_timer"] <= 0:
        # Spawn rate increases with score
        spawn_rate = max(20, 60 - Engine.state["score"] // 10)
        Engine.state["obstacle_timer"] = spawn_rate
        
        # Spawn obstacle
        Engine.new_object(Obstacle())
    
    Engine.state["obstacle_timer"] -= 1
    
    # Check collisions
    check_collisions()

def display_score():
    """Display score on LCD"""
    if Engine.lcd_manager and Engine.lcd_manager.is_connected:
        # Clear the top row first
        Engine.lcd_manager.write_string(" " * 16, 0, 0)
        
        score = Engine.state.get("score", 0)
        lives = Engine.state.get("lives", 3)
        
        # Display score on top row (left-aligned)
        score_text = f"Score:{score:04d}"
        Engine.lcd_manager.write_string(score_text, 0, 0)
        
        # Display lives on top row (right-aligned)
        lives_text = f"Lives:{lives}"
        Engine.lcd_manager.write_string(lives_text, 0, 16 - len(lives_text))
        
        # Display game over message if needed
        if Engine.state.get("game_over", False):
            # Clear the bottom row first
            Engine.lcd_manager.write_string(" " * 16, 1, 0)
            
            final_score = Engine.state.get("final_score", 0)
            game_over_text = "GAME OVER"
            Engine.lcd_manager.write_string(game_over_text, 1, (16 - len(game_over_text)) // 2)  # Center text

def main():
    """Main game function"""
    print("Starting Enhanced Dino Game...")
    print("Controls: Button A to jump, Button B to restart")
    
    # Set initial game state
    Engine.set_state({
        "score": 0,
        "lives": 3,
        "obstacle_timer": 60,  # Initial delay before first obstacle
        "game_over": False,
        "final_score": 0
    })
    
    # Create player
    player = Player()
    Engine.set_player(player)
    
    # Create score display
    score_display = ScoreDisplay()
    Engine.new_object(score_display)
    
    # Custom game loop that includes score display
    def enhanced_game_loop():
        game_loop()
        display_score()
    
    # Run the game
    try:
        Engine.run(enhanced_game_loop, max_fps=10)
    except KeyboardInterrupt:
        print("\nGame stopped by user")
    finally:
        print("Game ended. Final score:", Engine.state.get("final_score", 0))

if __name__ == "__main__":
    main() 