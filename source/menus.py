from source import *

sound_manager = SoundManager()
optionbutton = pg.Rect(120,70,80,40)

def start_screen(screen):

        sound_manager.play_bg_music("menu")
        screen.fill((0,0,0))
def level_select(screen,levels,selected_level):
    screen.fill((0, 0, 0))
    for i, option in enumerate(levels):
        color: str = BLUE if i == selected_level else WHITE
        text = FONT.render(option, True, color)
        screen.blit(text, (SCREEN_WIDTH // 2 - text.get_width() // 2, 10 + i * 30))
        