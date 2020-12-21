import socket
import threading
import ssl

SERVER = 'api.python-chat.com'
PORT = 500



sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

print(f"Connecting to {SERVER}...")

context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)

addr = (SERVER, PORT)
sock.connect(addr)
wrappedSocket = context.wrap_socket(sock)
client = wrappedSocket

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
    string = ''
    for i in packetl[1:len(packetl)]:
        string += (f'{i} ')
    
    
    return [packetl[0], string.rstrip()]

def encode(msg: str):

    length = len(f'M {msg}')

    return [length, (f'M {msg}')]
            

class clientn:

    def __init__(self, client, addr):
        self.conn = client
        self.addr = addr
        self.connected = True

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

    def send_raw(self, msg):
        try:
            self.conn.send(str(len(msg)).encode(FORMAT))
            time.sleep(0.1)
            self.conn.send(msg.encode(FORMAT))
        except Exception as e:
            print(f"[CLIENT] Bad send. Disconnecting. {e}")
            self.conn.close()
            CONNECTED = False

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
        except Exception:
            print("[CLIENT] Forced disconnect. Shutting down.")
            self.conn.close()
            CONNECTED = False
            
    def read(self):
        global CONNECTED
        while CONNECTED:
           
                msg = self.conn.recv(512).decode(FORMAT)
                if msg:
                    array = decode(msg)
                    message = array[1]
                    m_type = array[0]
                    if m_type == 'M':
                        print(f'{message}\n')
                        time.sleep(0.1)
                    elif m_type == 'R' and message == 'MESSAGE_SENT':
                        pass
                    elif m_type == 'SUN' and message == 'SUCCESS':
                        print("Username set!")
                    elif m_type == 'AL' and message =='INVALID_PACKET_DISCONNECTED':
                        print("Forced disconnect, shutting down.")
                        self.conn.close()
                        CONNECTED = False
                    else:
                        pass

           


username = input("Enter a username: ")
USERNAME = username

clientn = clientn(client, addr)
thread = threading.Thread(target=clientn.read)
thread.start()

setusername = 'SUN ' + USERNAME
length = len(setusername)



clientn.send_raw(setusername)

while CONNECTED:
    msg = input()
    if len(msg) > 512:
        print("Message too long!")
    else:
        clientn.send(f'{msg}')





