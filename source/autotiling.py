import pygame

pygame.init()

# Farben
WHITE = (255, 255, 255)
GRAY = (200, 200, 200)
BLACK = (0, 0, 0)
BLUE = (50, 100, 255)

# Bildschirmgröße
WIDTH, HEIGHT = 400, 300
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Einfaches Auswahlmenü")

# Schriftart
font = pygame.font.Font(None, 40)

# Menüoptionen
options = ["Start", "Optionen", "Beenden"]
selected_option = 0  # Index der ausgewählten Option

running = True
while running:
    screen.fill(WHITE)

    # Menüoptionen zeichnen
    for i, option in enumerate(options):
        color = BLUE if i == selected_option else BLACK
        text = font.render(option, True, color)
        screen.blit(text, (WIDTH // 2 - text.get_width() // 2, 100 + i * 50))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_DOWN:
                selected_option = (selected_option + 1) % len(options)  # Nächste Option
            elif event.key == pygame.K_UP:
                selected_option = (selected_option - 1) % len(options)  # Vorherige Option
            elif event.key == pygame.K_RETURN:  # Auswahl bestätigen
                if options[selected_option] == "Start":
                    print("Spiel startet...")
                elif options[selected_option] == "Optionen":
                    print("Optionen-Menü öffnet sich...")
                elif options[selected_option] == "Beenden":
                    running = False

    pygame.display.flip()

pygame.quit()
