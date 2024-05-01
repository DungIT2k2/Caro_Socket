import pygame
from caro_game.settings import WINDOW_HEIGHT, WINDOW_WIDTH, CURSOR_IMAGE
from pygame.image import load
from pygame.mouse import get_pressed as mouse_button
from caro_game.game import Game

class Caro:
    def __init__(self, connection, host, port, username=None, competitor_name=None, is_host=True):
        self.connection = connection
        self.host = host
        self.port = port
        self.username = username
        self.is_host = is_host

        self.display_surface = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        self.clock = pygame.time.Clock()
        self.game = Game(username, competitor_name, is_host)
        surf = load(CURSOR_IMAGE).convert_alpha()
        cursor = pygame.cursors.Cursor((0, 0),surf)
        pygame.mouse.set_cursor(cursor)
        self.clicked = False

    def mouse_event(self):
        if self.game.playing and mouse_button()[0] and not self.clicked:
            (x, y) = self.game.get_current_cell()
            if self.game.left_mouse_click(x, y):
                self.connection.sendto(f'Game:::{x}:::{y}:::'.encode('utf-8'), (self.host, self.port))
                self.clicked = True

    def event_loop(self, event):
        self.game.pan_input(event)
        #bấm enter để chơi lại
        if event.type == pygame.locals.KEYDOWN and event.key == pygame.locals.K_RETURN:
            #Set lượt đi cho người thua
            if self.game.selection_index == 'x':
                if self.is_host:
                    self.clicked = False
                else:
                    self.clicked = True
            else:
                if self.is_host:
                    self.clicked = True
                else:
                    self.clicked = False
            self.game.play_again()
            self.connection.sendto(b'Play again', (self.host, self.port))
