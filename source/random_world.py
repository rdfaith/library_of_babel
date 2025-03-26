from source import *

def create_level(width=50, height=16):
    # Leeres Level mit Luft füllen
    level = [[' ' for _ in range(width)] for _ in range(height)]

    # Erzeuge einen Grundparcours mit verschiedenen Höhen und Lücken
    ground_y = height - 2  # Zweitunterste Zeile als Basis
    last_height = ground_y
    for x in range(width):
        if random.random() < 0.2 and last_height > 4:
            last_height -= 1  # Plattform geht nach oben
        elif random.random() < 0.2 and last_height < ground_y:
            last_height += 1  # Plattform geht nach unten
        if random.random() > 0.1:  # Erzeuge gelegentliche Lücken im Boden
            level[last_height][x] = "block"

        # Lücken unterhalb der Plattformen mit Blöcken füllen
        for y in range(last_height + 1, height):
            level[y][x] = "block"

    # Löcher im Boden (mindestens 2 Blöcke breit und durchgängig)
    for _ in range(random.randint(2, 4)):
        x = random.randint(5, width - 7)
        for i in range(2):
            for y in range(height):
                level[y][x + i] = ' '

    # Spieler setzen (2 Blöcke über dem Boden gezeichnet)
    player_x = random.randint(0, 4)
    for y in range(height):
        if level[y][player_x] == "block" and level[y - 1][player_x] == ' ':
            level[y - 3][player_x] = "player"
            break

    # Säulen setzen (müssen auf Blöcken stehen, können komplexe Strukturen bilden)
    pillar_x_positions = set()
    for _ in range(random.randint(3, 6)):
        while True:
            x = random.randint(5, width - 5)
            if all(abs(x - px) >= 2 for px in pillar_x_positions):
                for y in range(height):
                    if level[y][x] == "block":
                        pillar_x_positions.add(x)
                        pillar_height = random.randint(2, 5)
                        for h in range(pillar_height):
                            level[y - h - 1][x] = "pillar"

                        # Struktur oben erweitern (Torstrukturen möglich)
                        if random.random() < 0.5:
                            for i in range(random.randint(1, 3)):
                                level[y - pillar_height][x + i] = "block"
                        else:
                            level[y - pillar_height][x] = "shelf"
                        break
                break

    # Shelfs setzen (horizontal oder vertikal, nicht beides, vertikale Shelfs auf Blöcken stehend)
    for _ in range(random.randint(4, 8)):
        if random.choice([True, False]):  # Horizontale Plattform
            x = random.randint(3, width - 6)
            y = random.randint(4, height - 3)
            length = random.randint(2, 5)
            if all(level[y][x + i] == ' ' for i in range(length)):
                for i in range(length):
                    level[y][x + i] = "shelf"
        else:  # Vertikale Barriere (muss auf einem Block stehen)
            x = random.randint(3, width - 3)
            for y in range(height - 6, 3, -1):
                if level[y][x] == "block" and all(level[y - i][x] == ' ' for i in range(1, 4)):
                    for i in range(3):
                        level[y - i][x] = "shelf"
                    break

    # Zwischenplattformen hinzufügen, wenn Sprünge zu hoch sind
    for x in range(1, width - 1):
        for y in range(1, height - 1):
            if (0 <= y + 2 < height and 0 <= y - 1 < height and
                    level[y][x] == ' ' and level[y + 2][x] in ["block", "pillar"] and level[y - 1][x] == ' '):
                if random.random() < 0.4:  # Wahrscheinlichkeit für Zwischenplattformen
                    level[y][x] = "shelf"

    # Buchstaben "BABEL" platzieren (müssen erreichbar sein)
    letters = list("BABEL")
    for letter in letters:
        while True:
            x = random.randint(1, width - 2)
            y = random.randint(1, height - 2)
            if level[y][x] == ' ' and (level[y + 1][x] in ["block", "pillar", "shelf"]):
                level[y][x] = letter
                break

    # Gegner "worm" platzieren (nicht in unmittelbarer Nähe des Spielers, können auch in der Luft spawnen, aber nicht direkt neben Blöcken)
    for _ in range(random.randint(2, 5)):
        while True:
            x = random.randint(5, width - 5)
            y = random.randint(2, height - 3)
            if level[y][x] == ' ' and abs(x - player_x) > 5:
                if level[y + 1][x] in ["block", "shelf"] or (
                        random.random() < 0.5 and level[y + 1][x] == ' ' and level[y - 1][x] == ' ' and all(
                        level[y][x + dx] == ' ' for dx in [-1, 1])):
                    level[y][x] = "worm"
                    break

    return level


# Level erstellen
level_data = create_level()

# Datei speichern
filename = utils.get_path("assets/levels/generated_map.csv")
with open(filename, "w", newline="") as file:
    writer = csv.writer(file)
    writer.writerows(level_data)

