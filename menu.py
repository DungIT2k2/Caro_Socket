import pygame
import pygame_menu
from pygame_menu.examples import create_example_window
import socket
import tkinter as tk
from tkinter import messagebox

from typing import Optional

from setting_menu import WINDOW_SIZE, FPS
from server import Server, Client

class Menu:
    def __init__(self):
        self.clock: Optional['pygame.time.Clock'] = None
        self.main_menu: Optional['pygame_menu.Menu'] = None
        self.surface: Optional['pygame.Surface'] = None
        
    def main_background(self):
        self.surface.fill((0, 0, 0))

    def start_click(self):
        username = self.username_server_text.get_value()
        if not username: return
        Server('', 55843, username, self.surface)

    def join_click(self):
        ip_address = self.ip_address_text.get_value().strip()
        if not ip_address: return
        username = self.username_client_text.get_value()
        if not username: return
        
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        #check(tồn tại) địa chỉ host 
        try:
            socket.gethostbyname(ip_address)
        except socket.gaierror:
            messagebox.showerror("Error", "Địa chỉ host không tồn tại!!!")
            self.ip_address_text.set_value("")
            return
        #check(đúng) địa chỉ host 
        sock.connect((ip_address, 55843))
        sock.settimeout(3)
        sock.sendto(f'Connected:::{username}'.encode('utf-8'), (ip_address, 55843))
        while True:
            try:
                response, addr = sock.recvfrom(1024)
                message = response.decode('utf-8').split(':::')
                print("Received message from server:", message[0])
                if message[0] == 'Connected':
                    sock.settimeout(None)
                    break 
            except (socket.error, socket.timeout):
                print("Timeout occurred, no response from server")
                messagebox.showerror("Error", "Địa chỉ host sai!!!")
                self.ip_address_text.set_value("")
                return
        Client(ip_address, 55843, username, message[1], sock)      
        
    def run(self):
        self.surface = create_example_window('Caro - Socket', WINDOW_SIZE)
        self.clock = pygame.time.Clock()

        self.play_menu = pygame_menu.Menu(
            height=WINDOW_SIZE[1],
            theme=pygame_menu.themes.THEME_BLUE,
            title='Play Menu',
            width=WINDOW_SIZE[0]
        )

        self.start_server_menu = pygame_menu.Menu(
            height=WINDOW_SIZE[1],
            theme=pygame_menu.themes.THEME_BLUE,
            title='Host Server',
            width=WINDOW_SIZE[0]
        )
        self.username_server_text = self.start_server_menu.add.text_input(title='Username: ')
        self.start_server_menu.add.button('Start', self.start_click)
        self.start_server_menu.add.button('Return to menu', pygame_menu.events.RESET)
        
        self.join_server_menu = pygame_menu.Menu(
            height=WINDOW_SIZE[1],
            theme=pygame_menu.themes.THEME_BLUE,
            title='Join Server',
            width=WINDOW_SIZE[0]
        )
        self.ip_address_text = self.join_server_menu.add.text_input(title='IP Address: ')
        self.username_client_text = self.join_server_menu.add.text_input(title='Username: ')
        self.join_server_menu.add.button('Join', self.join_click)
        self.join_server_menu.add.button('Return to menu', pygame_menu.events.RESET)

        self.play_menu.add.button('Host Server', self.start_server_menu)
        self.play_menu.add.button('Join Server', self.join_server_menu)
        self.play_menu.add.button('Return to menu', pygame_menu.events.BACK)
        
        main_theme = pygame_menu.themes.THEME_BLUE.copy()

        self.main_menu = pygame_menu.Menu(
            height=WINDOW_SIZE[1],
            theme=main_theme,
            title='Main Menu',
            width=WINDOW_SIZE[0]
        )

        self.main_menu.add.button(title='Play', action=self.play_menu)
        self.main_menu.add.button('Quit', pygame_menu.events.EXIT)

        self.main_background()
        
        while True:
            self.clock.tick(FPS)
            events = pygame.event.get()
            for event in events:
                if event.type == pygame.QUIT:
                    exit()

            if self.main_menu.is_enabled():
                self.main_menu.mainloop(self.surface, self.main_background, fps_limit=FPS)

            pygame.display.update()