import socket, ssl, threading, login

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

INVALID_LOGIN = 'AL INVALID_LOGIN'
INVALID_REGISTER = 'AL INVALID_REGISTER'

LOGGED_IN = 'LI SUCCESS'
REGISTER_SUCCESS = 'REG SUCCESS'

REPLY = 'R MESSAGE_SENT'
HEADER = 64
LOGIN = 'LI'

def decode(packet: str):
    packetl = packet.split()
    if packetl[0] == 'LI' or packetl[0] == 'REG' or packetl[0] == 'LO':
        return packetl
    else:
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
        self.token = ''

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

                    if msg_list[0] == 'LI' and self.username == '':
                        if len(msg_list) != 3:
                            self.conn.send(INVALID_LOGIN.encode(FORMAT))
                        else:
                            if msg_list[1] != '' and msg_list[2] != '': 
                            
                                output = login.login(msg_list[1], msg_list[2])
                                if output[0]:
                                    self.token = output[1]
                                    self.conn.send((LOGGED_IN + ' ' + output[1]).encode(FORMAT))
                                    self.username = msg_list[1]
                                    send_all(f'[SERVER] {self.username} connected!')
                                    print(f'[SERVER] {self.username} connected!')
                                else:
                                    self.conn.send(INVALID_LOGIN.encode(FORMAT))

                            else:
                                self.conn.send(INVALID_LOGIN.encode(FORMAT))
                    
                    elif msg_list[0] == 'REG' and self.username == '':
                        if len(msg_list) != 3:
                            self.conn.send(INVALID_REGISTER.encode(FORMAT))
                        else:
                            if msg_list[1] != '' and msg_list[2] != '':

                                output = login.register(msg_list[1], msg_list[2])
                                if output:
                                    self.conn.send(REGISTER_SUCCESS.encode(FORMAT))
                                else:
                                    self.conn.send(INVALID_REGISTER.encode(FORMAT))
                        
                    elif msg_list[0] == 'LO':

                        if len(msg_list) != 2:
                            raise Exception
                        else:
                            login.logout(self.token)
                            print(f'[SERVER] {self.username} disconnected!')
                            self.is_active = False
                            self.conn.close()
                            break

                    elif (msg_list[0] == 'LI' or msg_list[0] == 'REG') and self.username != '':

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
                            login.logout(self.token)
                            break
                    else:
                        print("ERROR")
                        raise Exception
            except ConnectionResetError:
                print(f"[SERVER] Client disconnected. {self.addr}")
                
                SERVER_THREADS.remove(self)
                if self.username != '':
                    print(f'[SERVER] {self.username} disconnected!')
                    send_all(f'[SERVER] {self.username} disconnected!')
                self.is_active = False
                self.conn.close()
                login.logout(self.token)
                break

            except ValueError:
                print(f"[SERVER] {self.addr} sent an unidentifiable packet.")
                self.conn.send(INVALID_PACKET.encode(FORMAT))
                self.conn.close()
                self.is_active = False
                login.logout(self.token)
                break

            except Exception as e:
                print(f"[SERVER] {self.addr} had an exception occur. {e}")
                self.conn.send(INVALID_PACKET.encode(FORMAT))
                self.conn.close()
                self.is_active = False
                login.logout(self.token)
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
