import pygame as py
import random
import os

class AudioManager:
    _instance = None

    def __init__(self):
        py.mixer.init()
        py.mixer.music.set_volume(0.1)
        self.current_track = None
        self.base_path = os.path.join("assets", "audio")
        self.tracks = {
            "menu": os.path.join(self.base_path, "menu.mp3"),
            "ambient": os.path.join(self.base_path, "ambient.mp3"),
            "level": [
                os.path.join(self.base_path, "1.mp3"),
                os.path.join(self.base_path, "2.mp3"),
                os.path.join(self.base_path, "3.mp3")
            ]
        }

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = AudioManager()
        return cls._instance

    def play_music(self, track, loop=-1):
        if self.current_track == track:
            return
        self.stop_music()

        if not os.path.exists(track):
            raise FileNotFoundError(f"ФАЙЛА НЕТ ДУРА: {track}")

        py.mixer.music.load(track)
        py.mixer.music.play(loop)
        self.current_track = track

    def play_random_level_music(self):
        track = random.choice(self.tracks["level"])
        self.play_music(track)
        return track

    def stop_music(self):
        py.mixer.music.stop()
        self.current_track = None

    def fadeout_music(self, duration_ms):
        py.mixer.music.fadeout(duration_ms)
        self.current_track = None
