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
from shaders.shader import Shader
from enum import Enum

# pygame setup
class GameState(Enum):
    START = 1
    LEVEL_SELECTION = 2
    GAME = 3
    GAME_OVER = 4

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


def main(running: bool, shader: Shader):

    # variablen
    selected_level = 0
    sound_manager = SoundManager()
    game_state: GameState = GameState.START
    optionbutton = pg.Rect(120, 70, 80, 40)
    delta = 0.0
    PLAYER_DIED = pg.USEREVENT + 1  # Custom event ID 25 (USEREVENT starts at 24)
    PLAYER_WON = pg.USEREVENT + 2
    clock = pg.time.Clock()

    game_screen = shader.get_game_screen()
    ui_screen = shader.get_ui_screen()

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
            shader.update()
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
                if event.type == PLAYER_DIED:  # Player Died
                    game_state = GameState.GAME_OVER
                elif event.type == PLAYER_WON:  # Player Won
                    unlocked_level = f"{current_level[:-1]}{int(current_level[-1]) + 1}"
                    current_level = unlocked_level
                    write_score(get_path("saves/unlocked_levels.sav"), unlocked_level)
                    game_world = load_world(current_level)
                    clock = pg.time.Clock()
                if event.type == pg.QUIT:
                    running = False
                    sys.exit()

            game_world.do_updates(delta)
            game_world.do_render(game_screen, ui_screen)

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

    pg.quit()
    sys.exit()
