'''
------------------------------------------------------------
Server module for api.python-chat.com. Free to use under the
GNU Public License specified in LICENSE file. Certificates
and other such server-specific things will need to be
replaced.
--------------------------------------------------------------------

--------------------------------------------------------------------
Import List:

socket module: Used for connection to server
ssl module: Used to wrap socket for secure communication
threading module: Used for managing server-threads. See class
           description for ServerThread below.
login module: Used to manage logins/registers/logouts for users
              on the server. See full description(s) in login.py
--------------------------------------------------------------------
'''

import socket
# import ssl
import threading
import login

'''
--------------------------------------------------------------------
Server-wide constants:
--------------------------------------------------------------------
Connection-related constants:

HOST: Specifies the hostname to use to
PORT: Specifies the port on HOST to open
FORMAT: Specify the format for the server. Make sure that
        the client knows the FORMAT variable.
CONTEXT: An SSL context. Specifies the protocol and loads
         cert-chain in CONTEXT.load_cert_chain()

SERVER: A socket. Wrapped using CONTEXT.wrap_socket(SERVER).
        Main connection for clients to connect to.

SERVER_THREADS: Array used by thread_manager class to destroy
                unused threads. See class description for full
                details
--------------------------------------------------------------------


--------------------------------------------------------------------
Packet-related constants:

AL-type packets:

DISCONNECT_MESSAGE: Sent to client to notify them to disconnect.
INVALID_PACKET: Garbled or unusable packet.
CLEAN_DISCONNECT: Let the client know disconnect was successful.
INVALID_LOGIN: An invalid login occurred. Either user was logged in
               or attempted to login twice or a login error occurred.
INVALID_REGISTER: User was already registered or a different error
                  occurred during registration.
INVALID_LOGOUT: User attempted to logout a user with a token that was
                their user's login-token.

Login-related packets (excluding INVALID_LOGIN, INVALID_REGISTER):

LOGGED_OUT: Successful logout.
LOGGED_IN: Successful login.
REG_SUCCESS: Successful register.
LI (Packet-type): LI packet to send to client.

Message-related packets/packet-types:

TYPE_MSG: A regular message. Will result in exception if user not
          logged in.
REPLY: Message was sent successfully.

Other packet-related constants:
HEADER: Specifies default-packet read size.
--------------------------------------------------------------------
'''

# Constant declarations:

DISCONNECT_MESSAGE = 'AL DISCONNECT'
CLEAN_DISCONNECT = 'AL DISCONNECTED'

INVALID_PACKET = 'AL INVALID_PACKET_DISCONNECTED'

INVALID_LOGIN = 'AL INVALID_LOGIN'
INVALID_REGISTER = 'AL INVALID_REGISTER'
INVALID_LOGOUT = 'AL INVALID_LOGOUT'

LOGGED_OUT = 'LO SUCCESS'
LOGGED_IN = 'LI SUCCESS'
REGISTER_SUCCESS = 'REG SUCCESS'

LOGIN = 'LI'

TYPE_MSG = 'M'
REPLY = 'R MESSAGE_SENT'

HEADER = 64
FORMAT = 'utf-8'

HOST = '0.0.0.0'
PORT = 500
ADDR = (HOST, PORT)

SERVER_THREADS = []

# SSL Init. Comment out to remove SSL implementation.

'''
CONTEXT = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
CONTEXT.load_cert_chain(certfile='/path/to/cert',
                        keyfile='/path/to/private-key')
'''
# Server init. Comment out SERVER = CONTEXT.wrap_socket(SERVER)
# to remove SSL implementation

SERVER = socket.socket(
    socket.AF_INET,
    socket.SOCK_STREAM
)

# SERVER = CONTEXT.wrap_socket(SERVER)

SERVER.bind(ADDR)
SERVER.listen(5)

'''
--------------------------------------------------------------------
decode(packet: str) function:
Decodes a packet and returns it by the type and
body of the given packet. Special cases include
LI, LO, and REG packets, where it returns packetl, which is
defined as packetl = packet.split()
--------------------------------------------------------------------
'''


def decode(packet: str):

    packetl = packet.split()

    if (

        packetl[0] == 'LI'
        or packetl[0] == 'REG'
        or packetl[0] == 'LO'

    ):
        return packetl

    else:

        string = ''

        for i in packetl[1:len(packetl)]:

            string += (f'{i} ')

        return [packetl[0], string.rstrip()]


'''
--------------------------------------------------------------------
send_all(msg: str) function:
Invokes the send function of a server_thread object in
the array SERVER_THREADS if the thread is active. Function
send transmits a TYPE_MSG packet to the client.
--------------------------------------------------------------------
'''


def send_all(msg: str):

    for i in SERVER_THREADS:

        if (

            i.is_active()

        ):

            i.send(msg)


'''
--------------------------------------------------------------------
thread_manager class:
Manages all running server threads. If a server_thread
object is inactive, invokes join on the thread and removes
it from SERVER_THREADS.
--------------------------------------------------------------------
'''


class thread_manager:

    def __init__(self):

        pass

    def init(self):

        while True:

            try:

                for i in SERVER_THREADS:

                    if (

                        i.is_active() is False

                    ):

                        SERVER_THREADS.remove(i)

                        i.get_thread().join()

            except Exception:

                pass


'''
--------------------------------------------------------------------
server_thread class:
A class to manage and handle a client. Instance is created
when a client connects, moved into a thread using the handle_client
function. Control is then moved to the thread_manager.
--------------------------------------------------------------------

--------------------------------------------------------------------
Main functions:
send(self, msg: str): Transmit data to a client as a TYPE_MSG
                      packet.

handle_client(self): Handles a client. Manages packets to/from
                     the client and handles login and messaging.
--------------------------------------------------------------------
'''


class server_thread:

    def __init__(

        self,
        conn,
        addr

    ):

        self.conn = conn
        self.addr = addr

        self.active = True

        self.username = ''
        self.token = ''

    def is_active(self):

        return self.active

    def get_thread(self):

        return self.thread

    def set_thread(self, thread: threading.Thread):

        self.thread = thread

    def send(self, msg: str):

        try:

            self.conn.send((f'M {msg}').encode(FORMAT))

        except Exception as f:

            print(f)

    def send_packet(

        self,
        packet_type: str,

    ):

        try:

            self.conn.send(packet_type.encode(FORMAT))

        except Exception as e:

            print(e)

    def send_packet_with_body(

        self,
        packet_type: str,
        packet_body: str

    ):

        try:

            self.conn.send((f'{packet_type} {packet_body}').encode(FORMAT))

        except Exception as e:

            print(e)

    def handle_client(self):

        print(f'[SERVER] New connection: [{self.addr}] connected.')

        CLIENT_CONNECTED = True

        while CLIENT_CONNECTED:

            try:

                msg_length = self.conn.recv(HEADER).decode(FORMAT)

                if msg_length:

                    msg_length = int(msg_length)

                    if msg_length > 512:

                        self.send_packet(INVALID_PACKET)

                    msg = self.conn.recv(msg_length).decode(FORMAT)

                    msg_list = decode(msg)

                    # Login logic:

                    if msg_list[0] == 'LI' and self.username == '':

                        if len(msg_list) != 3:

                            self.send_packet(INVALID_LOGIN)

                        else:

                            if(

                                msg_list[1] != ''
                                and msg_list[2] != ''

                            ):

                                output = login.login(

                                    msg_list[1],
                                    msg_list[2]

                                )

                                if output[0]:

                                    self.token = output[1]

                                    self.send_packet_with_body(

                                        LOGGED_IN,
                                        self.token

                                    )

                                    self.username = msg_list[1]

                                    print(

                                        f'[SERVER] {self.username} connected!'

                                    )

                                    send_all(

                                        f'[SERVER] {self.username} connected!'

                                    )

                                else:

                                    self.send_packet(INVALID_LOGIN)

                    elif msg_list[0] == 'REG' and self.username == '':

                        if len(msg_list) != 3:

                            self.send_packet(INVALID_REGISTER)

                        else:

                            if (

                                msg_list[1] != ''
                                and msg_list[2] != ''

                            ):

                                output = login.register(

                                    msg_list[1],
                                    msg_list[2]

                                )

                                if output:

                                    self.send_packet(REGISTER_SUCCESS)

                                    print(

                                        f"{self.addr} registered",
                                        "the username",
                                        f"{msg_list[1]}!"
                                    )

                                else:

                                    self.send_packet(INVALID_REGISTER)

                    elif msg_list[0] == 'LO':

                        if len(msg_list) != 2:

                            self.send_packet(INVALID_LOGOUT)

                        else:

                            if msg_list[2] != self.token:

                                self.send_packet(INVALID_LOGOUT)

                            else:

                                login.logout(self.token)

                                print(

                                    f"[SERVER] {self.username} disconnected!"

                                )

                                send_all(

                                    f"[SERVER] {self.username} " +
                                    "disconnected!"

                                )

                                self.active = False

                                self.conn.close()

                            CLIENT_CONNECTED = False

                    elif (

                        msg_list[0] == 'LI'
                        or msg_list[0] == 'REG'
                        or msg_list[0] == 'LO'

                    ):

                        raise Exception

                    # Message logic:

                    elif msg_list[0] == TYPE_MSG:

                        if len(msg_list[1]) > 0:

                            if self.username != '':

                                print(

                                    f"[{self.username}] {msg_list[1]}"

                                )

                                self.send_packet(REPLY)

                                send_all(f"[{self.username}] {msg_list[1]}")

                            else:

                                raise Exception

                    # AL Logic

                    elif msg_list[0] == 'AL':

                        if msg_list[1] == 'DISCONNECT':

                            print(

                                f"[SERVER] {self.username} disconnected1"

                            )

                            SERVER_THREADS.remove(self)

                            self.active = False

                            self.conn.close()

                            login.logout(self.token)

                            CLIENT_CONNECTED = False

                    else:

                        print(

                            "[SERVER] Unknown packet sent by",
                            f"{self.addr}."

                        )

                        raise Exception

            except ConnectionResetError:

                print(

                    f'[SERVER] Client disconnected. {self.addr}'

                )

                SERVER_THREADS.remove(self)

                if self.username != '':

                    print(

                        f'[SERVER] {self.username} disconnected!'

                    )

                    send_all(f'[SERVER] {self.username} disconnected!')

                self.active = False

                self.conn.close()

                login.logout(self.token)

                CLIENT_CONNECTED = False

            except ValueError:

                print(

                    f'[SERVER] {self.addr} sent an unidentifiable packet.'

                )

                if self.username != '':

                    print(

                        f'[SERVER] {self.username} disconnected!'

                    )

                    send_all(f'[SERVER] {self.username} disconnected!')

                self.send_packet(INVALID_PACKET)

                SERVER_THREADS.remove(self)

                self.active = False

                self.conn.close()

                login.logout(self.token)

                CLIENT_CONNECTED = False

            except Exception as e:

                print(

                    f'[SERVER] {self.addr} had an exception occur. {e}'

                )

                if self.username != '':

                    print(

                        f'[SERVER] {self.username} disconnected!'

                    )

                    send_all(f'[SERVER] {self.username} disconnected!')

                self.send_packet(INVALID_PACKET)

                SERVER_THREADS.remove(self)

                self.active = False

                self.conn.close()

                login.logout(self.token)

                CLIENT_CONNECTED = False


'''
--------------------------------------------------------------------
def start(): Function used to initialize server. Accepts
             clients and handles them.
--------------------------------------------------------------------
'''


def start():

    global SERVER

    global SERVER_THREADS

    threadmanager = thread_manager()

    tm_thread = threading.Thread(target=threadmanager.init)

    tm_thread.start()

    print(

        f"[SERVER] Server started, listening on port {PORT}"

    )

    while True:

        try:

            CONNECTION, ADDRESS = SERVER.accept()

            HANDLER = server_thread(CONNECTION, ADDRESS)

            H_THREAD = threading.Thread(target=HANDLER.handle_client,)

            H_THREAD.setDaemon(True)

            H_THREAD.start()

            HANDLER.set_thread(H_THREAD)

            SERVER_THREADS.append(HANDLER)

            print(

                "[SERVER] Active connections:",
                f"{threading.activeCount() - 2}"

            )

        except Exception as e:

            print(

                f"Exception occurred during SSL connection. Aborting: {e}"

            )


print(

    '[SERVER] Initiating.'

)

start()

# EOF
