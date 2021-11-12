import socket
import os
from _thread import *
import time

def multi_threaded_client(connection):
    connection.send(str.encode('Server is working:'))
    while True:
        data = connection.recv(2048)
        response = 'Server message: ' + data.decode('utf-8')
        if not data:
            break
        connection.sendall(str.encode(response))
    connection.close()


ServerSideSocket = socket.socket()
host = '127.0.0.1'
port = 2004
ThreadCount = 0

try:
    ServerSideSocket.bind((host, port))
except socket.error as e:
    print(str(e))

print('Socket is listening..')
ServerSideSocket.listen()


def obtain_keystrokes(connection):
    connection.send(int.to_bytes(0xFF, 1, 'little'))
    res = connection.recv(2048)
    while not res:
        res = connection.recv
    print(res)
    # while True:
    #     data = connection.recv(2048)
    #     response = 'Server message: ' + data.decode('utf-8')
    #     if not data:
    #         break
    #     connection.sendall(str.encode(response))
    # connection.close()


def start_game(clients):
    while True:
        time.sleep(0.2)
        for client in clients:
            start_new_thread(obtain_keystrokes, (client, ))
        # start_new_thread(obtain_keystrokes, (Client,))


def start_server():
    clients = []
    while len(clients) < 1:
        time.sleep(0.1)
        client, address = ServerSideSocket.accept()
        print('Connected to: ' + address[0] + ':' + str(address[1]))
        clients.append(client)
        client.send(str.encode('Welcome to the game Player {}'.format(len(clients))))
        print(clients)

    start_game(clients)
    ServerSideSocket.close()

start_server()