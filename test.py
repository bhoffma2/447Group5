# This is a simple script for testing the connection to our database.

import pymysql

hostname = 'localhost'
user = 'root'
password = 'teamFive'

# Initializing connection
db = pymysql.connections.Connection(
    host=hostname,
    user=user,
    password=password
)

# Creating cursor object
cursor = db.cursor()



# Executing SQL query
# cursor.execute("CREATE DATABASE IF NOT EXISTS users_db")
cursor.execute("SHOW DATABASES")

# Displaying databases
for databases in cursor:
    print(databases)

# Closing the cursor and connection to the database
cursor.close()
db.close()