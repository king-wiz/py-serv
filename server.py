import socket, ssl, threading

HOST, PORT = '0.0.0.0', 500
ADDR = (HOST, PORT)
FORMAT = 'utf-8'
context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
context.load_cert_chain(certfile='/etc/letsencrypt/live/api.python-chat.com/fullchain.pem', keyfile='/etc/letsencrypt/live/api.python-chat.com/privkey.pem')

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s = context.wrap_socket(s)
s.bind(ADDR)
s.listen(5)

SERVER_THREADS = []

#Client-from packet constants:
DISCONNECT_MESSAGE = 'AL DISCONNECT'
TYPE_MSG = 'M'
MAX_PACKET_SIZE = 512

INVALID_PACKET = 'AL INVALID_PACKET_DISCONNECTED'
CLEAN_DISCONNECT = 'AL DISCONNECTED'
REPLY = 'R MESSAGE_SENT'

SETUSERNAME = 'SUN'

def decode(packet: str):
    packetl = packet.split()
    string = ''
    for i in packetl[1:len(packetl)]:
        string += (f'{i} ')
    return [packetl[0], string.rstrip()]

class ThreadManager:

    def __init__(self):
        self.ACTIVE = True

    def init(self):
        
        while self.ACTIVE:
            try:
                for i in SERVER_THREADS:

                    if i.is_active == False:
                        SERVER_THREADS.remove(i)
                        i.get_thread().join()
            except Exception:
                pass

def send_all(msg):

    for i in SERVER_THREADS:

        if i.is_active == True:
            i.send(msg)

class ServerThread:

    def __init__(self, conn, addr, length, threadmanager):
        self.conn = conn
        self.addr = addr
        self.length = length
        self.is_active = True
        self.threadmanager = threadmanager
        self.username = ''

    def is_active(self):
        return self.is_active
        
    def get_thread(self):
        return self.thread

    def set_thread(self, thread):
        self.thread = thread

    def get_length(self):
        return self.length


    def send(self, msg: str):
        try:
            self.conn.send((f'M {msg}').encode(FORMAT))
        except Exception as e:
            print(e)
            

    def handle_client(self):
        print(f"[SERVER] New connection: [{self.addr}] connected.")
        connected = True
    
        while connected:
            try:
                msg_length = self.conn.recv(HEADER).decode(FORMAT)
                if msg_length:
                    msg_length = int(msg_length)
                    msg = self.conn.recv(msg_length).decode(FORMAT)
                    msg_list = decode(msg)
                    
                    #SUN logic:

                    if msg_list[0] == 'SUN' and self.username == '':

                        if msg_list[1] != '': 
                            self.username = msg_list[1]
                            print(f'[SERVER] {self.addr} set username to {self.username}.')
                            self.conn.send(f'SUN SUCCESS'.encode(FORMAT))
                            send_all(f'[SERVER] {self.username} connected!')
                        else:
                            raise Exception

                    elif msg_list[0] == 'SUN' and self.username != '':

                        raise Exception

                    elif msg_list[0] == 'M':
                        if self.username != '':
                            print(f"[{self.username}] {msg_list[1]}")
                            self.conn.send(REPLY.encode(FORMAT))
                            send_all('[' + self.username + '] ' + msg_list[1])
                        else:
                            raise Exception

                    elif msg_list[0] == 'AL':
                        #Alerts
                        if msg_list[1] == 'DISCONNECT':
                            print(f'[SERVER] {self.username} disconnected!')
                            SERVER_THREADS.remove(self)
                            self.is_active = False
                            self.conn.close()
                            break
                    else:
                        print("ERROR")
                        raise Exception
            except ConnectionResetError:
                print(f"[SERVER] Client disconnected. {self.addr}")
                
                SERVER_THREADS.remove(self)
                send_all(f'[SERVER] {self.username} disconnected!')
                self.is_active = False
                self.conn.close()
                break

            except ValueError:
                print(f"[SERVER] {self.addr} sent an unidentifiable packet.")
                self.conn.send(INVALID_PACKET.encode(FORMAT))
                self.conn.close()
                self.is_active = False
                break

            except Exception as e:
                print(f"[SERVER] {self.addr} had an exception occur. {e}")
                self.conn.send(INVALID_PACKET.encode(FORMAT))
                self.conn.close()
                self.is_active = False
                break
        

def start():

    global s

    threadmanager = ThreadManager()
    threadmanagerrun = threading.Thread(target=threadmanager.init)
    threadmanagerrun.start()

    print(f"[SERVER] Server is listening on {HOST}")

    while True:
        try:
            conn, addr = s.accept()
            cv = ServerThread(conn, addr, len(SERVER_THREADS)+1, threadmanager)
            thread = threading.Thread(target=cv.handle_client,)
            thread.setDaemon(True)
            thread.start()

            cv.set_thread(thread)

            SERVER_THREADS.append(cv)   

        #Clean disconnected clients
            print(f"[SERVER] Active connections: {threading.activeCount() - 2}") #active count minus 2 because of threadmanager and main thread
        except Exception  as e:
            print(f'Exception occurred during SSL connection. Aborting connection.')
            

        
print("[SERVER] Starting")
start()
