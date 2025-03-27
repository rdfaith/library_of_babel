from source import *
from source.shaders.shader import Shader, FakeShader
from source.title_screen import TitleScreen


class GameState(Enum):
    START = 1
    LEVEL_SELECTION = 2
    GAME = 3
    TRAILER = 4
    IN_GAME_MENU = 5
    SETTINGS = 6


class In_Game_Menu:
    def __init__(self, settings_filename: str):
        self.value = False
        self.rect = None
        self.image = None
        self.settings = load_file(settings_filename)
        self.options = list(self.settings.keys())
        self.font = FONT_16

    def draw_button(self, name, selected_name, screen):
        self.value = self.settings[name]
        if selected_name == name:
            if self.value == "True":
                self.image = TRUE_BUTTON_IMAGE_SELECTED
            else:
                self.image = FALSE_BUTTON_IMAGE_SELECTED
        else:
            if self.value == "True":
                self.image = TRUE_BUTTON_IMAGE
            else:
                self.image = FALSE_BUTTON_IMAGE
        self.image_width = self.image.get_width()
        self.image_height = self.image.get_height()

        self.lable = self.font.render(name, True, (244, 204, 161))
        self.lable_width = self.lable.get_width()
        self.lable_height = self.lable.get_height()

        self.option_index = self.options.index(name)
        self.y_offset = 20 + self.option_index * (self.image_height + 10)  # Mehr Abstand zwischen den Optionen

        self.x_base = (UI_WIDTH - TEXT_WIDTH - self.image_width - 50) // 2

        self.lable_pos = (self.x_base, self.y_offset + (self.image_height - self.lable_height) // 2)
        self.img_pos = (self.x_base + 120, self.y_offset)

        return screen.blit(self.image, self.img_pos), screen.blit(self.lable, self.lable_pos)

    def update(self, name):
        # Hier wird der Wert immer zwischen True und False gewechselt
        self.settings[name] = "False" if self.settings[name] == "True" else "True"
        return self.settings

def load_world(level_name: str):
    return world_generation.generate_world(f"{MAP_FOLDER + level_name}")

def availible_levels(filename: str) -> list:
    levels = load_file(filename)
    unlocked_levels = [key for key, value in levels.items() if value != "False"]
    return unlocked_levels

def display_levels(levels, selected_level, screen, filename: str):
    highscores = load_file(filename)
    for i, option in enumerate(levels):
        color = '#a05b53' if i == selected_level else (244, 204, 161)
        level_name_str = option[:-4].replace("_", " ").upper()
        line = f"{level_name_str} - {highscores[option]}" if highscores[option] != "False" and highscores[
            option] != "99.99" else f"{level_name_str} - NONE"
        text = FONT_16.render(line, True, color)
        screen.blit(text, (SCREEN_WIDTH // 2 - 150 // 2, 10 + i * 30))


def display_menu(menu, selected_option, screen):
    screen.blit(MENU_IMAGE, (0, 0, SCREEN_WIDTH, SCREEN_HEIGHT))
    for i, option in enumerate(menu.keys()):
        color = '#A65E58' if i == selected_option else "#602323"
        text = FONT_8.render(option, True, color)
        screen.blit(text, (SCREEN_WIDTH // 2 + 45 // 2, 70 + i * 20))


def unlock_levels(filename, current_level):
    levels = load_file(filename)
    all_levels = list(levels.keys())  # Jetzt ist es eine echte Liste

    if current_level in all_levels:
        current_index = all_levels.index(current_level)

        if current_index + 1 < len(all_levels):  # Prüfen, ob es ein nächstes Level gibt
            levels[all_levels[current_index + 1]] = "99.99"
    update_file(filename, levels)


def get_shader():
    settings = load_file(get_path(SETTINGS))
    if settings['SHADER'] == "True":
        shader = Shader(SCREEN_WIDTH, SCREEN_HEIGHT)
    else:
        shader = FakeShader(SCREEN_WIDTH, SCREEN_HEIGHT)
    return shader


def menu_main(running: bool):
    # variablen
    selected_level = 0
    selected_button = 0
    selected_option = 0
    voice_timer = 0
    sound_manager = SoundManager()
    game_state: GameState = GameState.START
    delta = 0.0
    clock = pg.time.Clock()
    shader = get_shader()
    in_game_menu = In_Game_Menu(SETTINGS)
    last_game_state = GameState.START
    dino_title_screen: TitleScreen = TitleScreen("START")
    monkey_title_screen: TitleScreen = TitleScreen("TRAILER")

    game_world = None  # global name
    current_level = None # global name

    while running:
        while game_state == GameState.START:
            sound_manager.play_bg_music("menu")
            last_game_state = GameState.START
            shader.get_ui_screen().fill((0, 0, 0))

            # poll for events
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    running = False
                    pg.quit()
                    sys.exit()
                if event.type == pg.KEYDOWN:
                    current_settings = load_file(LEVELS)
                    if current_settings["HEX_1.csv"] == "99.99":
                        game_state = GameState.TRAILER
                    else:
                        game_state = GameState.LEVEL_SELECTION

            # Render with shader
            dino_title_screen.do_updates(delta)
            dino_title_screen.do_render(shader)
            shader.update(light_map=dino_title_screen.light_map)
            clock.tick(60)

        while game_state == GameState.TRAILER:
            sound_manager.play_movement_sound("typewriter")
            sound_manager.play_enemy_sound("voiceover")
            last_game_state = GameState.START
            shader.get_ui_screen().fill((20, 20, 20))
            voice_timer += 0.1

            # poll for events
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    running = False
                    pg.quit()
                    sys.exit()
                if event.type == pg.KEYDOWN:
                    game_state = GameState.LEVEL_SELECTION
            if voice_timer > 145:
                game_state = GameState.LEVEL_SELECTION

            # Render with shader
            monkey_title_screen.do_updates(delta)
            monkey_title_screen.do_render(shader)
            shader.update(light_map=monkey_title_screen.light_map)
            clock.tick(60)

        while game_state == GameState.LEVEL_SELECTION:
            sound_manager.play_movement_sound("idle")
            sound_manager.play_enemy_sound("idle")
            last_game_state = GameState.LEVEL_SELECTION
            shader.get_ui_screen().fill((57, 49, 75))

            unlocked_levels = availible_levels(LEVELS)
            display_levels(unlocked_levels, selected_level, shader.get_ui_screen(), LEVELS)

            for event in pg.event.get():
                if event.type == pg.QUIT:
                    running = False
                    pg.quit()
                    sys.exit()
                elif event.type == pg.KEYDOWN:
                    if event.key == pg.K_DOWN:
                        selected_level = (selected_level + 1) % len(unlocked_levels)
                        sound_manager.play_system_sound("selection")
                    elif event.key == pg.K_UP:
                        selected_level = (selected_level - 1) % len(unlocked_levels)
                        sound_manager.play_system_sound("selection")
                    elif event.key == pg.K_RETURN:
                        current_level = unlocked_levels[selected_level]
                        game_world = load_world(current_level)
                        game_state = GameState.GAME
                    elif event.key == pg.K_ESCAPE:
                        game_state = GameState.SETTINGS

            # Render with shader
            shader.update()
            clock.tick(60)

        while game_state == GameState.GAME:
            last_game_state = GameState.GAME
            sound_manager.play_bg_music("game")
            for event in pg.event.get():
                if event.type == pg.KEYDOWN:
                    if event.key == pg.K_ESCAPE:
                        game_state = GameState.IN_GAME_MENU
                    elif event.key == pg.K_BACKSPACE:
                        game_world = load_world(current_level)
                if event.type == PLAYER_DIED:  # Player Died
                    game_world = load_world(current_level)
                    game_state = GameState.GAME
                elif event.type == PLAYER_WON:  # Player Won
                    unlock_levels(LEVELS, current_level)
                    unlocked_levels = availible_levels(LEVELS)
                    game_world = load_world(unlocked_levels[-1])
                    current_level = unlocked_levels[-1]
                    clock = pg.time.Clock()
                elif event.type == DOOR_UNLOCKED:  # unlock door
                    for o in game_world.static_objects:
                        if isinstance(o, object_classes.Door):
                            o.unlock(game_world)
                elif event.type == WORD_LIGHT:  # player collected word 'LIGHT'.
                    game_world.on_player_collected_light()
                if event.type == pg.QUIT:
                    running = False
                    pg.quit()
                    sys.exit()

            game_world.do_updates(delta)
            game_world.do_render(shader)
            shader.update(game_world.camera_pos, game_world.get_light_map())
            delta = clock.tick(60) / 1000

        while game_state == GameState.IN_GAME_MENU:
            last_game_state = GameState.IN_GAME_MENU
            sound_manager.play_bg_music("menu")
            sound_manager.play_movement_sound("idle")
            sound_manager.play_enemy_sound("idle")

            MENU_OPTIONS = {
                "RESUME": GameState.GAME,
                "RESTART": GameState.GAME,
                "LEVEL": GameState.LEVEL_SELECTION,
                "SETTINGS": GameState.SETTINGS,
            }

            display_menu(MENU_OPTIONS, selected_option, shader.get_ui_screen())
            clock.tick(60)  # Framerate-Limit früh setzen

            for event in pg.event.get():
                if event.type == pg.KEYDOWN:
                    if event.key == pg.K_ESCAPE or event.key == pg.K_BACKSPACE:
                        game_state = GameState.GAME
                        shader = get_shader()
                    elif event.key == pg.K_DOWN:
                        selected_option = (selected_option + 1) % len(MENU_OPTIONS)
                        sound_manager.play_system_sound("selection")
                    elif event.key == pg.K_UP:
                        selected_option = (selected_option - 1) % len(MENU_OPTIONS)
                        sound_manager.play_system_sound("selection")
                    elif event.key == pg.K_RETURN:
                        menu_options = list(MENU_OPTIONS.keys())

                        if selected_option == 1:
                            game_world = load_world(current_level)

                        game_state = MENU_OPTIONS[menu_options[selected_option]]

                elif event.type == pg.QUIT:
                    running = False
                    pg.quit()
                    sys.exit()

            shader.update()

        while game_state == GameState.SETTINGS:
            shader.get_ui_screen().fill((57, 49, 75))

            for event in pg.event.get():
                if event.type == pg.QUIT:
                    running = False
                    pg.quit()
                    sys.exit()
                elif event.type == pg.KEYDOWN:
                    if event.key == pg.K_DOWN:
                        selected_button = (selected_button + 1) % len(in_game_menu.options)
                        sound_manager.play_system_sound("selection")
                    elif event.key == pg.K_UP:
                        selected_button = (selected_button - 1) % len(in_game_menu.options)
                        sound_manager.play_system_sound("selection")
                    elif event.key == pg.K_RETURN:
                        update_file(SETTINGS, in_game_menu.update(in_game_menu.options[selected_button]))
                        sound_manager.play_bg_music("menu")
                        sound_manager.play_system_sound("selection")
                        for keys in in_game_menu.settings.keys():
                            in_game_menu.draw_button(keys, in_game_menu.options[selected_button],
                                                     shader.get_ui_screen())
                    elif event.key == pg.K_ESCAPE or event.key == pg.K_BACKSPACE:
                        game_state = last_game_state
                        shader = get_shader()
                    elif event.key == pg.K_r:
                        reset_file(LEVELS)
                        print("level wurden zurückgesetzt")

            for keys in in_game_menu.settings.keys():
                in_game_menu.draw_button(keys, in_game_menu.options[selected_button], shader.get_ui_screen())

            shader.update()

    pg.quit()
    sys.exit()
