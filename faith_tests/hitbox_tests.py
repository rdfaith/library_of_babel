import pygame
from source.object_classes import Player


def _generate_hitbox(position: pygame.Vector2, hitbox_image: pygame.Surface) -> pygame.Rect:
    """Generates a rectangular hitbox based on the non-transparent part of hitbox_image."""
    bbox = hitbox_image.get_bounding_rect()  # Get bounding rectangle of non-transparent area

    if bbox:
        # Adjust the hitbox position relative to the world position
        hitbox = bbox.copy()
        #hitbox.topleft = position + pygame.Vector2(bbox.topleft)  # Offset by bbox position
        hitbox.topleft
    else:
        # No visible hitbox, return an empty rect at the sprite's position
        hitbox = pygame.Rect(position.x, position.y, 0, 0)

    return hitbox


# Initialize Pygame
pygame.init()

# Screen dimensions
WIDTH, HEIGHT = 200, 200
screen = pygame.display.set_mode((WIDTH, HEIGHT), flags=pygame.SCALED)
pygame.display.set_caption('GameObject Test')

# Create a GameObject instance
player = Player(pygame.Vector2(100, 100))

# Game loop
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Fill the screen with a background color
    screen.fill((255, 255, 255))  # White background

    # Draw the GameObject
    player.draw(screen, pygame.Vector2(0, 0))
    # Draw hit box, just for debugging:

    # Update the screen
    pygame.display.flip()

    # Limit the frame rate
    pygame.time.Clock().tick(60)

# Quit Pygame
pygame.quit()
