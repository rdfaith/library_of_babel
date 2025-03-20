import pygame
from utils import get_path
import os

FRAME_SIZE = 16
SCREEN_WIDTH = 320
SCREEN_HEIGHT = 180
LEVEL_WIDTH, LEVEL_HEIGHT = 1600, 1200
#Kamera
DEAD_ZONE_Y = 20
CAMERA_DELAY_X, CAMERA_DELAY_Y = 50, 2

STANDARD_TILESET: str = "assets/sprites/tiles_spritesheet.png"

#region UI Constants
HEART_POS_0: pygame.Vector2 = pygame.Vector2(20,2)
HEART_POS_1: pygame.Vector2 = pygame.Vector2(35,2)
HEART_POS_2: pygame.Vector2 = pygame.Vector2(50,2)
HEART_POSITIONS: list[pygame.Vector2] = [HEART_POS_0, HEART_POS_1, HEART_POS_2]

LETTER_IMAGES = {}
for i in range(65, 90, 1):
    letter = chr(i)
    file_path = get_path("assets/sprites/letters/letter_" + letter + ".png")

    if os.path.exists(file_path):
        LETTER_IMAGES[letter] = pygame.image.load(file_path)
#endregion