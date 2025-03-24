# Example file showing a basic pygame "game loop"
import pygame
import pygame as pg
import object_classes
from game_world import GameWorld
import world_generation
from utils import *
from constants import *
import random_world
import os
import shaders.shader as shader

# pygame setup
pg.init()
pg.mixer.init()
sound = pg.mixer.Sound(get_path('assets/sounds/bg_music.mp3'))

game_screen = pg.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
light_source_screen = pg.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
ui_screen = pg.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))

shader = shader.Shader(SCREEN_WIDTH, SCREEN_HEIGHT, game_screen, ui_screen, light_source_screen)

running = True
delta = 0.0
menu = True
game = False
woaw = True
gameo = False
level_selection = False
selected_level = 0  # Index der ausgewählten Option
FONT = pg.font.Font(None, 30)

optionbutton = pg.Rect(120, 70, 80, 40)

# create player character
#obstacle = object_classes.GameObject(pygame.Vector2(200, 100), pygame.image.load(get_path('assets/test/egg.png')))
#floor = object_classes.GameObject(pygame.Vector2(0, 148), pygame.image.load(get_path('assets/test/floor.png')))
#worm = object_classes.Worm(pygame.Vector2(140, 100), pygame.image.load(get_path('assets/test/worm.png')), True)
#game_world = GameWorld([], [obstacle, floor], [worm])


# clock = pg.time.Clock()
# test = True
# while test:
#
#     for event in pygame.event.get():
#         if event.type == pygame.QUIT:
#             pygame.quit()
#
#     screen.fill((100, 100, 100))
#     pg.draw.rect(screen, (0, 255, 255), optionbutton, 50)
#
#     shader.update(screen)
#
#     clock.tick(60)

while running:

    while menu:
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
                menu = False
                level_selection = False
            if pg.Rect.collidepoint(optionbutton, pg.mouse.get_pos()) == True:
                if event.type == pg.MOUSEBUTTONDOWN:
                    menu = False
                    level_selection = True
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_RETURN:
                    menu = False
                    level_selection = True

        shader.update()

    while level_selection:
        # Menüoptionen
        ui_screen.fill((0, 0, 0))
        levels: list[str] = [os.path.splitext(f)[0] for f in os.listdir(get_path(MAP_FOLDER)) if
                             os.path.isfile(os.path.join(get_path(MAP_FOLDER), f))]
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
                elif event.key == pg.K_UP:
                    selected_level = (selected_level - 1) % len(levels)
                elif event.key == pg.K_RETURN:
                    game = True
                    level_selection = False
                    level = levels[selected_level]
                    game_world = world_generation.generate_world(f"{MAP_FOLDER + level}.csv",
                                                                 'assets/sprites/autotile_test.png')
                    clock = pg.time.Clock()

        shader.update()

    while game:

        sound.play(loops=-1)
        sound.set_volume(0.5)
        for event in pg.event.get():
            if event.type == pg.QUIT:
                running = False
                game = False

            if event.type == pg.KEYDOWN and gameo == True:
                if event.key == pg.K_e:
                    game_world = world_generation.generate_world(f"assets/levels/{level}.csv",
                                                                 'assets/sprites/tiles/autotile_tileset.png')
                    clock = pg.time.Clock()
                    gameo = False

        # do updates
        game_world.do_updates(delta)
        if game_world.player.player_lives <= 0:
            gameo = True

        #  render
        game_world.do_render(game_screen, ui_screen)
        if gameo == True:
            #pygame.draw.rect(screen,(255,255,255),optionbutton,50)
            dah = pg.image.load(get_path('assets/sprites/ui/restart.png'))
            ui_screen.blit(dah, optionbutton)

        # Display the game via moderngl shader pipeline:
        shader.update(game_world.camera_pos, game_world.get_light_map())

        delta = clock.tick(60) / 1000

pg.quit()
