# A program to generate the database for the user management
# Imports
import sqlite3
from bcrypt import hashpw, gensalt, checkpw

# Connect to the user management database, and create a cursor
conn = sqlite3.connect('UserManagement.db')
c = conn.cursor()

#####################
####### USERS #######
#####################
# Create the table, with IF NOT EXISTS setting to prevent errors
c.execute("""CREATE TABLE IF NOT EXISTS users(
           ID integer PRIMARY KEY AUTOINCREMENT,
           username varchar (31) NOT NULL,
           password varchar (31) NOT NULL
           ) """
           )
# ID as the primary key, which autoincrements when a new record is added. User sets this as NULL during INSERT
# Username is a 31 bit Variable Character, and it cannot be empty
# Password is a 31 bit Variable Character, and it cannot be empty

def insert_user(username, password):        
    # Function to insert a user. NULL for ID, and then arguments get passed to INSERT statement
    with conn:
        c.execute("INSERT INTO users VALUES (NULL, :username, :password)",
                  {'username':username, 'password':password})
        
# To insert a user, replace the values in the curly brackets with the new user details
#insert_user("{Username}", (hashpw("{Password}".encode('utf-8'), gensalt())))

#######################
###### VARIABLES ######
#######################
# Create the table, with IF NOT EXISTS setting to prevent errors
c.execute("""CREATE TABLE IF NOT EXISTS variables(
           variable varchar (4)  PRIMARY KEY NOT NULL,
           search varchar (127) NOT NULL
           ) """
           )
# Variable as the primary key, which is the shortcut variable a user can use to implement a longer search
# Search is a 63 bit Variable Character, and it cannot be empty. This is the custom search
        
def insert_variable(variable, search):        
    # Function to insert a variable. NULL for ID, and then arguments get passed to INSERT statement
    with conn:
        c.execute("INSERT INTO variables VALUES (:variable, :search)",
                  {'variable':variable, 'search':search})

#insert_variable("gb1","gastric OR bypass AND obes*")
#insert_variable("cc1","circumcision AND peni* AND stone")
