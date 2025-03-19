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
delta = 0.0

# create player character
# obstacle = object_classes.GameObject(pygame.Vector2(200, 100), pygame.image.load(get_path('assets/test/egg.png')))
# floor = object_classes.GameObject(pygame.Vector2(0, 148), pygame.image.load(get_path('assets/test/floor.png')))
# # game_world = GameWorld([], [obstacle, floor], [])
game_world = world_generation.generate_world('assets/levels/test_map.csv', 'assets/sprites/world_tileset.png', pygame.Vector2(0, 0))

while running:
    # poll for events
    # pygame.QUIT event means the user clicked X to close your window
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # do updates
    game_world.do_updates(delta)

    #  render
    game_world.do_render(screen)

    # flip() the display to put your work on screen
    pygame.display.flip()

    delta = clock.tick(60) / 1000

pygame.quit()
