# Example file showing a basic pygame "game loop"
import sys
import pygame as pg
import object_classes
from game_world import GameWorld
import world_generation
from utils import *
from constants import *
from sound_manager import *
import os
from shaders.shader import Shader, FakeShader
from enum import Enum
from title_screen import TitleScreen

# pygame setup
class GameState(Enum):
    START = 1
    LEVEL_SELECTION = 2
    GAME = 3
    GAME_OVER = 4
    IN_GAME_MENU = 5

class In_Game_Menu:
    def __init__(self, settings_filename: str, screen):
        self.screen = screen
        self.value = False
        self.rect = None
        self.image = None
        self.settings = load_settings(settings_filename)
        self.options = list(self.settings.keys())
        print(self.settings)

    def draw_button(self, name, selected_name):
        self.value = self.settings[name]
        if selected_name == name:
            if self.value == "True":
                self.image = TRUE_BUTTON_IMAGE_SELECTED
            else:
                self.image = FALSE_BUTTON_IMAGE_SELECTED
        else:
            if self.value == "True":
                self.image = TRUE_BUTTON_IMAGE
            else:
                self.image = FALSE_BUTTON_IMAGE
        self.image_width = self.image.get_width()
        self.image_height = self.image.get_height()
        self.pos = ((UI_WIDTH - self.image_width) // 2, 10 + (self.options.index(name)) * (self.image_height + 5))
        return self.screen.blit(self.image, self.pos)

    def update(self, name):
        # Hier wird der Wert immer zwischen "True" und "False" gewechselt
        if self.settings[name] == "True":
            self.settings[name] = "False"
        else:
            self.settings[name] = "True"
        return self.settings


def write_score(filename: str, text: str) -> list:
    with open(filename, "r") as file:
        content = file.read()

    if text not in content:
        with open(filename, "a") as file:
            file.write("\n" + text)

def load_score(filename: str) -> list:
    with open(filename, "r") as file:
        scores = [line.rstrip("\n") for line in file]
    return scores

def load_settings(filename: str) -> dict:
    settings = dict()

    with open(filename, 'r') as file:
        for line in file:
            key, value = line.strip().split('=')
            settings[key] = value
    return settings

def update_settings(filename: str, settings: dict):
    with open(filename, 'w') as file:
        for key, value in settings.items():
            file.write(f"{key}={value}\n")

def load_world(level_name: str):
    return world_generation.generate_world(f"{MAP_FOLDER + level_name}.csv")

def availible_levels(filename: str) -> list:
    unlocked_level = load_score(get_path(filename))
    levels: list[str] = []
    for f in os.listdir(get_path(MAP_FOLDER)):
        for level in unlocked_level:
            if f.startswith(level) and f.endswith(".csv") and os.path.isfile(os.path.join(get_path(MAP_FOLDER), f)):
                levels.append(os.path.splitext(f)[0])
    return levels

def display_levels(levels: int, selected_level, screen):
    FONT = pg.font.Font(None, 30)
    for i, option in enumerate(levels):
        color: str = BLUE if i == selected_level else WHITE
        text = FONT.render(option, True, color)
        screen.blit(text, (SCREEN_WIDTH // 2 - text.get_width() // 2, 10 + i * 30))
def get_shader():
    settings = load_settings(get_path(SETTINGS))
    if settings['SHADER'] == "True":
        shader = Shader(SCREEN_WIDTH, SCREEN_HEIGHT)
    elif settings['SHADER'] == "False":
        shader = FakeShader(SCREEN_WIDTH, SCREEN_HEIGHT)
    return shader

def main(running: bool):

    # variablen
    selected_level = 0
    selected_button = 0
    sound_manager = SoundManager()
    game_state: GameState = GameState.START
    optionbutton = pg.Rect(120, 70, 80, 40)
    delta = 0.0
    clock = pg.time.Clock()
    shader = get_shader()
    game_screen = shader.get_game_screen()
    ui_screen = shader.get_ui_screen()
    in_game_menu = In_Game_Menu(SETTINGS, ui_screen)
    was_paused = False

    title_screen: TitleScreen = TitleScreen()

    while running:

        while game_state == GameState.START:

            sound_manager.play_bg_music("menu")
            ui_screen.fill((0, 0, 0))
            if pg.Rect.collidepoint(optionbutton, pg.mouse.get_pos()) == True:
                pg.draw.rect(ui_screen, (255, 255, 255), optionbutton, 50)
            else:
                pg.draw.rect(ui_screen, (0, 255, 255), optionbutton, 50)

            # poll for events
            # pygame.QUIT event means the user clicked X to close your window
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    running = False
                    sys.exit()

                if event.type == pg.KEYDOWN:
                    game_state = GameState.LEVEL_SELECTION

            # !!! Render with shader (use this instead of display.flip()!!!)

            title_screen.do_updates(delta)
            title_screen.do_render(shader)

            shader.update(light_map=title_screen.light_map)
            clock.tick(60)


        while game_state == GameState.LEVEL_SELECTION:

            ui_screen.fill((0, 0, 0))

            levels = availible_levels(get_path("saves/unlocked_levels.sav"))
            display_levels(levels, selected_level, ui_screen)

            for event in pg.event.get():
                if event.type == pg.QUIT:
                    running = False
                    sys.exit()
                elif event.type == pg.KEYDOWN:
                    if event.key == pg.K_DOWN:
                        selected_level = (selected_level + 1) % len(levels)
                        sound_manager.play_system_sound("selection")
                    elif event.key == pg.K_UP:
                        selected_level = (selected_level - 1) % len(levels)
                        sound_manager.play_system_sound("selection")
                    elif event.key == pg.K_RETURN:
                        current_level = levels[selected_level]
                        game_world = load_world(current_level)
                        game_state = GameState.GAME

            # !!! Render with shader (use this instead of display.flip()!!!)
            shader.update()
            clock.tick(60)


        while game_state == GameState.GAME:

            sound_manager.play_bg_music("game")
            for event in pg.event.get():
                if event.type == pg.KEYDOWN:
                    if event.key == pg.K_ESCAPE:
                        game_state = GameState.IN_GAME_MENU
                if event.type == PLAYER_DIED:  # Player Died
                    game_state = GameState.GAME_OVER
                elif event.type == PLAYER_WON:  # Player Won
                    unlocked_level = f"{current_level[:-1]}{int(current_level[-1]) + 1}"
                    current_level = unlocked_level
                    write_score(get_path("saves/unlocked_levels.sav"), unlocked_level)
                    game_world = load_world(current_level)
                    clock = pg.time.Clock()
                elif event.type == DOOR_UNLOCKED:  # unlock door
                    for o in game_world.static_objects:
                        if isinstance(o, object_classes.Door):
                            o.unlock(game_world)
                elif event.type == WORD_LIGHT:  # player collected word 'LIGHT'
                    game_world.on_player_collected_light()
                if event.type == pg.QUIT:
                    running = False
                    sys.exit()

            game_world.do_updates(delta if not was_paused else 0.016)
            game_world.do_render(shader)
            if was_paused:
                was_paused = False

            # !!! Render with shader (use this instead of display.flip()!!!)
            shader.update(game_world.camera_pos, game_world.light_map)

            delta = clock.tick(60) / 1000

        while game_state == GameState.GAME_OVER:
            #screen.fill((0, 0, 0))
            #screen.blit(RESTART_IMAGE, optionbutton)
            for event in pg.event.get():
                if event.type == pg.KEYDOWN:
                    if event.key == pg.K_e:
                        game_world = load_world(current_level)
                        game_state = GameState.GAME
                if event.type == pg.QUIT:
                    running = False
                    sys.exit()

            clock.tick(60)
        while game_state == GameState.IN_GAME_MENU:
            was_paused = True
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    running = False
                    sys.exit()
                elif event.type == pg.KEYDOWN:
                    if event.key == pg.K_DOWN:
                        selected_button = (selected_button + 1) % (len(in_game_menu.options))
                        sound_manager.play_system_sound("selection")
                    elif event.key == pg.K_UP:
                        selected_button = (selected_button - 1) % (len(in_game_menu.options))
                        sound_manager.play_system_sound("selection")
                    elif event.key == pg.K_RETURN:

                        update_settings(SETTINGS, in_game_menu.update(in_game_menu.options[selected_button]))
                        print(in_game_menu.settings)
                        sound_manager.play_bg_music("menu")
                        sound_manager.play_system_sound("selection")
                        for keys in in_game_menu.settings.keys():
                            in_game_menu.draw_button(keys, in_game_menu.options[selected_button])
                    elif event.key == pg.K_ESCAPE:
                        game_state = GameState.GAME

            ui_screen.fill((30, 30, 30))
            for keys in in_game_menu.settings.keys():
                in_game_menu.draw_button(keys,in_game_menu.options[selected_button])

            shader.update()



    pg.quit()
    sys.exit()
