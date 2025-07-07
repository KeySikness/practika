import pygame as py
import sys
import os

from scene_manager import SceneManager
from src.scenes import character_select
from src.scenes.level_scene import LevelScene
from config import CONSTANTS, LEVELS_DIR
from src.scenes.menu import MainMenuScene
from src.scenes.introduction import IntroductionScene
from src.scenes.controls_guide import ControlsInfoScene


def main():
    py.init()
    screen_config = CONSTANTS["screen"]
    screen_size = (screen_config["width"], screen_config["height"])
    screen = py.display.set_mode(screen_size, py.RESIZABLE)
    py.display.set_caption("Game")
    clock = py.time.Clock()

    scene_manager = SceneManager.get_instance()

    scene_manager.add("main_menu", MainMenuScene(next_scene="introduction"))
    scene_manager.add("introduction", IntroductionScene(next_scene="controls_guide"))
    scene_manager.add("controls_guide", ControlsInfoScene(next_scene="character_select"))
    scene_manager.add("character_select", character_select.CharacterSelect(default_next="level1"))

    for file in os.listdir(LEVELS_DIR):
        if file.endswith(".json"):
            level_id = file.replace(".json", "")
            scene = LevelScene(level_id)
            scene_manager.add(level_id, scene)


    scene_manager.set_scene("main_menu")

    running = True
    while running:
        for event in py.event.get():
            if event.type == py.QUIT:
                running = False
            elif event.type == py.VIDEORESIZE:
                screen_size = event.size
                screen = py.display.set_mode(screen_size, py.RESIZABLE)

            scene_manager.handle_event(event)

        scene_manager.update()
        if hasattr(scene_manager.current_scene, 'update_layout'):
            scene_manager.current_scene.update_layout(screen_size)

        scene_manager.render(screen)
        py.display.flip()
        clock.tick(CONSTANTS["FPS"])

    py.quit()
    sys.exit()

if __name__ == "__main__":
    main()