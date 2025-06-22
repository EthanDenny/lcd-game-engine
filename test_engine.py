#!/usr/bin/env python3
"""
Test script for the Enhanced LCD Engine
Tests various features and configurations
"""

import time
import sys
from lcd_engine import Engine, GameObject, LCDConfig, InputConfig, InputType

def test_lcd_connection():
    """Test LCD connection and basic functionality"""
    print("Testing LCD connection...")
    
    # Try different configurations
    configs = [
        LCDConfig(i2c_address=0x27),
        LCDConfig(i2c_address=0x3F),
        LCDConfig(i2c_address=0x26),
    ]
    
    for config in configs:
        try:
            Engine.initialize(config, InputConfig(input_type=InputType.KEYBOARD))
            if Engine.lcd_manager and Engine.lcd_manager.is_connected:
                print(f"✓ LCD connected successfully at address 0x{config.i2c_address:02X}")
                return True
        except Exception as e:
            print(f"✗ Failed to connect at address 0x{config.i2c_address:02X}: {e}")
    
    print("✗ No LCD connection found")
    return False

def test_sprite_loading():
    """Test sprite loading functionality"""
    print("Testing sprite loading...")
    
    try:
        # Test sprite registration
        sprites = ["dino", "cactus", "rock", "bird"]
        for i, sprite in enumerate(sprites):
            success = Engine.register_sprite(sprite, i)
            if success:
                print(f"✓ Sprite '{sprite}' loaded successfully")
            else:
                print(f"✗ Failed to load sprite '{sprite}'")
        
        return True
    except Exception as e:
        print(f"✗ Sprite loading error: {e}")
        return False

def test_input_system():
    """Test input system functionality"""
    print("Testing input system...")
    
    try:
        # Test joystick input
        joystick = Engine.get_joystick()
        print(f"✓ Joystick input working: {joystick}")
        
        # Test button input
        button_a = Engine.get_button_a()
        button_b = Engine.get_button_b()
        print(f"✓ Button input working: A={button_a}, B={button_b}")
        
        return True
    except Exception as e:
        print(f"✗ Input system error: {e}")
        return False

def test_game_object_system():
    """Test GameObject system"""
    print("Testing GameObject system...")
    
    try:
        class TestObject(GameObject):
            def __init__(self):
                super().__init__(1, 1)
                self.test_value: int = 42
            
            def render(self):
                return 0
            
            def update(self, delta_time):
                self.test_value += 1
        
        # Create and test object
        obj = TestObject()
        Engine.new_object(obj)
        
        # Test object management
        objects = Engine.get_objects_of(TestObject)
        if len(objects) == 1:
            test_obj = objects[0]  # type: TestObject
            if test_obj.test_value == 42:
                print("✓ GameObject system working")
                
                # Test object removal
                Engine.delete_object(obj)
                objects = Engine.get_objects_of(TestObject)
                if len(objects) == 0:
                    print("✓ Object removal working")
                    return True
        
        print("✗ GameObject system test failed")
        return False
        
    except Exception as e:
        print(f"✗ GameObject system error: {e}")
        return False

def test_state_management():
    """Test state management system"""
    print("Testing state management...")
    
    try:
        # Set initial state
        initial_state = {"score": 0, "lives": 3, "level": 1}
        Engine.set_state(initial_state)
        
        # Modify state
        Engine.state["score"] = 100
        Engine.state["lives"] = 2
        
        # Test state persistence
        if (Engine.state["score"] == 100 and 
            Engine.state["lives"] == 2 and 
            Engine.state["level"] == 1):
            print("✓ State management working")
            
            # Test reset
            Engine.reset()
            if (Engine.state["score"] == 0 and 
                Engine.state["lives"] == 3 and 
                Engine.state["level"] == 1):
                print("✓ State reset working")
                return True
        
        print("✗ State management test failed")
        return False
        
    except Exception as e:
        print(f"✗ State management error: {e}")
        return False

def test_performance():
    """Test performance monitoring"""
    print("Testing performance monitoring...")
    
    try:
        # Test FPS tracking
        fps = Engine.get_fps()
        frame_count = Engine.get_frame_count()
        
        print(f"✓ Performance monitoring working: FPS={fps:.1f}, Frames={frame_count}")
        return True
        
    except Exception as e:
        print(f"✗ Performance monitoring error: {e}")
        return False

def run_simple_demo():
    """Run a simple demo to test the engine"""
    print("Running simple demo...")
    
    try:
        # Create a simple moving object
        class DemoObject(GameObject):
            def __init__(self):
                super().__init__(0, 0)
                self.direction = 1
            
            def render(self):
                return 0  # Use dino sprite
            
            def update(self, delta_time):
                self.x += self.direction * 0.5
                if self.x >= 15 or self.x <= 0:
                    self.direction *= -1
        
        # Setup demo
        Engine.set_player(DemoObject())
        Engine.set_state({"demo_time": 0})
        
        def demo_loop():
            Engine.state["demo_time"] += 1
            if Engine.state["demo_time"] > 100:  # Run for ~10 seconds
                return False  # Stop demo
        
        # Run demo
        print("Demo running for 10 seconds...")
        Engine.run(demo_loop, max_fps=10)
        print("✓ Demo completed successfully")
        return True
        
    except Exception as e:
        print(f"✗ Demo error: {e}")
        return False

def main():
    """Main test function"""
    print("Enhanced LCD Engine Test Suite")
    print("=" * 40)
    
    tests = [
        ("LCD Connection", test_lcd_connection),
        ("Sprite Loading", test_sprite_loading),
        ("Input System", test_input_system),
        ("GameObject System", test_game_object_system),
        ("State Management", test_state_management),
        ("Performance Monitoring", test_performance),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n{test_name}:")
        try:
            if test_func():
                passed += 1
        except Exception as e:
            print(f"✗ {test_name} failed with exception: {e}")
    
    print(f"\n{'=' * 40}")
    print(f"Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("✓ All tests passed! Engine is working correctly.")
        
        # Run demo if all tests pass
        print("\nRunning demo...")
        run_simple_demo()
    else:
        print("✗ Some tests failed. Please check your setup.")
        sys.exit(1)
    
    # Cleanup
    try:
        Engine.cleanup()
        print("✓ Engine cleanup completed")
    except:
        pass

if __name__ == "__main__":
    main() 