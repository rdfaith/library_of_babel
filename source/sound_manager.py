from time import sleep

import pygame as pg
from constants import *


class SoundManager:
    def __init__(self):
        pg.mixer.init()
        self.current_bg_music = None
        self.current_menu_state = None
        self.current_movement_sound = None
        self.current_movement = None
        self.current_system_sound = None

    def play_bg_music(self, menu_state):
        if self.current_menu_state == menu_state:
            return
        if self.current_bg_music:
            self.current_bg_music.fadeout(1500)
        self.current_menu_state = menu_state

        self.current_bg_music = BG_MUSIC.get(menu_state)

        (self.current_bg_music.play(loops=-1))
        if DEBUG_MODE:
            self.current_bg_music.set_volume(0)
        else:
            self.current_bg_music.set_volume(1)

    def play_movement_sound(self, movement_name):
        if movement_name == self.current_movement:
            return

        for key, value in PLAYER_SOUNDS.items():
            if value:
                value.fadeout(100)

        self.current_movement = movement_name
        self.current_movement_sound = PLAYER_SOUNDS.get(movement_name)

        if self.current_movement_sound:
            self.current_movement_sound.play(loops=-1)
            self.current_movement_sound.set_volume(0.5)
    def play_system_sound(self, system_sound_name):
        if self.current_system_sound:
            self.current_system_sound.stop()

        self.current_system_sound = SYSTEM_SOUNDS.get(system_sound_name)

        self.current_system_sound.play()
        self.current_system_sound.set_volume(0.5)



