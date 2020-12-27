'''
--------------------------------------------------------------------

Client for connecting to api.python-chat.com. Modify anything here
for added QAL or functionality. DM red red#0001 to report bugs and
security vulnerabilities.

--------------------------------------------------------------------
'''

import socket
import threading
# import ssl
import time

FORMAT = 'utf-8'
CONNECTED = False

ALERT_DISCONNECT = 'AL DISCONNECT'
TYPE_MSG = 'M'

USERNAME = ''
SERVER_DISCONNECT_CLEAN = 'AL DISCONNECTED'

SERVER = 'localhost'
PORT = 500
ADDR = (SERVER, PORT)

LOGGED_IN = False

CLIENT = socket.socket(socket.AF_INET, socket.SOCK_STREAM)


def decode(packet: str):

    packetl = packet.split()

    if packetl[0] != 'LI' and packetl[0] != 'REG':

        string = ''

        for i in packetl[1:len(packetl)]:

            string += (f'{i} ')

        return [packetl[0], string.rstrip()]

    else:

        return packetl


def encode(msg: str):

    length = len(f'M {msg}')

    return [length, (f'M {msg}')]


class python_client:

    def __init__(self, conn, addr):

        self.conn = conn
        self.addr = addr
        self.token = ''

    def send(self, msg: str):

        try:

            encoded = encode(msg)

            self.conn.send(str(encoded[0]).encode(FORMAT))

            time.sleep(0.1)

            self.conn.send(str(encoded[1]).encode(FORMAT))

        except Exception:

            global CONNECTED

            print('[CLIENT] Bad send. Disconnected.')

            self.conn.close()

            CONNECTED = False

            time.sleep(5)

            quit()

    def get_token(self):

        return self.token

    def send_raw(self, packet):

        global CONNECTED

        try:

            self.conn.send(str(len(packet)).encode(FORMAT))

            time.sleep(0.1)

            self.conn.send(packet.encode(FORMAT))

        except Exception:

            print('[CLIENT] Bad send. Disconnected.')

            self.conn.close()

            CONNECTED = False

            time.sleep(5)

    def logout(self):

        global CONNECTED, LOGGED_IN

        self.send_raw(f"LO {self.token}")
        CONNECTED = False
        LOGGED_IN = False

        print("You have logged out!")

    def disconnect(self, token: str):

        self.send_raw('AL DISCONNECT')

    def read(self):

        global CONNECTED, LOGGED_IN

        while CONNECTED:

            try:

                msg = self.conn.recv(512).decode(FORMAT)

                if msg:

                    array = decode(msg)

                    message = array[1]

                    m_type = array[0]

                    if m_type == 'M' and LOGGED_IN:

                        print(f'{message}\n')
                        time.sleep(0.1)

                    elif m_type == 'R' and message == 'MESSAGE_SENT':

                        pass

                    elif m_type == 'LI' and message == 'SUCCESS':

                        self.token = array[2]
                        LOGGED_IN = True
                        print('Logged in! Type !disconnect to logout.')

                    elif m_type == 'REG' and message == 'SUCCESS':

                        print("Username registered. Press 1 to log in!")

                    elif m_type == 'LO' and message == 'SUCCESS':

                        print("Logged out!")
                        time.sleep(2)
                        quit()

                    elif m_type == 'AL' and message == 'INVALID_LOGIN':

                        print("Invalid credentials!")

                    elif m_type == 'AL' and message == 'INVALID_REGISTER':

                        print(

                            "Username was already taken! Try a different one!"

                        )

                    elif (
                        m_type == 'AL' and
                        message == 'INVALID_PACKET_DISCONNECTED'
                    ):

                        print('Forced disconnect, shutting down.')

                        CONNECTED = False

                        time.sleep(5)

                        quit()

                    else:

                        pass

            except Exception:

                print("Connection error: Socket closed.")

                CONNECTED = False

                time.sleep(5)


print(f'Connection to {SERVER}...')

try:

    # context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
    # CLIENT = context.wrap_socket(CLIENT)
    CLIENT.connect(ADDR)

except Exception:

    print(
        f'Error while connecting to {SERVER}.',
        'Is the connection offline?'
    )

print(f"Connected to {SERVER}")

CONNECTED = True

CLIENTX = python_client(CLIENT, ADDR)

THREAD = threading.Thread(target=CLIENTX.read,)

THREAD.start()

while not LOGGED_IN:

    check_var = False

    choice = input(

        "Type '1' for login or '2' to register an account: "

    )

    if choice == '1':

        username = input("Enter username: ")

        if len(username) > 16 or len(username.split()) > 1:

            print("Username too long or is invalid!")
            check_var = True

        if not check_var:
            password = input("Enter password: ")
            if len(password.split()) == 1:
                CLIENTX.send_raw(f'LI {username} {password}')
                time.sleep(1)

            else:

                print("Password may not contain whitespace!")

    elif choice == '2':

        username = input("Enter username: ")

        if len(username) > 16 or len(username.split()) > 1:

            print("Username too long or is invalid!")
            check_var = True
            time.sleep(2.5)

        if not check_var:
            password = input("Enter password: ")
            if len(password.split()) == 1:
                CLIENTX.send_raw(f'REG {username} {password}')
                time.sleep(1)

            else:

                print("Password may not contain whitespace!!")

    else:

        print("Invalid option!")

while LOGGED_IN:

    msg = input()

    if len(msg) > 512:

        print("Message too long!")
        time.sleep(1)

    elif msg == '!disconnect':

        CLIENTX.logout()

    else:

        CLIENTX.send(msg)


# EOF
