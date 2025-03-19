# Example file showing a basic pygame "game loop"
import pygame


# pygame setup
WIDTH, HEIGHT = 320, 180
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT), flags=pygame.SCALED) # SCALED flag automatically scales screen to highest possible resolution
clock = pygame.time.Clock()
running = True
#test
while running:
    # poll for events
    # pygame.QUIT event means the user clicked X to close your window
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # fill the screen with a color to wipe away anything from last frame
    screen.fill("purple")

    # RENDER YOUR GAME HERE

    # flip() the display to put your work on screen
    pygame.display.flip()

    clock.tick(60)  # limits FPS to 60

pygame.quit()