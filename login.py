# Login/Register functionality

import mysql.connector
import bcrypt
import hashlib

# Init MySQL connection.

SERVER = 'localhost'
PORT = '3306'
ADDR = (SERVER, PORT)

mysql_socket = mysql.connector.connect(host=SERVER, user='root', password='OBFUSCATED')
cursor = mysql_socket.cursor(buffered=True)

cursor.execute("USE userdata")

def hash(string: str):

    h = hashlib.sha512(string.encode('utf-8')).hexdigest()
    return h

def generate_salt():

    return str(bcrypt.gensalt(24))

def register(user, password):

    if len(user) == 0 or len(password) == 0:
        return False

    cursor.execute("""
    
        SELECT
            *
        FROM
            user_login
        WHERE
            username = %(username)s 
    
    """, {
        'username': user
    })

    result = cursor.fetchone()

    

    if result is None:

        salt = generate_salt()

        passhash = hash(password+salt)
        

        if len(password) > 16 or len(user) > 16:

            return False

        cursor.execute("""
        
            INSERT INTO user_login (username, salt, password)
            
            VALUES (%(username)s, %(salt)s, %(password)s)

        """, {

            'username': user,
            'salt': salt,
            'password': passhash

        })

        mysql_socket.commit()

        return True
        
    
    else:
        
        return False


def login(user, password):

    cursor.execute("""
    
        SELECT
            *
        FROM
            user_login
        WHERE
            username = %(username)s 
    
    """, {
        'username': user
    })

    result = cursor.fetchone()

    if result != None:

        salt = result[1]
        password_sum = result[2]



        if hash(password+salt) == password_sum:

            return True

        else:

            return False
    
    else:

        return False


