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


class GameObject:
    x = 0
    y = 0

    def __init__(self, x=0, y=0):
        self.x = x
        self.y = y

    def render(self):
        return "?"


class Core:
    player = None
    state = initial_state = None
    objects = []

    def reset(self):
        self.player = self.player_class()
        self.state = self.initial_state.copy()
        self.objects = []

    def set_state(self, state):
        self.initial_state = state.copy()
        self.state = state.copy()

    def set_player(self, class_name):
        self.player_class = class_name
        self.player = class_name()

    def new_object(self, obj):
        self.objects.append(obj)

    def delete_object(self, obj):
        self.objects = [o for o in self.objects if o != obj]

    def get_objects_of(self, class_name):
        return [obj for obj in self.objects if isinstance(obj, class_name)]
