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

def find_tile(pos:pg.Vector2, map_data: list[list[str]]) -> int:
    map_width: int = len(map_data[0])
    map_height: int = len(map_data)
    coord_x, coord_y = int(pos.x/FRAME_SIZE), int(pos.y/FRAME_SIZE)
    object: str = map_data[coord_y][coord_x]

    # Prüfe direkte Nachbarn (oben, rechts, unten, links)
    top: bool = coord_y > 0 and map_data[coord_y - 1][coord_x] == object
    right: bool = coord_x < map_width - 1 and map_data[coord_y][coord_x + 1] == object
    bottom: bool = coord_y < map_height - 1 and map_data[coord_y + 1][coord_x] == object
    left: bool = coord_x > 0 and map_data[coord_y][coord_x - 1] == object

    # Binärwert berechnen (Reihenfolge: oben, rechts, unten, links)
    index: int = (top << 3) | (right << 2) | (bottom << 1) | left

    return TILE_MAPPING.get(index, (0))

def get_frame(frame_x: int, frame_y: int, tileset_file_path: str) -> pg.Surface:
    """Extrahiert einen Frame aus dem Tileset."""
    spritesheet = pg.image.load(get_path(tileset_file_path)).convert_alpha()
    frame = pg.Surface((FRAME_SIZE, FRAME_SIZE), pg.SRCALPHA)
    frame.blit(spritesheet, (0, 0), (frame_x * FRAME_SIZE, frame_y * FRAME_SIZE, FRAME_SIZE, FRAME_SIZE))
    return frame

def get_sprite(frame_x: int, frame_y: int) -> pg.Surface:
    """Extrahiert aus dem festgelegten standard tileset"""
    return get_frame(frame_x, frame_y, STANDARD_TILESET)

def generate_world(map_file_path: str, tileset_file_path: str) -> GameWorld:
    # Variablen
    map_data = read_map(map_file_path)
    current_pos: pg.Vector2 = pg.Vector2(0, 0)
    collision_objects: list[GameObject] = []
    interactable_objects: list[GameObject] = []
    objects: list[GameObject] = [] # unused currently
    player_start_pos: pg.Vector2
    level_size: tuple[int, int] = (len(map_data[0]) * FRAME_SIZE, len(map_data) * FRAME_SIZE)

    # # Level Dictionary für Tiles
    # # Frame, Position_list, collidable, interactive, enemy
    # level_dict = {
    #     " ": [get_frame(0, 6, tileset_file_path), [], False, False, False],
    #     "w": [get_frame(0, 1, tileset_file_path), [], True, False, False],
    #     "b": [get_frame(0, 0, tileset_file_path), [], True, False, False],
    #     "g": [get_frame(2, 0, tileset_file_path), [], True, False, False],
    #     "r": [get_frame(2, 1, tileset_file_path), [], True, False, False],
    #     "E": [get_frame(4, 8, tileset_file_path), [], False, True, True]
    # }

    for row in map_data:
        for col in row:
            pos: pygame.Vector2 = current_pos

            match col:
                case "block":
                    collision_objects.append(GameObject(pos, get_sprite(find_tile(pos, map_data), 0)))
                case "shelf":
                    collision_objects.append(GameObject(pos, get_sprite(find_tile(pos, map_data), 1)))

                case "worm":
                    interactable_objects.append(Worm(pos))
                case "player":
                    player_start_pos = pg.Vector2(pos.x, pos.y)
                case _:  # letter objects
                    if len(col) == 1:
                        if 65 <= ord(col) <= 90:
                            interactable_objects.append(LetterPickUp(pos, col))

            current_pos.x += FRAME_SIZE
        current_pos.x = 0
        current_pos.y += FRAME_SIZE
    current_pos.y = 0

    if not player_start_pos:
        print("ERROR: Player start position not defined for this level!")

    # for row in map_data:
    #     for col in row:
    #         frame = level_dict.get(col, level_dict[" "])[0]
    #         drawing_position = camera_pos + current_pos
    #         game_object = GameObject(drawing_position, frame)
    #         level_dict.get(col, level_dict[" "])[1].append(game_object)
    #         current_pos.x += FRAME_SIZE
    #     current_pos.x = 0
    #     current_pos.y += FRAME_SIZE
    # current_pos.y = 0
    #
    # for elements in level_dict:
    #     collidable = level_dict.get(elements, level_dict[" "])[2]
    #     interactive = level_dict.get(elements, level_dict[" "])[3]
    #     enemy = level_dict.get(elements, level_dict[" "])[4]
    #     if collidable:
    #         collision_objects.extend(level_dict.get(elements, level_dict[" "])[1])
    #     if interactive:
    #         interactable_objects.extend(level_dict.get(elements, level_dict[" "])[1])
    #     if not collidable and not interactive:
    #         objects.extend(level_dict.get(elements, level_dict[" "])[1])

    game_world: GameWorld = GameWorld(objects, collision_objects, interactable_objects, player_start_pos, level_size)
    return game_world

if __name__ == '__main__':
    pg.init()
    pg.display.set_mode((1, 1))
    test = generate_world('assets/levels/test_map.csv', 'assets/sprites/world_tileset.png')
    print(test.interactable_objects)