import pygame as pg
from constants import *
from utils import *

def load_settings(filename: str) -> dict:
    settings = dict()

    with open(filename, 'r') as file:
        for line in file:
            key, value = line.strip().split('=')
            settings[key] = value
    return settings

class SoundManager:
    def __init__(self):
        pg.mixer.init()
        self.current_bg_music = None
        self.current_menu_state = None
        self.current_movement_sound = None
        self.current_movement = None
        self.current_system_sound = None
    def play_bg_music(self, menu_state):
        self.settings = load_settings(SETTINGS)
        if self.current_menu_state == menu_state and self.settings["MUSIC"] == "True":
            self.current_bg_music.set_volume(1)
            return
        elif self.settings["MUSIC"] == "False":
            if self.current_bg_music:
                self.current_bg_music.set_volume(0)
        else:
            if self.current_bg_music:
                self.current_bg_music.fadeout(1500)
            self.current_menu_state = menu_state

            self.current_bg_music = BG_MUSIC.get(menu_state)
            if self.settings["MUSIC"] == "False":
                self.current_bg_music.set_volume(0)
            elif self.settings["MUSIC"] == "True":
                self.current_bg_music.set_volume(1)

            self.current_bg_music.play(loops=-1)



    def play_movement_sound(self, movement_name):
        self.settings = load_settings(SETTINGS)
        if self.current_movement == movement_name and self.settings["SFX"] == "True":
            self.current_movement_sound.set_volume(0.5)
            return
        elif self.settings["SFX"] == "False":
            if self.current_movement_sound:
                self.current_movement_sound.set_volume(0)
        else:

            for key, value in PLAYER_SOUNDS.items():
                if value:
                    value.fadeout(100)

            self.current_movement = movement_name
            self.current_movement_sound = PLAYER_SOUNDS.get(movement_name)

            if self.current_movement_sound:
                self.current_movement_sound.play(loops=-1)

    def play_system_sound(self, system_sound_name):
        self.settings = load_settings(SETTINGS)

        if self.current_system_sound:
            self.current_system_sound.stop()

        self.current_system_sound = SYSTEM_SOUNDS.get(system_sound_name)

        if self.settings["SFX"] == "True":
            self.current_system_sound.set_volume(0.5)
        elif self.settings["SFX"] == "False":
            self.current_system_sound.set_volume(0)

        self.current_system_sound.play()



