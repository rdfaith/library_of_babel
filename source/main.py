import pygame
import object_classes
import game_world

pygame.init()
screen = pygame.display.set_mode((320, 180), flags=pygame.SCALED)
running = True
clock = pygame.time.Clock()
delta = 0.0
#  create list with game objects

#  create player character
obstacle = object_classes.GameObject((200, 100), 'assets/test/egg.png')
floor = object_classes.GameObject((0, 148), 'assets/test/floor.png')
game_world = game_world.GameWorld([], [obstacle, floor], [])

while running:
    #  check if closed
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