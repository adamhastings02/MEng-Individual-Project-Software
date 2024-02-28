# A program to generate the database for the user management
import sqlite3
from bcrypt import hashpw, gensalt, checkpw
conn = sqlite3.connect('UserManagement.db')
c = conn.cursor()

c.execute("""CREATE TABLE IF NOT EXISTS users(
           ID integer PRIMARY KEY AUTOINCREMENT,
           username varchar (31) NOT NULL,
           password varchar (31) NOT NULL
           ) """
           )

def insert_user(username, password):
    with conn:
        c.execute("INSERT INTO users VALUES (NULL, :username, :password)",
                  {'username':username, 'password':password})


# To insert a user, replace the values in the curly brackets with the new user details
#insert_user("{Username}", (hashpw("{Password}".encode('utf-8'), gensalt())))
