from flask import Flask, render_template, request, redirect, session
from werkzeug.security import check_password_hash, generate_password_hash
import secrets
import sqlite3

app = Flask(__name__)
# Secret key needs to be set to enable sessions.
secret_key = secrets.token_hex(24)
app.secret_key = secret_key

def get_db_connection():
    conn = sqlite3.connect('sql_database.db')
    conn.row_factory = sqlite3.Row
    return conn

# Troubleshooting purposes.
# conn = get_db_connection()
# test = conn.execute('SELECT * FROM users').fetchall()
# print(test)
# conn.close()

@app.route('/', methods=['POST', 'GET'])
def index():
    return render_template('index.html')
    
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        # Check if the user exists in the database
        try:
            conn = get_db_connection()
            user = conn.execute('SELECT * FROM users WHERE email = ?', (email,)).fetchone()
            conn.close()

            if check_password_hash(user['password'], password):
                session['user_id'] = user['user_id']
                # 1 means logged in, 0 means not logged in, 2 means wrong attempt.
                session['login_status'] = 1
                session['first_name'] = user['first_name']
                session['last_name'] = user['last_name']
                session['account_type'] = user['account_type']
                return render_template('index.html', login_status=1, first_name=user['first_name'])
            else:
                return render_template('login.html', login_status=2)
        except Exception as e:
            print(str(e)) # Troubleshooting purposes.
            return render_template('login.html', login_status=2)
    
    
    return render_template('login.html')
    
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        email = request.form['email']
        password = generate_password_hash(request.form['password'], method='pbkdf2:sha256')
        address = request.form['address']
        phone_number = request.form['phone_number']

        try:
            conn = get_db_connection()
            conn.execute('INSERT INTO users (first_name, last_name, email, password, address, phone_number) VALUES (?, ?, ?, ?, ?, ?)', 
                        (first_name, last_name, email, password, address, phone_number))
            conn.commit()
            conn.close()

            return redirect('/login')
        except Exception as e:
            print(str(e))
            # return 'There was an unexpected issue. Please try again.'
            # signup_status 2 means email already exists.
            return render_template('signup.html', signup_status=2)

    return render_template('signup.html')

@app.route('/logout', methods=['GET', 'POST'])
def logout():
    if request.method == 'POST':
        session.clear()
        return render_template('index.html', login_status=0)
    
if __name__ == '__main__':

    app.run(debug=True)