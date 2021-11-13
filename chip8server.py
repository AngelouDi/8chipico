import socket
from chippico8 import Chip8
import os
import threading
import time

SCREEN_WIDTH = 64
SCREEN_HEIGHT = 32

def multi_threaded_client(connection):
    connection.send(str.encode('Server is working:'))
    while True:
        data = connection.recv(2048)
        response = 'Server message: ' + data.decode('utf-8')
        if not data:
            break
        connection.sendall(str.encode(response))
    connection.close()


def show_display_terminal(DISPLAY):
    display_buffer = ""
    display_buffer += "."
    for x in range(SCREEN_WIDTH):
        display_buffer += '_'
    display_buffer += '\n'
    for y in range(SCREEN_HEIGHT):
        display_buffer += '|'
        for x in range(SCREEN_WIDTH):
            if DISPLAY[x][y] == 1:
                display_buffer += '▓'
            else:
                display_buffer += ' '

        display_buffer += '\n'

    clearConsole = lambda: os.system('cls' if os.name in ('nt', 'dos') else 'clear')
    clearConsole()
    print(display_buffer)



def encode_display(display):
    data = 0
    for y in range(SCREEN_HEIGHT):
        for x in range(SCREEN_WIDTH):
            data |= display[x][y] & 1
            data <<= 1
    return int.to_bytes(data, 2048, 'little')






class Server:

    def __init__(self):
        self.ACTIVE_KEYS = []

        self.ServerSideSocket = socket.socket()
        host = '192.168.1.3'
        port = 2004

        try:
            self.ServerSideSocket.bind((host, port))
        except socket.error as e:
            print(str(e))

        print('Socket is listening..')
        self.ServerSideSocket.listen()

    def start_server(self):
        clients = []
        while len(clients) < 2:
            time.sleep(0.1)
            client, address = self.ServerSideSocket.accept()
            print('Connected to: ' + address[0] + ':' + str(address[1]))
            clients.append(client)
            client.send(str.encode('Welcome to the game Player {}'.format(len(clients))))
            # print(clients)

        self.start_game(clients)
        # self.ServerSideSocket.close()


    def start_game(self, clients):
        emu = Chip8()
        emu.load_rom("pong2.ch8")
        while True:
            self.ACTIVE_KEYS = []
            for client in clients:
                # self.obtain_keystrokes(client)
                thread = threading.Thread(target=self.obtain_keystrokes(client), group=None)
                thread.start()  #possibly neεding join or locking for accessing active keys
            emu.ACTIVE_KEYS = self.ACTIVE_KEYS
            display_data = encode_display(emu.get_display())
            if emu.updated_display:
                for client in clients:
                    threading.Thread(target=client.sendto(display_data), group=None)

                print(self.ACTIVE_KEYS)

            emu.set_keys(self.ACTIVE_KEYS)
            # emu.update_keys()
            emu.tick()


    def obtain_keystrokes(self, connection):
        connection.send(int.to_bytes(0xFF, 1, 'little'))
        res = connection.recv(2048)
        while not res:
            connection.send(int.to_bytes(0xFF, 1, 'little'))
            res = connection.recv(2048)
        keys = res.decode('utf-8')
        for key in keys:
            if key not in self.ACTIVE_KEYS:
                self.ACTIVE_KEYS.append(key)
                print(key)
        return

        # while True:
        #     data = connection.recv(2048)
        #     response = 'Server message: ' + data.decode('utf-8')
        #     if not data:
        #         break
        #     connection.sendall(str.encode(response))
        # connection.close()


server = Server()
server.start_server()