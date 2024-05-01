import queue
import socket
import sys
import threading
import subprocess
import platform

import pygame
import pygame_menu
from caro_game.main import Caro
from setting_menu import WINDOW_SIZE

clickQueue = queue.Queue()

class Client:
    def __init__(self, host, port, username, competitor_name, sock):
        self.host = host
        self.port = port
        self.username = username
        self.competitor_name = competitor_name
        self.sock = sock
        self.gui = PlaySurface(self.sock, self.host, self.port, username, self.competitor_name, False)
        self.gui.game_gui_window.clicked = True
        self.message_queue = queue.Queue()
        self.close_queue = queue.Queue()
        threading.Thread(target=self.receive, daemon=True).start()
        self.gui.run()

    def receive(self):
        while True:
            try:
                data, addr = self.sock.recvfrom(1024)
                if data == b'Play again':
                    self.gui.game_gui_window.game.play_again()
                    continue
                message = data.decode('utf-8').split(':::')
                print(message)
                if message[0] == 'Game':
                    print(str(message[0]) + " " + str(message[1]) + " " + str(message[2]))
                    x = int(message[1])
                    y = int(message[2])
                    clickQueue.put(f'Clicked:::{x}:::{y}')
            except OSError as e:
                print(str(e))
                self.sock.close()
                self.close_queue.put('Close connection')
                break

class Server:
    def __init__(self, host, port, username, surface):
        self.host = host
        self.port = port
        self.username = username
        self.competitor_name = 'Player 2'
        self.connected = False

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind((self.host, self.port))

        loading = pygame_menu.Menu(
            height=WINDOW_SIZE[1],
            theme=pygame_menu.themes.THEME_BLUE,
            title='Waiting for client',
            width=WINDOW_SIZE[0]
        )

        os_name = platform.system()

        if os_name == 'Windows':
            loading.add.label(title=f'IP Address:{socket.gethostbyname(socket.gethostname())}')
        else:
            process = subprocess.Popen(['ifconfig'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            output, error = process.communicate()
            ip_address = None
            for line in output.decode('utf-8').split('\n'):
                if 'inet ' in line and '127.0.0.1' not in line:
                    ip_address = line.strip().split(' ')[1]
                    break
            loading.add.label(title=f'IP Address: {ip_address}')

        threading.Thread(target=self.accepted_connect).start()
        
        while True:
            events = pygame.event.get()
            for event in events:
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
            if self.connected:
                break
            if loading.is_enabled():
                loading.update(events)
                loading.draw(surface)
            pygame.display.update()
        loading.disable()
        self.gui = PlaySurface(self.sock, self.addr[0], self.addr[1], self.username, self.competitor_name, True)
        self.message_queue = queue.Queue()
        self.close_queue = queue.Queue()
        threading.Thread(target=self.receive, daemon=True).start()
        self.gui.run()
	  
    def accepted_connect(self):
        while True:
            try:
                data, self.addr = self.sock.recvfrom(1024)
                message = data.decode('utf-8').split(':::')
                if message[0] == 'Connected':
                    self.connected = True
                    self.competitor_name = str(message[1])
                    self.sock.sendto(f'Connected:::{self.username}'.encode('utf-8'), self.addr)
                    break
                else:
                    self.connected = False
            except Exception:
                break

    def receive(self):
        while True:
            try:
                data, addr = self.sock.recvfrom(1024)
                if data == b'Play again':
                    self.gui.game_gui_window.game.play_again()
                    continue
                message = data.decode('utf-8').split(':::')
                print(message)
                if message[0] == 'Game':
                    x = int(message[1])
                    y = int(message[2])
                    clickQueue.put(f'Clicked:::{x}:::{y}')
            except OSError as e:
                print(str(e))
                self.sock.close()
                self.close_queue.put('Close connection')
                break

class PlaySurface:
    def __init__(self, connection, host, port, username, competitor_name=None, is_host=True):
        self.connection = connection
        self.game_gui_window = Caro(connection, host, port, username, competitor_name, is_host)

    def run(self):
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                    self.connection.close()
                    pygame.quit()
                    sys.exit()
                self.game_gui_window.event_loop(event)
                self.game_gui_window.mouse_event()

            if not clickQueue.empty():
                message = str(clickQueue.get()).split(":::")
                if self.game_gui_window.game.left_mouse_click(int(message[1]), int(message[2])):
                    self.game_gui_window.clicked = False
            
            self.game_gui_window.clock.tick(60)
            self.game_gui_window.game.run()
            pygame.display.update()

    def close(self):
        self.connection.close()
        pygame.quit()
        sys.exit()
