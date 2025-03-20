import pygame as pg
import utils

# Pygame initialisieren
pg.init()

# Bildschirmgröße
SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600
screen = pg.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

# Spielfeldgröße (Level größer als Screen)
LEVEL_WIDTH, LEVEL_HEIGHT = 1600, 1200

# Hintergrundbild laden
background = pg.image.load(utils.get_path('assets/sprites/bg.png'))  # Ersetze mit deinem Bildpfad
background = pg.transform.scale(background, (LEVEL_WIDTH, LEVEL_HEIGHT))

# Spieler erstellen
player = pg.Rect(400, 300, 50, 50)

# Kamera-Startposition
camera_x, camera_y = player.x - SCREEN_WIDTH // 2, player.y - SCREEN_HEIGHT // 2

# Lerp-Funktion für sanfte Bewegung
def lerp(a, b, t):
    return a + (b - a) * t

# Spiel-Loop
running = True
clock = pg.time.Clock()
while running:
    screen.fill((30, 30, 30))  # Hintergrundfarbe für Debug-Zwecke

    # Event-Handling
    for event in pg.event.get():
        if event.type == pg.QUIT:
            running = False

    # Spielerbewegung (mit WASD)
    keys = pg.key.get_pressed()
    speed = 5
    if keys[pg.K_w]: player.y -= speed
    if keys[pg.K_s]: player.y += speed
    if keys[pg.K_a]: player.x -= speed
    if keys[pg.K_d]: player.x += speed

    # Zielposition der Kamera berechnen
    target_x = player.x - SCREEN_WIDTH // 2
    target_y = player.y - SCREEN_HEIGHT // 2

    # Verzögerte Bewegung der Kamera (smooth follow)
    camera_x = lerp(camera_x, target_x, 0.1)
    camera_y = lerp(camera_y, target_y, 0.1)

    # Kamera-Begrenzung innerhalb der Levelgrenzen
    camera_x = max(0, min(camera_x, LEVEL_WIDTH - SCREEN_WIDTH))
    camera_y = max(0, min(camera_y, LEVEL_HEIGHT - SCREEN_HEIGHT))

    # Hintergrund relativ zur Kamera zeichnen
    screen.blit(background, (-camera_x, -camera_y))

    # Spieler relativ zur Kamera zeichnen
    pg.draw.rect(screen, (0, 255, 0), (player.x - camera_x, player.y - camera_y, 50, 50))

    # Update-Loop
    pg.display.flip()
    clock.tick(60)

pg.quit()
