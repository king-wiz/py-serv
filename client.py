import socket
import threading
import ssl
import time
import OpenSSL

SERVER = 'api.python-chat.com'
PORT = 500

LOGGED_IN = False

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

print(f"Connecting to {SERVER}...")

client = None

try:
    context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
    addr = (SERVER, PORT)
    client = context.wrap_socket(sock)
    client.connect(addr)

except Exception as e:

    print(f"Error while connecting to {SERVER}. Is the connection offline? " + str(e))
    time.sleep(5)
    quit()

print(f"Connected to {SERVER}.")


FORMAT = 'utf-8'
CONNECTED = True

MAX_PACKET_SIZE = 512
ALERT_DISCONNECT = 'AL DISCONNECT'
M_FORMAT = 'M'

USERNAME = ''
SERVER_DISCONNECT_CLEAN = 'AL DISCONNECTED'


def decode(packet: str):
    packetl = packet.split()
    if packetl[0] != 'LI' and packetl[1] != 'REG': 
        string = ''
        for i in packetl[1:len(packetl)]:
            string += (f'{i} ')
    
    
        return [packetl[0], string.rstrip()]
    else:

        return packetl

def encode(msg: str):

    length = len(f'M {msg}')

    return [length, (f'M {msg}')]
            

class clientn:

    def __init__(self, client, addr):
        self.conn = client
        self.addr = addr
        self.connected = True
        self.token = ''

    def send(self, msg: str):
        try:
            encoded = encode(msg)
            self.conn.send(str(encoded[0]).encode(FORMAT))
            time.sleep(0.1)
            self.conn.send(str(encoded[1]).encode(FORMAT))
        except Exception as e:
            print(f"[CLIENT] Bad send. Disconnecting. {e}")
            self.conn.close()
            CONNECTED = False
            time.sleep(5)

    def get_token(self):
        return self.token

    def send_raw(self, msg):
        try:
            self.conn.send(str(len(msg)).encode(FORMAT))
            time.sleep(0.1)
            self.conn.send(msg.encode(FORMAT))
        except Exception as e:
            print(f"[CLIENT] Bad send. Disconnecting. {e}")
            self.conn.close()
            CONNECTED = False
            time.sleep(5)

    def disconnect(self):
        try:
            self.send(ALERT_DISCONNECT)
            reply = decode(self.conn.recv(512).decode(FORMAT))
            s_type = reply[0]
            smessage = reply[1]
            if s_type == 'AL' and smessage == 'DISCONNECTED':
                print("[CLIENT] Clean disconnect. Shutting down socket/threads.")
                self.conn.close()
                CONNECTED = False
                time.sleep(5)
        except Exception:
            print("[CLIENT] Forced disconnect. Shutting down.")
            self.conn.close()
            CONNECTED = False
            time.sleep(5)
            
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
                        print("Logged in! Type !disconnect to logout.")
                    elif m_type == 'REG' and message == 'SUCCESS':
                        print("Username registered! Press 1 to log in!")
                    elif m_type == 'AL' and message == 'INVALID_LOGIN':
                        print("Invalid credentials!")
                    elif m_type == 'AL' and message == 'INVALID_REGISTER':
                        print("Oops! The username you want is taken or invalid.")
                    elif m_type == 'AL' and message =='INVALID_PACKET_DISCONNECTED':
                        print("Forced disconnect, shutting down.")
                        self.conn.close()
                        CONNECTED = False
                        time.sleep(5)
                    else:
                        pass
            except Exception:
                print("Connection error: Socket closed")
                CONNECTED = False
                time.sleep(5)
           


clientn = clientn(client, addr)
thread = threading.Thread(target=clientn.read)
thread.start()

print("Welcome to PyChat!")
while not LOGGED_IN:
    choice = input("Type '1' for login or '2' to register an account: ")
    if choice == '1':
        username = input("Enter username: ")
        password = input("Enter password: ")
        clientn.send_raw(f'LI {username} {password}')
        time.sleep(2.5)
    elif choice == '2':
        username = input("Enter username: ")
        password = input("Enter password: ")
        clientn.send_raw(f'REG {username} {password}')
        time.sleep(2.5)
    else:
        print("Invalid response!")
        time.sleep(2.5)
        
def disconnect(token):
    clientn.send_raw(f"LO {token}")

while CONNECTED:
    msg = input()
    if len(msg) > 512:
        print("Message too long!")
        time.sleep(1)
    elif len(msg) == 0:
        print("no message entered")
        time.sleep(1)
    elif msg == '!disconnect':
        disconnect(clientn.get_token())
        print(f"Disconnected from {SERVER}!")
    else:
        clientn.send(f'{msg}')






