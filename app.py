from flask import Flask, render_template, request, redirect, session, flash, url_for
from werkzeug.security import check_password_hash, generate_password_hash
import secrets
import sqlite3

from flask_pymongo import PyMongo
import urllib
from bson.objectid import ObjectId

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


@app.route('/', methods=['POST', 'GET'])
def index():
    products = []
    #Fetch products from MongoDB
    for product in db.product.find().sort("productName"):
        product["_id"] = str(product["_id"])
        products.append(product)

    #Get average rating for each product
    for product in products:
        product_id = product["_id"]
        conn = get_db_connection()
        avg_rating = (conn.execute('SELECT AVG(review_rating) from review WHERE product_id=?', (product_id,))).fetchone()[0]
        conn.close()
        product["avg_rating"] = avg_rating

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

@app.route('/manage_user', methods=['GET', 'POST'])
def manage_user():
    try:
        if request.method == 'GET':
            conn = get_db_connection()
            users = conn.execute('SELECT * FROM users').fetchall()
            conn.close()

            return render_template('manage_user.html', users=users)
        
    except Exception as e:
        print(str(e))
        return redirect('/')
    
@app.route('/delete_user', methods=['GET', 'POST'])
def delete_user():
    try:
        if request.method == 'POST':
            conn = get_db_connection()
            conn.execute('DELETE FROM users WHERE user_id = ?', (request.form['user_id'],))
            conn.commit()
            conn.close()

            return redirect('/manage_user')
        
    except Exception as e:
        print(str(e))
        return redirect('/')
    
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        # Check if the user exists in the database
        try:
            conn = get_db_connection()
            user = conn.execute('SELECT * FROM users WHERE email = ?', (email,)).fetchone()[0]
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
            return redirect('/cart')
    except:
        return redirect('/cart')
    
@app.route('/cart_delete', methods=['GET', 'POST'])
def cart_delete():
    try:
        if request.method == 'POST':
            conn = get_db_connection()
            conn.execute('DELETE FROM shopping_cart WHERE user_id = ? AND product_id = ?', (session['user_id'], request.form['product_id']))
            conn.commit()
            conn.close()
            return redirect('/cart')
    except:
        return redirect('/cart')
    

@app.route('/purchase_history', methods=['GET', 'POST'])
def purchase_history():
    try:
        if request.method == 'GET':
            conn = get_db_connection()
            orders = conn.execute('SELECT * FROM orders').fetchall()
            conn.close()

            return render_template('purchase_history.html', orders=orders)

    except Exception as e:
        print(str(e))
        return redirect('/')

@app.route('/payment', methods=['GET', 'POST'])
def payment():
    try:
        if (request.method == 'GET') and session['login_status'] == 1:
            conn = get_db_connection()
            shopping_cart = conn.execute(
                'SELECT * FROM shopping_cart WHERE user_id = ?', (session['user_id'],)).fetchall()
            card = conn.execute(
                'SELECT * FROM card_details WHERE user_id = ?', (session['user_id'],)).fetchall()
            total_price = sum(
                item['product_price'] * item['product_quantity'] for item in shopping_cart)
            session['total_price'] = total_price
            conn.close()

            card_exists = bool(card)

            return render_template('payment.html', shopping_cart=shopping_cart, card_exists=card_exists, total_price=total_price, card=card)
    except:
        return redirect('/login.html')
    

@app.route('/order_success', methods=['GET', 'POST'])
def order_success():
    user_id = session['user_id']
    card_id = request.form['card_id']
    order_price = session.get('total_price')
    order_payment_method = "card"
    try:
        if (request.method == 'POST'):
            conn = get_db_connection()
            conn.execute('INSERT INTO orders (user_id, card_id, order_price, order_payment_method) VALUES (?, ?, ?, ?)',
                            (user_id, card_id, order_price, order_payment_method))
            conn.commit()

            cursor = conn.cursor()
            cursor.execute("SELECT last_insert_rowid()")
            order_id = cursor.fetchone()[0]

            shopping_cart = conn.execute(
                'SELECT * FROM shopping_cart WHERE user_id = ?', (session['user_id'],)).fetchall()

            for item in shopping_cart:
                product_id = item['product_id']
                product_name = item['product_name']
                product_price = item['product_price']
                quantity = item['product_quantity']

                conn.execute('INSERT INTO order_items (order_id, product_id, product_name, product_price, quantity) VALUES (?, ?, ?, ?, ?)',
                            (order_id, product_id, product_name, product_price, quantity))
                conn.commit()
            
            order = conn.execute(
                'SELECT * FROM orders WHERE order_id = ?', (order_id,)).fetchall()
            order_items = conn.execute(
                'SELECT * FROM order_items WHERE order_id = ?', (order_id,)).fetchall()
            
            # conn.execute('DELETE FROM shopping_cart WHERE user_id = ?', (session['user_id'],))
            conn.commit()
            conn.close()

            return render_template('order_success.html', order=order, order_items=order_items)
    except Exception as e:
            print(str(e))
            return redirect('/payment')   
    return render_template('order_success.html')
    

@app.route('/add_card', methods=['GET', 'POST'])
def add_card():
    if request.method == 'POST':
        card_number = request.form['card_number']
        exp_date = request.form['exp_date']
        security_code = request.form['security_code']
        full_name = request.form['full_name']
        shipping_address = request.form['shipping_address']
        user_id = session['user_id']

        try:
            conn = get_db_connection()
            conn.execute('INSERT INTO card_details (user_id, card_number, exp_date, security_code, full_name, shipping_address) VALUES (?, ?, ?, ?, ?, ?)',
                         (user_id, card_number, exp_date, security_code, full_name, shipping_address))
            conn.commit()
            conn.close()

            return redirect('/payment')
        except Exception as e:
            return redirect('/login.html')    
    return render_template('/add_card.html')
        
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
    

#Review part
reviewQuery = '''
    SELECT R.product_id, R.review_id, R.user_id, R.review_title, R.review_description, R.review_rating, R.product_id, R.time_created, U.first_name
    FROM
    review R, users U
    WHERE
    R.product_id = ? AND R.user_id = U.user_id
'''

@app.route('/detailedItem/<product_id>', methods=['GET', 'POST'])
def detailedItem(product_id):
    try:
        if request.method == 'POST' and 'reviewRating' in request.form:
            reviewTitle = request.form['reviewTitle']
            reviewDescription = request.form['reviewDescription']
            reviewRating = request.form['reviewRating']
            user_id = session['user_id']

            try:
                #Insert then Retrieve to reload page
                conn = get_db_connection()
                conn.execute('INSERT INTO review (user_id, review_title, review_description, review_rating, product_id) VALUES (?, ?, ?, ?, ?)', (user_id, reviewTitle, reviewDescription, reviewRating, product_id))
                conn.commit()
                reviews = conn.execute(reviewQuery, (product_id,)).fetchall()
                conn.close()
                #Get product info from mongodb
                product = db.product.find_one({"_id": ObjectId(product_id)})
                return render_template('detailedItem.html', product_id=product_id, product=product, reviews=reviews)
            
            except Exception as e:
                print(str(e))
                return render_template('index.html')
            
        elif request.method == 'GET':
            conn = get_db_connection()
            reviews = conn.execute(reviewQuery, (product_id,)).fetchall()
            conn.close()
            product = db.product.find_one({"_id": ObjectId(product_id)})
            return render_template('detailedItem.html', product_id=product_id, product=product, reviews=reviews)

    except Exception as e:
        print(str(e))
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