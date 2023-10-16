from flask import Flask, render_template, request, redirect, session, flash
from werkzeug.security import check_password_hash, generate_password_hash
import secrets
import sqlite3

from flask_pymongo import PyMongo
import urllib

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

#Connecting to mongoDB
escaped_username = urllib.parse.quote_plus("malcolm5964")
escaped_password = urllib.parse.quote_plus("@T0012069z")
app.config["MONGO_URI"] = f"mongodb+srv://{escaped_username}:{escaped_password}@databaseproject.rlzcysi.mongodb.net/Product?retryWrites=true&w=majority"
mongodb_client = PyMongo(app)
db = mongodb_client.db

#Display item
@app.route('/', methods=['POST', 'GET'])
def index():
    products = []
    for product in db.product.find().sort("productName"):
        product["_id"] = str(product["_id"])
        products.append(product)
        # print(product)
    return render_template('index.html', products=products)

#Adding new item
@app.route('/add_item', methods=['GET', 'POST'])
def add_item():
    if request.method == 'POST':
        productName = request.form['productName']
        productStock = request.form['productStock']
        productCategory = request.form['productCategory']
        productPrice = request.form['productPrice']
        productDescription = request.form['productDescription']

        db.product.insert_one({
            "productName": productName,
            "productStock": productStock,
            "productCategory": productCategory,
            "productPrice": productPrice,
            "productDescription": productDescription
        })

        flash("Added new item successfully", "success")
        return redirect("/add_item")
    
    return render_template('add_item.html')

    
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
                return redirect('/')
            else:
                session['login_status'] = 2
                return redirect('/login')
        except Exception as e:
            print(str(e)) # Troubleshooting purposes.
            session['login_status'] = 2
            return redirect('/login')
    
    
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

            return render_template('login.html')
        except Exception as e:
            print(str(e))
            # signup_status 2 means email already exists.
            return render_template('signup.html', signup_status=2)

    return render_template('signup.html')

@app.route('/logout', methods=['GET', 'POST'])
def logout():
    session.clear()
    return redirect('/')

@app.route('/cart', methods=['GET', 'POST'])
def cart():
    try:
        if request.method == 'POST' and session['login_status'] == 1:
            product_id = request.form['product_id']
            product_name = request.form['product_name']
            product_price = request.form['product_price']
            user_id = session['user_id']

            try:
                conn = get_db_connection()
                product = conn.execute('SELECT * FROM shopping_cart WHERE user_id = ? AND product_id = ?', (user_id, product_id)).fetchone()
                if product is not None:
                    conn.execute('UPDATE shopping_cart SET product_quantity = product_quantity + 1 WHERE user_id = ? AND product_id = ?', (user_id, product_id))
                    conn.commit()
                    conn.close()
                else:
                    conn.execute('INSERT INTO shopping_cart (user_id, product_id, product_name, product_price, product_quantity) VALUES (?, ?, ?, ?, ?)', 
                                (user_id, product_id, product_name, product_price, 1))
                    conn.commit()
                    conn.close()

                return redirect('/')
            
            except Exception as e:
                print(str(e))
                return render_template('index.html')
    
        elif request.method == 'GET':
            conn = get_db_connection()
            shopping_cart = conn.execute('SELECT * FROM shopping_cart WHERE user_id = ?', (session['user_id'],)).fetchall()
            conn.close()

            return render_template('cart.html', shopping_cart=shopping_cart)
    except:
        return redirect('/login')
    
@app.route('/cart_update', methods=['GET', 'POST'])
def cart_update():
    try:
        if request.method == 'POST' and session['login_status'] == 1:
            conn = get_db_connection()
            conn.execute('UPDATE shopping_cart SET product_quantity = ? WHERE user_id = ? AND product_id = ?', (request.form['quantity'], session['user_id'], request.form['product_id']))
            conn.commit()
            conn.close()
            print(request.form['quantity'])
            print(request.form['product_id'])
            return redirect('/cart')
    except:
        print("Error")
        return redirect('/cart')

    

@app.route('/wishlist', methods=['GET', 'POST'])
def wishlist():
    try:
        if request.method == 'POST' and session['login_status'] == 1:
            product_id = request.form['product_id']
            product_name = request.form['product_name']
            product_price = request.form['product_price']
            user_id = session['user_id']

            try:
                conn = get_db_connection()
                conn.execute('INSERT INTO wishlist (user_id, product_id, product_name, product_price) VALUES (?, ?, ?, ?)',
                             (user_id, product_id, product_name, product_price))
                conn.commit()
                conn.close()

                return redirect('/')

            except Exception as e:
                print(str(e))
                return render_template('index.html')

        elif request.method == 'GET':
            conn = get_db_connection()
            shopping_cart = conn.execute(
                'SELECT * FROM wishlist WHERE user_id = ?', (session['user_id'],)).fetchall()
            conn.close()

            return render_template('wishlist.html', shopping_cart=shopping_cart)
    except:
        return redirect('/login')


@app.route('/remove_from_wishlist', methods=['POST'])
def remove_from_wishlist():
    if session['login_status'] == 1:
        product_id = request.form['product_id']
        user_id = session['user_id']

        try:
            conn = get_db_connection()
            conn.execute('DELETE FROM wishlist WHERE user_id = ? AND product_id = ?',
                         (user_id, product_id))
            conn.commit()
            conn.close()

        except Exception as e:
            print(str(e))

    return redirect('/wishlist')
    
if __name__ == '__main__':
    app.run(debug=True)