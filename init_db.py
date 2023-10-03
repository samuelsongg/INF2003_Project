# Initialise the database.
# Do NOT run it unless you want to reset the database.

import sqlite3

connection = sqlite3.connect('sql_database.db')

with open('schema.sql') as f:
    connection.executescript(f.read())

# connection.commit()
connection.close()

# Troubleshooting purposes.
print('Database initialized.')