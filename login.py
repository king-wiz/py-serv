'''
--------------------------------------------------------------------

MYSQL BACKEND:

Implements LOGIN, LOGOUT, and REGISTER functionality. Uses MySQL
queries to do this and connects to a remote database storing the
credentials.

Imports:

mysql.connector: MySQL connector to remote database
bcrypt: Salt module
hashlib: Hashing module
uuid: Used to generate login-tokens.

Constants:

SERVER: Specifies an off-site database to connect to

MYSQL_SOCKET: Socket for MySQL to read/recieve data from
CURSOR: Used to send queries to SERVER

--------------------------------------------------------------------
'''

import mysql.connector
import bcrypt
import hashlib
import uuid

SERVER = 'database-3.ca1ssxyjeifl.us-east-2.rds.amazonaws.com'

MYSQL_SOCKET = mysql.connector.connect(

    host=SERVER,
    user='admin',
    password='nopassword4u'

)

CURSOR = MYSQL_SOCKET.cursor(buffered=True)

CURSOR.execute("USE users")

'''
--------------------------------------------------------------------

def reconnect(): Called everytime a query is executed to make sure
                 that we are connected to SERVER

--------------------------------------------------------------------
'''


def reconnect():

    try:

        MYSQL_SOCKET.connect(

            host=SERVER,
            user='admin',
            password='nopassword4u'

        )

    except Exception:

        pass


'''
--------------------------------------------------------------------

def hash(string: str): Returns the SHA512 hash of the
                       given argument.

--------------------------------------------------------------------
'''


def hash(string: str):

    hash = hashlib.sha512(

        string.encode('utf-8')

    ).hexdigest()

    return hash


'''
--------------------------------------------------------------------

def generate_salt(): Generate a salt of size 32

--------------------------------------------------------------------
'''


def generate_salt():

    return str(bcrypt.gensalt(24))


'''
--------------------------------------------------------------------

def register(user: str, password: str): Register a new user if noone
else has the username specified

--------------------------------------------------------------------
'''


def register(

    user: str,
    password: str

):

    if (

        len(user) == 0
        or len(password) == 0
        or len(user) > 16

    ):

        return False

    reconnect()

    CURSOR.execute(

        """

        SELECT *

        FROM users.user_login

        WHERE username = %(username)s;

        """, {

            'username': user

        }
    )

    result = CURSOR.fetchone()

    if result is None:

        salt = generate_salt()

        passhash = hash(

            password+salt

        )

        reconnect()

        CURSOR.execute(

            """

            INSERT INTO users.user_login (

                username,
                salt,
                password,
                logged_in,
                token

            )

            VALUES (

                %(username)s,
                %(salt)s,
                %(password)s,
                False,
                Null

            )

            """, {

                'username': user,
                'salt': salt,
                'password': passhash

            }

        )

        MYSQL_SOCKET.commit()

        return True

    else:

        return False


'''
--------------------------------------------------------------------

def login(user: str, password: str): Login a user. If successful,
                                     generate a new token until they
                                     disconnect/logout.

--------------------------------------------------------------------
'''


def login(

    user: str,
    password: str

):

    reconnect()

    CURSOR.execute(

        """
        SELECT *

        FROM users.user_login

        WHERE

            logged_in = False and
            username = %(username)s

        """, {

            'username': user

        }

    )

    result = CURSOR.fetchone()

    if result is not None:

        token = uuid.uuid4().hex

        salt = result[1]
        password_sum = result[2]

        if(

            hash(password+salt) ==
            password_sum

        ):

            reconnect()

            CURSOR.execute(

                """

                UPDATE users.user_login

                SET

                    logged_in = True,
                    token = %(token)s

                WHERE

                    username = %(username)s;

                """, {

                    'token': token,
                    'username': user

                }

            )

            MYSQL_SOCKET.commit()

            return [True, token]

        else:

            return [False]

    else:

        return [False]


def logout(token: str):

    reconnect()

    CURSOR.execute(

        """

        UPDATE users.user_login

        SET

            logged_in = False,
            token = null

        WHERE

            token = %(token)s;

        """, {

            'token': token

        }

    )

    MYSQL_SOCKET.commit()

# EOF
