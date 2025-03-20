# Example file showing a basic pygame "game loop"
import pygame
import object_classes
import game_world
import utils

# pygame setup
WIDTH, HEIGHT = 320, 180
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT),
                                 flags=pygame.SCALED)  # SCALED flag automatically scales screen to highest possible resolution
clock = pygame.time.Clock()
running = True
delta = 0.0

#  create player character
obstacle = object_classes.GameObject((200, 100), utils.get_path('assets/test/egg.png'))
floor = object_classes.GameObject((0, 148), utils.get_path('assets/test/floor.png'))
worm = object_classes.Worm((150, 100), 'assets/test/egg.png', True)
game_world = game_world.GameWorld([], [obstacle, floor], [worm])

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
