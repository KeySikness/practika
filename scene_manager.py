class SceneManager:
    _instance = None

    def __init__(self):
        self.scenes = {}
        self.current_scene = None

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = SceneManager()
        return cls._instance

    def add(self, name, scene):
        self.scenes[name] = scene

    def set_scene(self, name):
        self.current_scene = self.scenes[name]
        if hasattr(self.current_scene, 'on_enter'):
            self.current_scene.on_enter()

    def handle_event(self, event):
        if self.current_scene:
            self.current_scene.handle_event(event)

    def update(self):
        if self.current_scene:
            self.current_scene.update()

    def render(self, screen):
        if self.current_scene:
            self.current_scene.render(screen)