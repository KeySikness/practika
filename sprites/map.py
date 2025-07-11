import pygame as py

class Map:
    def __init__(self, map_data):
        self.background = py.image.load(map_data["background"]).convert_alpha()
        self.walls = py.image.load(map_data["walls"]).convert_alpha()

    def draw(self, surface, offset=(0, 0)):
        surface.blit(self.background, offset)
        surface.blit(self.walls, offset)

    def is_walkable(self, x, y):
        w, h = self.background.get_size()
        if 0 <= x < w and 0 <= y < h:
            bg_color = self.background.get_at((x, y))
            wall_color = self.walls.get_at((x, y))
            if bg_color == (0, 0, 0, 255):
                return False
            if wall_color[:3] != (0, 0, 0) and wall_color[3] != 0:  # стена есть
                return False
            return True
        return False
