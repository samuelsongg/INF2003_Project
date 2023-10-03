from flask import Flask, render_template, url_for, request, redirect, session
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from werkzeug.security import check_password_hash, generate_password_hash
import secrets

app = Flask(__name__)
secret_key = secrets.token_hex(24)
app.secret_key = secret_key
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data.db'
db = SQLAlchemy(app)
    
class User(db.Model):
    user_id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(200), nullable=False)
    last_name = db.Column(db.String(200), nullable=True)
    email = db.Column(db.String(200), nullable=False)
    password = db.Column(db.String(200), nullable=False)
    address = db.Column(db.String(200), nullable=False)
    phone_number = db.Column(db.String(200), nullable=False)
    account_type = db.Column(db.String(200), default='user') # Either user or admin
    time_created = db.Column(db.DateTime, default=datetime.utcnow)

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
            user = User.query.filter_by(email=email).one()

            if check_password_hash(user.password, password):
                session['user_id'] = user.user_id
                # 1 means logged in, 0 means not logged in, 2 means wrong attempt.
                session['login_status'] = 1
                session['first_name'] = user.first_name
                session['last_name'] = user.last_name
                session['account_type'] = user.account_type
                return render_template('index.html', login_status=1, first_name=user.first_name)
        except Exception as e:
            print(str(e))
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

        new_user = User(
            first_name=first_name,
            last_name=last_name,
            email=email,
            password=password,
            address=address,
            phone_number=phone_number
        )
    
        try:
            db.session.add(new_user)
            db.session.commit()
            return redirect('/login')
        except Exception as e:
            print(str(e))
            return 'There was an unexpected issue. Please try again.'

    return render_template('signup.html')
    
if __name__ == '__main__':

    app.run(debug=True)