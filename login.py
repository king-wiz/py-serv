# Login/Register functionality

import mysql.connector
import bcrypt
import hashlib
import uuid

# Init MySQL connection.

SERVER = 'database-3.ca1ssxyjeifl.us-east-2.rds.amazonaws.com'
PORT = '3306'
ADDR = (SERVER, PORT)

mysql_socket = mysql.connector.connect(host=SERVER, user='admin', password='rdstest1')
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
        
            INSERT INTO user_login (username, salt, password, logged_in, token)
            
            VALUES (%(username)s, %(salt)s, %(password)s, False, Null)

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
            username = %(username)s and
            logged_in = False
    
    """, {
        'username': user
    })

    result = cursor.fetchone()

    if result != None:

        token = uuid.uuid4().hex

        salt = result[1]
        password_sum = result[2]



        if hash(password+salt) == password_sum:

            cursor.execute("""
            
            UPDATE 
	            user_login
            SET
	            logged_in = True,
	            token = %(token)s
            WHERE
                username = %(username)s
            """, {

                'token': token,
                'username': user

            })

            mysql_socket.commit()

            return [True, token]

        else:

            return [False]
    
    else:

        return [False]

def logout(token):

    cursor.execute("""

        UPDATE 
            user_login
        SET
            logged_in = False,
            token = null
        WHERE
            token = %(token)s

    
    """, {

        'token': token

    })


    mysql_socket.commit()
