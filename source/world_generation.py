from source import *
from source.object_classes import GameObject, ColliderObject


def load_spritesheets():
    """Lädt alle Spritesheets einmal und gibt sie als Dictionary zurück."""
    return {
        "tileset": pg.image.load(get_path(DEFAULT_TILESET)).convert(),
        "collider": pg.image.load(get_path(DEFAULT_COLLIDER_TILESET)).convert(),
        "normal": pg.image.load(get_path(DEFAULT_NORMAL_TILESET)).convert()
    }


def get_sprites(frame_x: int, frame_y: int, spritesheets: dict) -> (pg.Surface, pg.Surface):
    """Extrahiert sprite und Kollisions-sprite aus den standard tilesets"""
    return (
        spritesheets["tileset"].subsurface(frame_x * FRAME_SIZE, frame_y * FRAME_SIZE, FRAME_SIZE, FRAME_SIZE),
        spritesheets["collider"].subsurface(frame_x * FRAME_SIZE, frame_y * FRAME_SIZE, FRAME_SIZE, FRAME_SIZE),
        spritesheets["normal"].subsurface(frame_x * FRAME_SIZE, frame_y * FRAME_SIZE, FRAME_SIZE, FRAME_SIZE)
    )


def read_map(map_file_path: str) -> list[list[str]]:
    """Liest die Karte aus einer Datei und gibt sie als 2D-Liste zurück."""
    with open(get_path(map_file_path), newline='') as f:
        reader = csv.reader(f)
        return [list(row) for row in reader]


def find_tile(pos: pg.Vector2, map_data: list[list[str]]) -> int:
    map_width: int = len(map_data[0])
    map_height: int = len(map_data)
    coord_x, coord_y = int(pos.x / FRAME_SIZE), int(pos.y / FRAME_SIZE)
    object: str = map_data[coord_y][coord_x]

    # Prüfe direkte Nachbarn (oben, rechts, unten, links)
    top: bool = coord_y > 0 and map_data[coord_y - 1][coord_x] == object
    right: bool = coord_x < map_width - 1 and map_data[coord_y][coord_x + 1] == object
    bottom: bool = coord_y < map_height - 1 and map_data[coord_y + 1][coord_x] == object
    left: bool = coord_x > 0 and map_data[coord_y][coord_x - 1] == object

    # Binärwert berechnen (Reihenfolge: oben, rechts, unten, links)
    index: int = (top << 3) | (right << 2) | (bottom << 1) | left

    return TILE_MAPPING.get(index, (0))


def generate_world(map_file_path: str) -> GameWorld:
    # Lade Spritesheets einmal
    spritesheets = load_spritesheets()

    # Variablen
    map_data = read_map(map_file_path)
    current_pos: pg.Vector2 = pg.Vector2(0, 0)
    collision_objects: list[GameObject] = []
    interactable_objects: list[GameObject] = []
    objects: list[GameObject] = []  # unused currently
    player_start_pos: pg.Vector2
    level_size: tuple[int, int] = (len(map_data[0]) * FRAME_SIZE, len(map_data) * FRAME_SIZE)
    level_name = map_file_path[14:]

    for row in map_data:
        for col in row:
            pos: pg.Vector2 = current_pos
            tile_index = find_tile(pos, map_data)  # Berechnung nur einmal hier

            match col:
                case "block":
                    collision_objects.append(ColliderObject(pos, *get_sprites(tile_index, 0, spritesheets)))
                case "shelf":
                    collision_objects.append(ColliderObject(pos, *get_sprites(tile_index, 1, spritesheets)))
                case "pillar":
                    collision_objects.append(ColliderObject(pos, *get_sprites(tile_index, 2, spritesheets)))
                case "moving_platform":
                    collision_objects.append(MovingPlatform(pos.copy()))
                case "keyhole":
                    interactable_objects.append(Keyhole(pos))
                case "door":
                    collision_objects.append(Door(pos))
                case "worm":
                    interactable_objects.append(Worm(pos.copy()))
                case "flying_book":
                    interactable_objects.append(FlyingBook(pos.copy()))
                case "monkey":
                    interactable_objects.append(Monkey(pos.copy()))
                case "player":
                    player_start_pos = pg.Vector2(pos.x, pos.y)
                case "deco_candle":
                    objects.append(Candle(pos))
                case "deco_hourglass":
                    objects.append(Hourglass(pos))
                case "deco_books":
                    objects.append(GameObject(pos.copy(), pg.image.load(get_path("assets/sprites/deco/books1.png"))))
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

    game_world: GameWorld = GameWorld(objects, collision_objects, interactable_objects, player_start_pos, level_size,
                                      level_name)
    return game_world
