# Example file showing a basic pygame "game loop"
import pygame as pg
import object_classes
from game_world import GameWorld
import world_generation
from utils import *
from constants import *
from sound_manager import *
import os
from menus import *
import shaders.shader as shader

# pygame setup
pg.init()

game_screen = pg.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
light_source_screen = pg.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
ui_screen = pg.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))

shader = shader.Shader(SCREEN_WIDTH, SCREEN_HEIGHT, game_screen, ui_screen, light_source_screen)

running = True
delta = 0.0
menu = True
game = False
level_unloaded = False
level_selection = False
game_over = False
selected_level = 0  # Index der ausgewählten Option
pause_image = pg.image.load(get_path('assets/test/pause_test.png'))
FONT = pg.font.Font(None, 30)
sound_manager = SoundManager()
optionbutton = pg.Rect(120,70,80,40)

# create player character
#obstacle = object_classes.GameObject(pygame.Vector2(200, 100), pygame.image.load(get_path('assets/test/egg.png')))
#floor = object_classes.GameObject(pygame.Vector2(0, 148), pygame.image.load(get_path('assets/test/floor.png')))
#worm = object_classes.Worm(pygame.Vector2(140, 100), pygame.image.load(get_path('assets/test/worm.png')), True)
#game_world = GameWorld([], [obstacle, floor], [worm])

def write_score(filename:str, text:str) -> list:
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

while running:

    if menu == True:

        sound_manager.play_bg_music("menu")
        ui_screen.fill((0,0,0))
        if pg.Rect.collidepoint(optionbutton,pg.mouse.get_pos()) == True:
            pg.draw.rect(ui_screen,(255,255,255),optionbutton,50)
        else:
            pg.draw.rect(ui_screen,(0,255,255),optionbutton,50)

        # poll for events
        # pygame.QUIT event means the user clicked X to close your window
        for event in pg.event.get():
            if event.type == pg.QUIT:
                running = False
                menu = False
                level_selection = False
            if event.type == pg.KEYDOWN:

                menu = False
                level_selection = True
        #start_screen(screen)

        # Display the game via moderngl shader pipeline:
        shader.update()

    while level_selection:
        unlocked_level = load_score(get_path("saves/unlocked_levels.sav"))
        print(unlocked_level)
        # Menüoptionen
        ui_screen.fill((0, 0, 0))

        levels: list[str] = []
        for f in os.listdir(get_path(MAP_FOLDER)):
            for level in unlocked_level:
                if f.startswith(level) and f.endswith(".csv") and os.path.isfile(os.path.join(get_path(MAP_FOLDER), f)):
                    levels.append(os.path.splitext(f)[0])
        for i, option in enumerate(levels):
            color: str = BLUE if i == selected_level else WHITE
            text = FONT.render(option, True, color)
            ui_screen.blit(text, (SCREEN_WIDTH // 2 - text.get_width() // 2, 10 + i * 30))
        for event in pg.event.get():
            if event.type == pg.QUIT:
                running = False
                level_selection = False
            elif event.type == pg.KEYDOWN:
                if event.key == pg.K_DOWN:
                    selected_level = (selected_level + 1) % len(levels)
                    sound_manager.play_system_sound("selection")
                elif event.key == pg.K_UP:
                    selected_level = (selected_level - 1) % len(levels)
                    sound_manager.play_system_sound("selection")
                elif event.key == pg.K_RETURN:
                    game = True
                    level_selection = False
                    current_level = levels[selected_level]
                    game_world = load_world(current_level)
                    clock = pg.time.Clock()

        # Display the game via moderngl shader pipeline:
        shader.update()

    while game:

        sound_manager.play_bg_music("game")
        for event in pg.event.get():
            if event.type == pg.USEREVENT + 1:
                #game_world = load_world(current_level)
                clock = pg.time.Clock()
                #game_world.do_updates(delta)
                print("test")
            if event.type == pg.USEREVENT + 2:
                unlocked_level = f"{current_level[:-1]}{int(current_level[-1]) + 1}"
                current_level = unlocked_level
                write_score(get_path("saves/unlocked_levels.sav"), unlocked_level)
                game_world = load_world(current_level)
                clock = pg.time.Clock()
                game_world.do_updates(delta)
            if event.type == pg.QUIT:
                running = False
                game = False

            if event.type == pg.KEYDOWN and game_over == True:
                if event.key == pg.K_e:
                    game_world = load_world(current_level)
                    clock = pg.time.Clock()
                    game_over = False
            if event.type == pg.KEYDOWN:
                if level_unloaded == True:
                    if event.key == pg.K_e:
                        game_world = load_world(current_level)
                        clock = pg.time.Clock()
                        level_unloaded = False
                if event.key == pg.K_ESCAPE:
                    paused = True
                    clock = clock
                    while paused:


                        game_screen.blit(pause_image,(0,0,320,180))
                        pg.display.flip()
                        for event in pg.event.get():
                            if event.type == pg.KEYDOWN:
                                if event.key == pg.K_ESCAPE:
                                    paused = False
                                    clock = pg.time.Clock()
                            if event.type == pg.QUIT:
                                running = False
                                game = False
                                paused = False



        # do updates
        game_world.do_updates(delta)
        if game_world.player.player_lives <= 0:
            game_over = True

        #  render
        game_world.do_render(game_screen, ui_screen)
        if game_over == True:
            #pygame.draw.rect(screen,(255,255,255),optionbutton,50)
            restart_image = pg.image.load(get_path('assets/sprites/ui/restart.png'))
            game_screen.blit(restart_image, optionbutton)

        # Display the game via moderngl shader pipeline:
        # Pass camera position and light map (default both are zero)
        shader.update(game_world.camera_pos, game_world.get_light_map())

        delta = clock.tick(60) / 1000

pg.quit()
