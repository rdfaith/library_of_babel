# Example file showing a basic pygame "game loop"
import pygame as pg
import object_classes
from game_world import GameWorld
import world_generation
from utils import *
from constants import *
from sound_manager import *

import os

# pygame setup
pg.init()
from menus import *
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

sound_manager = SoundManager()
optionbutton = pg.Rect(120,70,80,40)

# create player character
#obstacle = object_classes.GameObject(pygame.Vector2(200, 100), pygame.image.load(get_path('assets/test/egg.png')))
#floor = object_classes.GameObject(pygame.Vector2(0, 148), pygame.image.load(get_path('assets/test/floor.png')))
#worm = object_classes.Worm(pygame.Vector2(140, 100), pygame.image.load(get_path('assets/test/worm.png')), True)
#game_world = GameWorld([], [obstacle, floor], [worm])


while running:

    if menu == True:

        for event in pg.event.get():
            if event.type == pg.QUIT:
                running = False
                menu = False
                level_selection = False
            if event.type == pg.KEYDOWN:

                menu = False
                level_selection = True
        start_screen(screen)

        
    while level_selection:
        # Menüoptionen
        levels: list[str] = [os.path.splitext(f)[0] for f in os.listdir(get_path(MAP_FOLDER)) if
                            os.path.isfile(os.path.join(get_path(MAP_FOLDER), f))]
        level_select(screen,levels,selected_level)
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
                    game_world = world_generation.generate_world(f"{MAP_FOLDER + level}.csv",
                                                                 'assets/sprites/autotile_test.png')
                    clock = pg.time.Clock()
        pg.display.flip()

    while game:

        sound_manager.play_bg_music("game")
        for event in pg.event.get():
            if event.type == pg.QUIT:
                running = False
                game = False

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
