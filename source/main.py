# Example file showing a basic pygame "game loop"
import pygame as pg
import object_classes
from game_world import GameWorld
import world_generation
from utils import *
from constants import *
from sound_manager import *
import os
#from menus import *

# pygame setup
pg.init()
screen = pg.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT),
                             flags=pg.SCALED)  # SCALED flag automatically scales screen to highest possible resolution
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
        screen.fill((0,0,0))
        if pg.Rect.collidepoint(optionbutton,pg.mouse.get_pos()) == True:
            pg.draw.rect(screen,(255,255,255),optionbutton,50)
        else:
            pg.draw.rect(screen,(0,255,255),optionbutton,50)
        pg.display.flip()
        
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


    while level_selection:
        unlocked_level = load_score(get_path("saves/unlocked_levels.sav"))
        print(unlocked_level)
        # Menüoptionen
        screen.fill((0, 0, 0))

        levels: list[str] = []
        for f in os.listdir(get_path(MAP_FOLDER)):
            for level in unlocked_level:
                if f.startswith(level) and f.endswith(".csv") and os.path.isfile(os.path.join(get_path(MAP_FOLDER), f)):
                    levels.append(os.path.splitext(f)[0])
        for i, option in enumerate(levels):
            color: str = BLUE if i == selected_level else WHITE
            text = FONT.render(option, True, color)
            screen.blit(text, (SCREEN_WIDTH // 2 - text.get_width() // 2, 10 + i * 30))
        levels: list[str] = [os.path.splitext(f)[0] for f in os.listdir(get_path(MAP_FOLDER)) if
                            os.path.isfile(os.path.join(get_path(MAP_FOLDER), f))]
        #level_select(screen,levels,selected_level)
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
                    level = levels[selected_level]
                    game_world = load_world(level)
                    clock = pg.time.Clock()
        pg.display.flip()

    while game:

        sound_manager.play_bg_music("game")
        for event in pg.event.get():
            if event.type == pg.USEREVENT + 1:

                print("test")
            if event.type == pg.USEREVENT + 2:
                unlocked_level = f"{level[:-1]}{int(level[-1]) + 1}"
                write_score(get_path("saves/unlocked_levels.sav"), unlocked_level)
                game_world = load_world(unlocked_level)
                clock = pg.time.Clock()
                game_world.do_updates(delta)
            if event.type == pg.QUIT:
                running = False
                game = False

            if event.type == pg.KEYDOWN and gameo == True:
                if event.key == pg.K_e:
                    game_world = load_world(level)
                    clock = pg.time.Clock()
                    gameo = False
            if event.type == pg.KEYDOWN:
                if level_unloaded == True:
                    if event.key == pg.K_e:
                        game_world = world_generation.generate_world(f"assets/levels/{level}.csv",
                                                                    'assets/sprites/tiles/autotile_tileset.png')
                        clock = pg.time.Clock()
                        level_unloaded = False
                if event.key == pg.K_ESCAPE:
                    paused = True
                    clock = clock
                    while paused:


                        screen.blit(pause_image,(0,0,320,180))
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
        game_world.do_render(screen)
        if game_over == True:
            #pygame.draw.rect(screen,(255,255,255),optionbutton,50)
            restart_image = pg.image.load(get_path('assets/sprites/ui/restart.png'))
            screen.blit(restart_image, optionbutton)

        # flip() the display to put your work on screen
        pg.display.flip()

        delta = clock.tick(60) / 1000

pg.quit()
