import pygame
from pygame import *

pygame.init()

# Konstanten
WIDTH, HEIGHT = 320, 180
FRAME_SIZE = 16

run = True
white = (255,255,255)
blue = (0,0,255)
black = (0,0,0)
gah = (255,0,0)
dah = (0,255,0)
screen = display.set_mode((WIDTH, HEIGHT), flags=SCALED)  # SCALED flag skaliert automatisch
clock = time.Clock()
optionbutton = Rect(160,90,80,40)
selected = False

while run:
    for event in pygame.event.get():
        if event.type == QUIT:
            run = False
        if Rect.collidepoint(optionbutton,mouse.get_pos()) == True:
            if event.type == MOUSEBUTTONDOWN:
                selected = True
    
    blah = mouse.get_pos()
    screen.fill(black)
    if Rect.collidepoint(optionbutton,blah) == True:
        draw.rect(screen,white,optionbutton,50)
    else:
        draw.rect(screen,blue,optionbutton, 50)
    display.flip()
quit()
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
clock = pygame.time.Clock()
running = True
selected = False
menu = True
game = False
woaw = True
delta = 0.0
optionbutton = pygame.Rect(160,90,80,40)

game_world: GameWorld

def load_game() -> GameWorld:
    # create player character
    #obstacle = object_classes.GameObject(pygame.Vector2(200, 100), pygame.image.load(get_path('assets/test/egg.png')))
    #floor = object_classes.GameObject(pygame.Vector2(0, 148), pygame.image.load(get_path('assets/test/floor.png')))
    #worm = object_classes.Worm(pygame.Vector2(140, 100), pygame.image.load(get_path('assets/test/worm.png')), True)
    #game_world = GameWorld([], [obstacle, floor], [worm])
    game_world = world_generation.generate_world('assets/levels/test_map.csv', 'assets/sprites/world_tileset.png', pygame.Vector2(0, 0))
    return game_world

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

    while game:
        if woaw == True:
            woaw = False
            game_world = load_game()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                game = False
        # do updates
        game_world.do_updates(delta)

        #  render
        game_world.do_render(screen)

        # flip() the display to put your work on screen
        pygame.display.flip()

        delta = clock.tick(60) / 1000

pygame.quit()