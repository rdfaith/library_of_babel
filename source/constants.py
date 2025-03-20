import pygame as pg
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
HEART_POS_0: pg.Vector2 = pg.Vector2(20, 2)
HEART_POS_1: pg.Vector2 = pg.Vector2(35, 2)
HEART_POS_2: pg.Vector2 = pg.Vector2(50, 2)
UI_HEART_POSITIONS: list[pg.Vector2] = [HEART_POS_0, HEART_POS_1, HEART_POS_2]

# LETTER_POS_0: pg.Vector2 = pg.Vector2(256, 0)
UI_LETTER_POSITIONS: list[pg.Vector2] = []
for i in range(5):
    UI_LETTER_POSITIONS.append(pg.Vector2(256 + (12 * i), 0))

LETTER_IMAGES = {}
for i in range(65, 90, 1):
    letter = chr(i)
    file_path = get_path("assets/sprites/letters/letter_" + letter + ".png")

    if os.path.exists(file_path):
        LETTER_IMAGES[letter] = pg.image.load(file_path)
#endregion