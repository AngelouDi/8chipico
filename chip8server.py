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
        self.udpSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        host = '192.168.1.3'
        port = 2004

        try:
            self.ServerSideSocket.bind((host, port))
            self.udpSocket.bind((host, port+1))
        except socket.error as e:
            print(str(e))

        print('Socket is listening..')
        self.ServerSideSocket.listen()

    def start_server(self):
        clients = []
        while len(clients) < 1:
            time.sleep(0.1)
            client, address = self.ServerSideSocket.accept()
            print('Connected to: ' + address[0] + ':' + str(address[1]))
            clients.append({"client": client, "address": address})
            # clients.append(client)
            client.send(str.encode('Welcome to the game Player {}'.format(len(clients))))
            # print(clients)

        self.start_game(clients)
        # self.ServerSideSocket.close()


    def start_game(self, clients):
        emu = Chip8()
        emu.load_rom("pong2.ch8")
        while True:
            self.ACTIVE_KEYS = []
            for client_obj in clients:
                # self.obtain_keystrokes(client)
                thread = threading.Thread(target=self.obtain_keystrokes(client_obj), group=None)
                thread.start()  #possibly neεding join or locking for accessing active keys
            emu.ACTIVE_KEYS = self.ACTIVE_KEYS
            display_data = encode_display(emu.get_display())
            if emu.updated_display:
                for client_obj in clients:
                    threading.Thread(target=client_obj["client"].send(display_data), group=None)

                print(self.ACTIVE_KEYS)

            emu.set_keys(self.ACTIVE_KEYS)
            # emu.update_keys()
            emu.tick()


    def obtain_keystrokes(self, client_obj):
        print("{} {}".format(client_obj["address"][0], client_obj["address"][1]))
        self.udpSocket.sendto(int.to_bytes(0xFF, 1, 'little'), (client_obj["address"][0], (client_obj["address"][1])))
        # client_obj.send(int.to_bytes(0xFF, 1, 'little')
        res = client_obj["client"].recv(2048)
        while not res:
            client_obj["client"].send(int.to_bytes(0xFF, 1, 'little'))
            res = client_obj["client"].recv(2048)
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