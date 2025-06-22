# lcd-game-engine

Tiny games on tiny hardware.

## What is this?

During the 2025 [DO I.T. Hackathon](https://ecumene.github.io/dontoverthinkit/), we were encouraged to think about how hardware could be a solution to real-world problems. To that end, we decided to build a miniature game console, complete with a 16x2 LCD screen, button and joystick inputs, 1-channel sound, and am emulator for local development and testing.

This project is aimed at budding game developers, hackers, programmers, and thinkers; as well as those who educate them. It provides a safe, fun, and accessible platform to get started building with hardware, and to explore both Python and Raspberry Pi development

## What parts do I need?

TODO

## How can I make a game?

Start by checking out the two examples, `dino.py` and `rpg.py`. The dino game recreates the classic Google Chrome "no connection" experience, while the RPG gives a small taste of how the joystick can be used for moving a character around the screen.

`lcd_engine.py` and `py_engine.py` both export an `Engine` class. The one you import will be dependent on your environment:

- For local development, use the emulator in `py_engine.py`
- Once your game is working, run it on the Pi with `lcd_engine.py`

The `core` module provides `GameObject`, the base class for all other objects rendered in the game. Provides two variables, `x` and `y`, as well as a primitive render function, which should be replaced. Either ASCII characters (as srings) or custom sprites (as numbers, see below) can be rendered.

The `Engine` class provides the following ways to interact with the emulator or console:

- `register_sprite(name, number)` - The console is limited to 8 unique, non-ASCII sprites. This function will load `assets/{name}.png`, and map it to the numbers 0-7 in the render function.
- `get_joystick()` - Returns an object with booleans `left`, `right`, `up`, and `down`, allowing for 8-directional input.
- `get_button_a()` - Returns a boolean depending on the state of the A button.
- `get_button_a()` - Same as above, but for the B button.
- `set_state(state)` - Accepts a dictionary of values, accessible through `engine.state[...]`. Convenient for global variables that need to reset to some intial value when the game resets, and for keeping code concise (creates a copy).
- `set_player(obj)`- Set the "player", a special object accessible more directly through `engine.player` (creates a copy).
- `new_object(obj)` - Create a new object (creates a copy).
- `delete_object(obj)` - Delete the provided object (by reference).
- `get_objects_of(class_name)` - Returns all objects that are instances of the given class.
- `run(loop)` - Starts the game. `loop()` is a function that defines the game's logic.
- `reset()` - Resets the engine's `player` and `state` to their initial values and `objects` to empty.

### How can I assemble it?

## Contributors

This was very much a group effort, put together by many talented souls:

- Ethan (https://github.com/EthanDenny)
- Farhan Probandho (https://github.com/farhanprobandho)
- Farhan Reaz (https://github.com/farhanhaseen22)
- Som (https://github.com/som-sinha)
- Ripudaman (https://github.com/singhripudaman)
- Rowan (https://github.com/dunningkrugerkid)
