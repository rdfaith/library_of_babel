from source import *
from source.shaders.shader import Shader, FakeShader
from source.title_screen import TitleScreen

class GameState(Enum):
    START = 1
    LEVEL_SELECTION = 2
    GAME = 3
    GAME_OVER = 4
    IN_GAME_MENU = 5


class In_Game_Menu:
    def __init__(self, settings_filename: str):
        self.value = False
        self.rect = None
        self.image = None
        self.settings = load_settings(settings_filename)
        self.options = list(self.settings.keys())
        print(self.settings)

    def draw_button(self, name, selected_name, screen):
        self.font = pg.font.Font(get_path("assets/fonts/PixelOperator8.ttf"), 16)
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

        self.lable = self.font.render(name, True, (244,204,161))
        self.lable_width = self.lable.get_width()
        self.lable_height = self.lable.get_height()

        self.option_index = self.options.index(name)
        self.y_offset = 20 + self.option_index * (self.image_height + 10)  # Mehr Abstand zwischen den Optionen

        self.x_base = (UI_WIDTH - TEXT_WIDTH - self.image_width - 50) // 2

        self.lable_pos = (self.x_base, self.y_offset + (self.image_height - self.lable_height) // 2)
        self.img_pos = (self.x_base + 120, self.y_offset)

        return screen.blit(self.image, self.img_pos), screen.blit(self.lable, self.lable_pos)

    def update(self, name):
        # Hier wird der Wert immer zwischen "True" und "False" gewechselt
        if self.settings[name] == "True":
            self.settings[name] = "False"
        else:
            self.settings[name] = "True"
        return self.settings


def write_score(filename: str, text: str) -> list:
    with open(filename, "r") as file:
        content = file.read()

    if text not in content:
        with open(filename, "a") as file:
            file.write("\n" + text)

def load_score(filename: str) -> list:
    with open(filename, "r") as file:
        scores = [line.rstrip("\n") for line in file]
    return scores

def load_settings(filename: str) -> dict:
    settings = dict()

    with open(filename, 'r') as file:
        for line in file:
            key, value = line.strip().split('=')
            settings[key] = value
    return settings

def update_settings(filename: str, settings: dict):
    with open(filename, 'w') as file:
        for key, value in settings.items():
            file.write(f"{key}={value}\n")

def load_world(level_name: str):
    return world_generation.generate_world(f"{MAP_FOLDER + level_name}.csv")

def availible_levels(filename: str) -> list:
    unlocked_level = load_score(get_path(filename))
    levels: list[str] = []
    for f in os.listdir(get_path(MAP_FOLDER)):
        for level in unlocked_level:
            if f.startswith(level) and f.endswith(".csv") and os.path.isfile(os.path.join(get_path(MAP_FOLDER), f)):
                levels.append(os.path.splitext(f)[0])
    return levels

def display_levels(levels: int, selected_level, screen):
    FONT = pg.font.Font(get_path("assets/fonts/PixelOperator8.ttf"), 16)
    for i, option in enumerate(levels):
        color = '#a05b53' if i == selected_level else (244,204,161)
        text = FONT.render(option, True, color)
        screen.blit(text, (SCREEN_WIDTH // 2 - text.get_width() // 2, 10 + i * 30))
def get_shader():
    settings = load_settings(get_path(SETTINGS))
    if settings['SHADER'] == "True":
        shader = Shader(SCREEN_WIDTH, SCREEN_HEIGHT)
    elif settings['SHADER'] == "False":
        shader = FakeShader(SCREEN_WIDTH, SCREEN_HEIGHT)
    return shader

def menu_main(running: bool):

    # variablen
    selected_level = 0
    selected_button = 0
    sound_manager = SoundManager()
    game_state: GameState = GameState.START
    delta = 0.0
    clock = pg.time.Clock()
    shader = get_shader()
    in_game_menu = In_Game_Menu(SETTINGS)
    last_game_state = GameState.START

    title_screen: TitleScreen = TitleScreen()

    while running:

        while game_state == GameState.START:

            sound_manager.play_bg_music("menu")
            last_game_state = GameState.START
            shader.get_ui_screen().fill((0, 0, 0))


            # poll for events
            # pygame.QUIT event means the user clicked X to close your window
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    running = False
                    pg.quit()
                    sys.exit()

                if event.type == pg.KEYDOWN:
                    game_state = GameState.LEVEL_SELECTION


            # !!! Render with shader (use this instead of display.flip()!!!)

            title_screen.do_updates(delta)
            title_screen.do_render(shader)

            shader.update(light_map=title_screen.light_map)
            clock.tick(60)


        while game_state == GameState.LEVEL_SELECTION:
            last_game_state = GameState.LEVEL_SELECTION

            shader.get_ui_screen().fill((57, 49, 75))

            levels = availible_levels(get_path("saves/unlocked_levels.sav"))
            display_levels(levels, selected_level, shader.get_ui_screen())

            for event in pg.event.get():
                if event.type == pg.QUIT:
                    running = False
                    pg.quit()
                    sys.exit()
                elif event.type == pg.KEYDOWN:
                    if event.key == pg.K_DOWN:
                        selected_level = (selected_level + 1) % len(levels)
                        sound_manager.play_system_sound("selection")
                    elif event.key == pg.K_UP:
                        selected_level = (selected_level - 1) % len(levels)
                        sound_manager.play_system_sound("selection")
                    elif event.key == pg.K_RETURN:
                        current_level = levels[selected_level]
                        game_world = load_world(current_level)
                        game_state = GameState.GAME
                    elif event.key == pg.K_ESCAPE:
                        game_state = GameState.IN_GAME_MENU

            # !!! Render with shader (use this instead of display.flip()!!!)
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
                    game_state = GameState.GAME_OVER
                elif event.type == PLAYER_WON:  # Player Won
                    unlocked_level = f"{current_level[:-1]}{int(current_level[-1]) + 1}"
                    current_level = unlocked_level
                    write_score(get_path("saves/unlocked_levels.sav"), unlocked_level)
                    game_world = load_world(current_level)
                    clock = pg.time.Clock()
                elif event.type == DOOR_UNLOCKED:  # unlock door
                    for o in game_world.static_objects:
                        if isinstance(o, object_classes.Door):
                            o.unlock(game_world)
                elif event.type == WORD_LIGHT:  # player collected word 'LIGHT'
                    game_world.on_player_collected_light()
                if event.type == pg.QUIT:
                    running = False
                    pg.quit()
                    sys.exit()

            game_world.do_updates(delta)
            game_world.do_render(shader)

            # !!! Render with shader (use this instead of display.flip()!!!)
            shader.update(game_world.camera_pos, game_world.light_map)
            delta = clock.tick(60) / 1000

        while game_state == GameState.GAME_OVER:
            last_game_state = GameState.GAME_OVER
            #screen.fill((0, 0, 0))
            #screen.blit(RESTART_IMAGE, optionbutton)
            for event in pg.event.get():
                if event.type == pg.KEYDOWN:
                    if event.key == pg.K_ESCAPE:
                        game_state = GameState.IN_GAME_MENU
                    elif event.key == pg.K_e:
                        game_world = load_world(current_level)
                        game_state = GameState.GAME
                if event.type == pg.QUIT:
                    running = False
                    pg.quit()
                    sys.exit()

            clock.tick(60)
        while game_state == GameState.IN_GAME_MENU:
            sound_manager.play_bg_music("menu")
            sound_manager.play_movement_sound("idle")
            shader.get_ui_screen().fill((57, 49, 75))

            for event in pg.event.get():
                if event.type == pg.QUIT:
                    running = False
                    pg.quit()
                    sys.exit()
                elif event.type == pg.KEYDOWN:
                    if event.key == pg.K_DOWN:
                        selected_button = (selected_button + 1) % (len(in_game_menu.options))
                        sound_manager.play_system_sound("selection")
                    elif event.key == pg.K_UP:
                        selected_button = (selected_button - 1) % (len(in_game_menu.options))
                        sound_manager.play_system_sound("selection")
                    elif event.key == pg.K_RETURN:

                        update_settings(SETTINGS, in_game_menu.update(in_game_menu.options[selected_button]))
                        print(in_game_menu.settings)
                        sound_manager.play_bg_music("menu")
                        sound_manager.play_system_sound("selection")
                        for keys in in_game_menu.settings.keys():
                            in_game_menu.draw_button(keys, in_game_menu.options[selected_button], shader.get_ui_screen())
                    elif event.key == pg.K_ESCAPE:
                        game_state = last_game_state
                        shader = get_shader()
                    elif event.key == pg.K_BACKSPACE:
                        game_state = GameState.LEVEL_SELECTION


            for keys in in_game_menu.settings.keys():
                in_game_menu.draw_button(keys,in_game_menu.options[selected_button], shader.get_ui_screen())

            shader.update()



    pg.quit()
    sys.exit()
