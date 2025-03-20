import pygame as pg
import csv
from object_classes import *
from game_world import *
from constants import *
from utils import *


def read_map(map_file_path: str) -> list[list[str]]:
    """Liest die Karte aus einer Datei und gibt sie als 2D-Liste zurück."""
    with open(get_path(map_file_path), newline='') as f:
        reader = csv.reader(f)
        return [list(row) for row in reader]

def get_frame(frame_x: int, frame_y: int, tileset_file_path: str) -> pg.Surface:
    """Extrahiert einen Frame aus dem Tileset."""
    spritesheet = pg.image.load(get_path(tileset_file_path)).convert_alpha()
    frame = pg.Surface((FRAME_SIZE, FRAME_SIZE), pg.SRCALPHA)
    frame.blit(spritesheet, (0, 0), (frame_x * FRAME_SIZE, frame_y * FRAME_SIZE, FRAME_SIZE, FRAME_SIZE))
    return frame

def generate_world(map_file_path: str, tileset_file_path: str, camera_pos: pg.Vector2) -> GameWorld:
    # Variablen
    map_data = read_map(map_file_path)
    current_pos: pg.Vector2 = pg.Vector2(0, 0)
    objects = []
    collision_objects = []
    interactable_objects = []


    # Level Dictionary für Tiles
    # Frame, Position_list, collidable, interactive
    level_dict = {
        " ": [get_frame(0, 6, tileset_file_path), [], False, False],
        "w": [get_frame(0, 1, tileset_file_path), [], True, False],
        "b": [get_frame(0, 0, tileset_file_path), [], False, False],
        "g": [get_frame(2, 0, tileset_file_path), [], True, False],
        "r": [get_frame(2, 1, tileset_file_path), [], True, False]
    }

    for row in map_data:
        for col in row:
            frame = level_dict.get(col, level_dict[" "])[0]
            drawing_position = camera_pos + current_pos
            game_object = GameObject(drawing_position, frame)
            level_dict.get(col, level_dict[" "])[1].append(game_object)
            current_pos.x += FRAME_SIZE
        current_pos.x = 0
        current_pos.y += FRAME_SIZE
    current_pos.y = 0

    for elements in level_dict:
        collidable = level_dict.get(elements, level_dict[" "])[2]
        interactive = level_dict.get(elements, level_dict[" "])[3]
        if collidable:
            collision_objects.extend(level_dict.get(elements, level_dict[" "])[1])
        if interactive:
            interactable_objects.extend(level_dict.get(elements, level_dict[" "])[1])
        if not collidable and not interactive:
            objects.extend(level_dict.get(elements, level_dict[" "])[1])

    return GameWorld(objects, collision_objects, interactable_objects)

if __name__ == '__main__':
    pg.init()
    pg.display.set_mode((1, 1))
    test = generate_world('assets/levels/test_map.csv', 'assets/sprites/world_tileset.png', pg.Vector2(0, 0))
    print(test.interactable_objects)