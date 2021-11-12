import socket
import keyboard

keys = [
    '1', '2', '3', '4',
    'Q', 'W', 'E', 'R',
    'A', 'S', 'D', 'F',
    'Z', 'X', 'C', 'V']


def check_keys():
    pressed_keys = b''

    for key in keys:
        if keyboard.is_pressed(key):
            pressed_keys += str.encode(key)
    return pressed_keys


ClientMultiSocket = socket.socket()
host = '127.0.0.1'
port = 2004

print('Waiting for connection response')

try:
    ClientMultiSocket.connect((host, port))
except socket.error as e:
    print(str(e))

res = ClientMultiSocket.recv(1024)
print(res.decode('utf-8'))


while True:
    res = ClientMultiSocket.recv(2048)
    if res:
        res = int.from_bytes(res, 'little')
        if res == 0xFF:
            ClientMultiSocket.send(check_keys())

ClientMultiSocket.close()