# Initialise the database.
# Do NOT run it unless you want to reset the database.

import sqlite3
from werkzeug.security import generate_password_hash

conn = sqlite3.connect('sql_database.db')

with open('schema.sql') as f:
    conn.executescript(f.read())

# Create an admin account.
password = 'admin'
password = generate_password_hash(password, method='pbkdf2:sha256')
conn.execute('INSERT INTO users (first_name, email, password, account_type) VALUES (?, ?, ?, ?)',
            ('administrator', 'admin@gmail.com', password, 'admin'))
            

conn.commit()
conn.close()

# Troubleshooting purposes.
print('Database initialized.')