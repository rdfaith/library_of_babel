# Example file showing a basic pygame "game loop"
import pygame
import object_classes
from game_world import GameWorld
import world_generation
from utils import *
from constants import *

# pygame setup
pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT),
                                 flags=pygame.SCALED)  # SCALED flag automatically scales screen to highest possible resolution
running = True
delta = 0.0
menu = True
game = False
woaw = True
gameo = False

optionbutton = pygame.Rect(160,90,80,40)

# create player character
#obstacle = object_classes.GameObject(pygame.Vector2(200, 100), pygame.image.load(get_path('assets/test/egg.png')))
#floor = object_classes.GameObject(pygame.Vector2(0, 148), pygame.image.load(get_path('assets/test/floor.png')))
#worm = object_classes.Worm(pygame.Vector2(140, 100), pygame.image.load(get_path('assets/test/worm.png')), True)
#game_world = GameWorld([], [obstacle, floor], [worm])


while running:
    while menu:
        screen.fill((0,0,0))
        if pygame.Rect.collidepoint(optionbutton,pygame.mouse.get_pos()) == True:
            pygame.draw.rect(screen,(255,255,255),optionbutton,50)
        else:
            pygame.draw.rect(screen,(0,255,255),optionbutton,50)
        pygame.display.flip()
        
        # poll for events
        # pygame.QUIT event means the user clicked X to close your window
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                menu = False
            if pygame.Rect.collidepoint(optionbutton,pygame.mouse.get_pos()) == True:
                if event.type == pygame.MOUSEBUTTONDOWN:
                    menu = False
                    game = True
                    game_world = world_generation.generate_world('assets/levels/test_map3.csv', 'assets/sprites/world_tileset.png')
                    clock = pygame.time.Clock()
    while game:


        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                game = False

            if pygame.Rect.collidepoint(optionbutton,pygame.mouse.get_pos()) == True:
                if event.type == pygame.MOUSEBUTTONDOWN:
                    game_world = world_generation.generate_world('assets/levels/test_map3.csv', 'assets/sprites/world_tileset.png')
                    clock = pygame.time.Clock()
                    gameo = False


        # do updates
        game_world.do_updates(delta)
        if game_world.player.player_lives <= 0:
            gameo = True

        #  render
        game_world.do_render(screen)
        if gameo == True:
            pygame.draw.rect(screen,(255,255,255),optionbutton,50)
            

        # flip() the display to put your work on screen
        pygame.display.flip()

        delta = clock.tick(60) / 1000

        
pygame.quit()
