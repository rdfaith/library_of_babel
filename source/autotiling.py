import pygame
import utils

# Konstanten
TILE_SIZE = 32
MAP_WIDTH, MAP_HEIGHT = 10, 10

# Beispiel-Tileset (16 Tiles für Autotiling)
tileset = pygame.image.load(utils.get_path('assets/sprites/test_dino.png'))

# Mapping der binären Werte zu Tileset-Positionen
TILE_MAPPING = {
    0b0000: (0, 0),  # Isolierte Kachel
    0b0001: (1, 0),  # Verbindung nach links
    0b0010: (2, 0),  # Verbindung nach unten
    0b0011: (3, 0),  # Verbindung nach links & unten
    0b0100: (0, 1),  # Verbindung nach rechts
    0b0101: (1, 1),  # Verbindung nach links & rechts
    0b0110: (2, 1),  # Verbindung nach rechts & unten
    0b0111: (3, 1),  # U-Form (rechts, links, unten)
    0b1000: (0, 2),  # Verbindung nach oben
    0b1001: (1, 2),  # Verbindung nach oben & links
    0b1010: (2, 2),  # Verbindung nach oben & unten (vertikale Linie)
    0b1011: (3, 2),  # U-Form (oben, unten, links)
    0b1100: (0, 3),  # Verbindung nach oben & rechts
    0b1101: (1, 3),  # U-Form (oben, rechts, links)
    0b1110: (2, 3),  # U-Form (oben, unten, rechts)
    0b1111: (3, 3),  # Komplett umschlossen
}

# Beispielhafte Tilemap mit 1 (Wand) und 0 (Leerraum)
tilemap = [
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 1, 1, 1, 1, 1, 1, 1, 1, 0],
    [0, 1, 0, 0, 0, 0, 0, 0, 1, 0],
    [0, 1, 0, 1, 1, 1, 1, 0, 1, 0],
    [0, 1, 0, 1, 0, 0, 1, 0, 1, 0],
    [0, 1, 0, 1, 1, 1, 1, 0, 1, 0],
    [0, 1, 0, 0, 0, 0, 0, 0, 1, 0],
    [0, 1, 1, 1, 1, 1, 1, 1, 1, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
]

def get_tile_index(x, y):
    """Berechnet den Autotile-Index basierend auf direkten Nachbarn."""
    if tilemap[y][x] == 0:
        return None  # Keine Kachel nötig

    # Prüfe direkte Nachbarn (oben, rechts, unten, links)
    top = y > 0 and tilemap[y-1][x] == 1
    right = x < MAP_WIDTH-1 and tilemap[y][x+1] == 1
    bottom = y < MAP_HEIGHT-1 and tilemap[y+1][x] == 1
    left = x > 0 and tilemap[y][x-1] == 1

    # Binärwert berechnen (Reihenfolge: oben, rechts, unten, links)
    index = (top << 3) | (right << 2) | (bottom << 1) | left
    print(index)
    return TILE_MAPPING.get(index, (0, 0))

def draw_map(screen):
    """Zeichnet die Tilemap mit Autotiling."""
    for y in range(MAP_HEIGHT):
        for x in range(MAP_WIDTH):
            tile_pos = get_tile_index(x, y)
            if tile_pos:
                sx, sy = tile_pos
                screen.blit(tileset, (x*TILE_SIZE, y*TILE_SIZE), (sx*TILE_SIZE, sy*TILE_SIZE, TILE_SIZE, TILE_SIZE))

# Pygame Initialisierung
pygame.init()
screen = pygame.display.set_mode((MAP_WIDTH * TILE_SIZE, MAP_HEIGHT * TILE_SIZE))
clock = pygame.time.Clock()

running = True
while running:
    screen.fill((0, 0, 0))
    draw_map(screen)

    pygame.display.flip()
    clock.tick(60)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

pygame.quit()
