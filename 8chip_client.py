import socket
import keyboard
import pygame

keys = [
    '1', '2', '3', '4',
    'Q', 'W', 'E', 'R',
    'A', 'S', 'D', 'F',
    'Z', 'X', 'C', 'V']

SCREEN_WIDTH = 64
SCREEN_HEIGHT = 32
SCREEN_MULTIPLIER = 12
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
size = [SCREEN_WIDTH*SCREEN_MULTIPLIER, SCREEN_HEIGHT*SCREEN_MULTIPLIER]
screen = pygame.display.set_mode(size)
clock = pygame.time.Clock()


def check_keys():
    pressed_keys = b' '

    for key in keys:
        if keyboard.is_pressed(key):
            pressed_keys += str.encode(key)
    return pressed_keys

def show_display(DISPLAY):
    for y in range(SCREEN_HEIGHT):
        for x in range(SCREEN_WIDTH):
            if DISPLAY[x][y] == 1:
                pygame.draw.rect(screen, WHITE, [x*SCREEN_MULTIPLIER, y*SCREEN_MULTIPLIER, 1*SCREEN_MULTIPLIER, 1*SCREEN_MULTIPLIER])

def decode_display_data(display_data):
    DISPLAY = []
    for x_screen in range(SCREEN_WIDTH):
        new_column = []
        for y_screen in range(SCREEN_HEIGHT):
            new_column.append(0)
        DISPLAY.append(new_column)
    iter = 0
    for y in range(SCREEN_HEIGHT):
        for x in range(SCREEN_WIDTH):
            DISPLAY[x][y] = ((display_data >> (2048-iter)) & 1)
            iter += 1
    # show_display(DISPLAY)

    return DISPLAY




class Client:

    def __init__(self):
        self.ClientMultiSocket = None
        self.udpSocket = None
        self.DISPLAY = []
        self.res = None
        self.initialize_connection()
        self.initialize_display()

    def initialize_connection(self):
        self.ClientMultiSocket = socket.socket()
        self.udpSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        host = 'localhost'
        port = 2004

        print('Waiting for connection response')

        try:
            self.ClientMultiSocket.connect((host, port))
            self.udpSocket.bind((host, port+1))
        except socket.error as e:
            print(str(e))

        self.res = self.ClientMultiSocket.recv(1024)
        print(self.res.decode('utf-8'))

    def initialize_display(self):
        for x_screen in range(SCREEN_WIDTH):
            new_column = []
            for y_screen in range(SCREEN_HEIGHT):
                new_column.append(0)
            self.DISPLAY.append(new_column)


    def receive_udp(self):
        res = self.udpSocket.recv(2048)
        return res

    def game_loop(self):


        pygame.init()
        for event in pygame.event.get():  # User did something
            if event.type == pygame.QUIT:  # If user clicked close
                done = True  # Flag that we are done so we exit this loop


        done = False

        while not done:
            res = self.receive_udp()
            if res:
                res = int.from_bytes(res, 'little')
                if res == 0xFF:
                    self.ClientMultiSocket.send(check_keys())
                else:
                    clock.tick(1024)
                    for event in pygame.event.get():  # User did something
                        if event.type == pygame.QUIT:  # If user clicked close
                            done = True  # Flag that we are done so we exit this loop
                    screen.fill(BLACK)
                    DISPLAY = decode_display_data(res)
                    show_display(DISPLAY)
                    pygame.display.flip()


        # self.ClientMultiSocket.close()


client = Client()
client.game_loop()