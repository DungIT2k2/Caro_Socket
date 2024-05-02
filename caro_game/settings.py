# setup
import pygame

TILE_SIZE = 40
WINDOW_WIDTH = 1280
WINDOW_HEIGHT = 640

LINE_COLOR = "blue"

CURSOR_IMAGE = './img/cursor.png'

EDITOR_DATA = [
    {'id': 'x', 'image': './img/mark_x.png'},
    {'id': 'o', 'image': './img/mark_o.png'}
]

pygame.mixer.init()

#âm thanh
TICK_SOUND_X = pygame.mixer.Sound('./sound/mark_x.wav')
TICK_SOUND_O = pygame.mixer.Sound('./sound/mark_o.wav')
DRAW_WIN = pygame.mixer.Sound('./sound/win.wav')

# Tạo một kênh âm thanh mới để chứa âm thanh X và O
GAME_SOUNDS = pygame.mixer.Channel(1)
