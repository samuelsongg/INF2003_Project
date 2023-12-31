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
    conn = sqlite3.connect("sql_database.db")
    conn.row_factory = sqlite3.Row
    return conn


# Connecting to mongoDB
escaped_username = urllib.parse.quote_plus("malcolm5964")
escaped_password = urllib.parse.quote_plus("@T0012069z")
app.config[
    "MONGO_URI"
] = f"mongodb+srv://{escaped_username}:{escaped_password}@databaseproject.rlzcysi.mongodb.net/Product?retryWrites=true&w=majority"
mongodb_client = PyMongo(app)
db = mongodb_client.db


@app.route("/", methods=["POST", "GET"])
def index():
    products = []
    # Fetch products from MongoDB
    for product in db.product.find().sort("productName"):
        product["_id"] = str(product["_id"])
        products.append(product)

    # Get average rating for each product
    for product in products:
        product_id = product["_id"]
        conn = get_db_connection()
        avg_rating = (
            conn.execute(
                "SELECT AVG(review_rating) from review WHERE product_id=?",
                (product_id,),
            )
        ).fetchone()[0]
        conn.close()
        product["avg_rating"] = avg_rating

    # Get top 3 products based on quantity sold
    top_products = get_top_products()

    return render_template("index.html", products=products, top_products=top_products)


def get_top_products():
    # SQLite query to get the top 3 products based on quantity sold
    conn = get_db_connection()
    top_products_id = conn.execute(
        """
        SELECT product_id, SUM(quantity) AS total_quantity
        FROM order_items
        GROUP BY product_id, product_name
        ORDER BY total_quantity DESC
        LIMIT 3;
    """
    ).fetchall()
    conn.close()

    # Get the product details from MongoDB
    top_products = []
    for product_id in top_products_id:
        product = db.product.find_one({"_id": ObjectId(product_id[0])})
        product["_id"] = str(product["_id"])
        top_products.append(product)

    return top_products


# Adding new item
@app.route("/add_item", methods=["GET", "POST"])
def add_item():
    if request.method == "GET":
        session["product_tag_number"] = 1
        session.pop("tagName", None)
        session.pop("tagValue", None)
        session.pop("productName", None)
        session.pop("productStock", None)
        session.pop("productCategory", None)
        session.pop("productPrice", None)
        session.pop("productDescription", None)
        session.pop("productImage", None)
        return render_template("add_item.html")

    if request.method == "POST":
        if request.form["submit"] == "AddTag":
            session["product_tag_number"] += 1
            session["tagName"] = request.form.getlist("tagName")
            session["tagValue"] = request.form.getlist("tagValue")
            session["productName"] = request.form["productName"]
            session["productStock"] = request.form["productStock"]
            session["productCategory"] = request.form["productCategory"]
            session["productPrice"] = request.form["productPrice"]
            session["productDescription"] = request.form["productDescription"]
            session["productImage"] = request.form["productImage"]
            return render_template("add_item.html")

        elif request.form["submit"] == "Submit":
            productName = request.form["productName"]
            productStock = request.form["productStock"]
            productCategory = request.form["productCategory"]
            productPrice = request.form["productPrice"]
            productDescription = request.form["productDescription"]
            productImage = request.form["productImage"]

            product_data = {
                "productName": productName,
                "productStock": productStock,
                "productCategory": productCategory,
                "productPrice": productPrice,
                "productDescription": productDescription,
                "productImage": productImage,
            }

            tag_names = request.form.getlist("tagName")
            tag_values = request.form.getlist("tagValue")

            for i in range(session["product_tag_number"]):
                tag_name = tag_names[i]
                tag_value = tag_values[i]
                product_data[tag_name] = tag_value

            db.product.insert_one(product_data)

            flash("Added new item successfully", "success")
            return redirect("/add_item")


@app.route("/edit_item", methods=["GET", "POST"])
def edit_item():
    if request.method == "GET":
        # Insert code here...
        return render_template("edit_item.html")

    # If user presses on "Add Tag" button, add a new tag field
    if request.method == "POST":
        if request.form["submit"] == "AddTag":
            session["product_tag_number"] += 1  # Adds 1 to the tag number
            session["tagName"] = request.form.getlist("tagName")
            session["tagValue"] = request.form.getlist("tagValue")
            session["productName"] = request.form["productName"]
            session["productStock"] = request.form["productStock"]
            session["productCategory"] = request.form["productCategory"]
            session["productPrice"] = request.form["productPrice"]
            session["productDescription"] = request.form["productDescription"]
            session["productImage"] = request.form["productImage"]
            return render_template("edit_item.html")

        # If user presses on "Update" button, update the product in the database
        if request.form["submit"] == "Update":
            session["tagName"] = request.form.getlist("tagName")
            session["tagValue"] = request.form.getlist("tagValue")
            session["productName"] = request.form["productName"]
            session["productStock"] = request.form["productStock"]
            session["productCategory"] = request.form["productCategory"]
            session["productPrice"] = request.form["productPrice"]
            session["productDescription"] = request.form["productDescription"]
            session["productImage"] = request.form["productImage"]

            query = {"_id": ObjectId(session["productID"])}
            update = {
                "productName": session["productName"],
                "productStock": session["productStock"],
                "productCategory": session["productCategory"],
                "productPrice": session["productPrice"],
                "productDescription": session["productDescription"],
                "productImage": session["productImage"],
            }

            temp_tag_counter = 0  # To count how many tags are there
            temp_tag_name = []  # To store the tag name
            temp_tag_value = []  # To store the tag value

            # To check if the tag name is empty or not
            for i in range(session["product_tag_number"]):
                if session["tagName"][i] != "":
                    temp_tag_name.append(session["tagName"][i])
                    temp_tag_value.append(session["tagValue"][i])
                    temp_tag_counter += 1

            # Update the session variables with the new tag name and value
            session["tagName"] = temp_tag_name
            session["tagValue"] = temp_tag_value
            session["product_tag_number"] = temp_tag_counter

            # To update the tag name and value
            for i in range(session["product_tag_number"]):
                tag_name = session["tagName"][i]
                tag_value = session["tagValue"][i]
                update[tag_name] = tag_value

            # Replace the old data with the new data according to the product ID
            db.product.replace_one(query, update)
            return redirect("/")

        # If user presses on "Delete" button, delete the product from the database
        if request.form["submit"] == "Delete":
            query = {"_id": ObjectId(session["productID"])}
            db.product.delete_one(query)
            return redirect("/")


@app.route("/manage_user", methods=["GET", "POST"])
def manage_user():
    try:
        if request.method == "GET":
            conn = get_db_connection()
            users = conn.execute("SELECT * FROM users").fetchall()
            conn.close()

            return render_template("manage_user.html", users=users)

    except Exception as e:
        print(str(e))
        return redirect("/")


@app.route("/delete_user", methods=["GET", "POST"])
def delete_user():
    try:
        if request.method == "POST":
            conn = get_db_connection()
            conn.execute(
                "DELETE FROM users WHERE user_id = ?", (request.form["user_id"],)
            )
            conn.commit()
            conn.close()

            return redirect("/manage_user")

    except Exception as e:
        print(str(e))
        return redirect("/")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        # Check if the user exists in the database
        try:
            conn = get_db_connection()
            user = conn.execute(
                "SELECT * FROM users WHERE email = ?", (email,)
            ).fetchone()
            conn.close()

            if check_password_hash(user["password"], password):
                session["user_id"] = user["user_id"]
                # 1 means logged in, 0 means not logged in, 2 means wrong attempt.
                session["login_status"] = 1
                session["first_name"] = user["first_name"]
                session["last_name"] = user["last_name"]
                session["account_type"] = user["account_type"]
                return redirect("/")
            else:
                session["login_status"] = 2
                return redirect("/login")
        except Exception as e:
            print(str(e))  # Troubleshooting purposes.
            session["login_status"] = 2
            return redirect("/login")

    return render_template("login.html")


@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        first_name = request.form["first_name"]
        last_name = request.form["last_name"]
        email = request.form["email"]
        password = generate_password_hash(
            request.form["password"], method="pbkdf2:sha256"
        )
        address = request.form["address"]
        phone_number = request.form["phone_number"]

        try:
            conn = get_db_connection()
            conn.execute(
                "INSERT INTO users (first_name, last_name, email, password, address, phone_number) VALUES (?, ?, ?, ?, ?, ?)",
                (first_name, last_name, email, password, address, phone_number),
            )
            conn.commit()
            conn.close()

            return render_template("login.html")
        except Exception as e:
            print(str(e))
            # signup_status 2 means email already exists.
            return render_template("signup.html", signup_status=2)

    return render_template("signup.html")


@app.route("/logout", methods=["GET", "POST"])
def logout():
    session.clear()
    return redirect("/")


@app.route("/cart", methods=["GET", "POST"])
def cart():
    try:
        if (
            request.method == "POST"
            and session["login_status"] == 1
            and request.form["submit"] == "Add to Cart"
        ):
            product_id = request.form["product_id"]
            product_name = request.form["product_name"]
            product_price = request.form["product_price"]
            user_id = session["user_id"]

            try:
                conn = get_db_connection()
                product = conn.execute(
                    "SELECT * FROM shopping_cart WHERE user_id = ? AND product_id = ?",
                    (user_id, product_id),
                ).fetchone()
                if product is not None:
                    conn.execute(
                        "UPDATE shopping_cart SET product_quantity = product_quantity + 1 WHERE user_id = ? AND product_id = ?",
                        (user_id, product_id),
                    )
                    conn.commit()
                    conn.close()
                else:
                    conn.execute(
                        "INSERT INTO shopping_cart (user_id, product_id, product_name, product_price, product_quantity) VALUES (?, ?, ?, ?, ?)",
                        (user_id, product_id, product_name, product_price, 1),
                    )
                    conn.commit()
                    conn.close()

                return redirect("/")

            except:
                return render_template("index.html")

        elif (
            request.method == "POST"
            and session["login_status"] == 1
            and request.form["submit"] == "Edit Product"
        ):
            product_id = request.form["product_id"]
            product_list = db.product.find_one({"_id": ObjectId(product_id)})
            session["productID"] = product_id
            session["productName"] = product_list["productName"]
            session["productStock"] = product_list["productStock"]
            session["productCategory"] = product_list["productCategory"]
            session["productPrice"] = product_list["productPrice"]
            session["productDescription"] = product_list["productDescription"]
            session["productImage"] = product_list["productImage"]

            tag_name_list = []
            tag_value_list = []

            for i, (key, value) in enumerate(product_list.items()):
                if i >= 7:
                    tag_name_list.append(key)
                    tag_value_list.append(value)

            session["tagName"] = tag_name_list
            session["tagValue"] = tag_value_list
            session["product_tag_number"] = len(tag_name_list)

            return render_template("edit_item.html")

        elif request.method == "GET":
            conn = get_db_connection()
            shopping_cart = conn.execute(
                "SELECT * FROM shopping_cart WHERE user_id = ?", (session["user_id"],)
            ).fetchall()
            conn.close()

            return render_template("cart.html", shopping_cart=shopping_cart)
    except Exception as e:
        print(str(e))
        return redirect("/login")


@app.route("/cart_update", methods=["GET", "POST"])
def cart_update():
    try:
        if request.method == "POST" and session["login_status"] == 1:
            conn = get_db_connection()
            conn.execute(
                "UPDATE shopping_cart SET product_quantity = ? WHERE user_id = ? AND product_id = ?",
                (
                    request.form["quantity"],
                    session["user_id"],
                    request.form["product_id"],
                ),
            )
            conn.commit()
            conn.close()
            return redirect("/cart")
    except:
        return redirect("/cart")


@app.route("/cart_delete", methods=["GET", "POST"])
def cart_delete():
    try:
        if request.method == "POST":
            conn = get_db_connection()
            conn.execute(
                "DELETE FROM shopping_cart WHERE user_id = ? AND product_id = ?",
                (session["user_id"], request.form["product_id"]),
            )
            conn.commit()
            conn.close()
            return redirect("/cart")
    except:
        return redirect("/cart")


@app.route("/purchase_history", methods=["GET", "POST"])
def purchase_history():
    try:
        if request.method == "GET":
            conn = get_db_connection()
            orders = conn.execute(
                "SELECT * FROM order_items oi JOIN orders o ON oi.order_id = o.order_id"
            ).fetchall()
            conn.close()

            return render_template("purchase_history.html", orders=orders)

    except Exception as e:
        print(str(e))
        return redirect("/")


@app.route("/payment", methods=["GET", "POST"])
def payment():
    try:
        if (request.method == "GET") and session["login_status"] == 1:
            conn = get_db_connection()
            shopping_cart = conn.execute(
                "SELECT * FROM shopping_cart WHERE user_id = ?", (session["user_id"],)
            ).fetchall()
            card = conn.execute(
                "SELECT * FROM card_details WHERE user_id = ?", (session["user_id"],)
            ).fetchall()
            total_price = sum(
                item["product_price"] * item["product_quantity"]
                for item in shopping_cart
            )
            session["total_price"] = total_price
            conn.close()

            card_exists = bool(card)

            return render_template(
                "payment.html",
                shopping_cart=shopping_cart,
                card_exists=card_exists,
                total_price=total_price,
                card=card,
            )
    except:
        return redirect("/login.html")


@app.route("/order_success", methods=["GET", "POST"])
def order_success():
    user_id = session["user_id"]
    card_id = request.form["card_id"]
    order_price = session.get("total_price")
    order_payment_method = "card"
    try:
        if request.method == "POST":
            conn = get_db_connection()
            conn.execute(
                "INSERT INTO orders (user_id, card_id, order_price, order_payment_method) VALUES (?, ?, ?, ?)",
                (user_id, card_id, order_price, order_payment_method),
            )
            conn.commit()

            cursor = conn.cursor()
            cursor.execute("SELECT last_insert_rowid()")
            order_id = cursor.fetchone()[0]

            shopping_cart = conn.execute(
                "SELECT * FROM shopping_cart WHERE user_id = ?", (session["user_id"],)
            ).fetchall()

            for item in shopping_cart:
                product_id = item["product_id"]
                product_name = item["product_name"]
                product_price = item["product_price"]
                quantity = item["product_quantity"]

                conn.execute(
                    "INSERT INTO order_items (order_id, product_id, product_name, product_price, quantity) VALUES (?, ?, ?, ?, ?)",
                    (order_id, product_id, product_name, product_price, quantity),
                )
                conn.commit()

            order = conn.execute(
                "SELECT * FROM orders WHERE order_id = ?", (order_id,)
            ).fetchall()
            order_items = conn.execute(
                "SELECT * FROM order_items WHERE order_id = ?", (order_id,)
            ).fetchall()

            # conn.execute('DELETE FROM shopping_cart WHERE user_id = ?', (session['user_id'],))
            conn.commit()
            conn.close()

            return render_template(
                "order_success.html", order=order, order_items=order_items
            )
    except Exception as e:
        print(str(e))
        return redirect("/payment")
    return render_template("order_success.html")


@app.route("/add_card", methods=["GET", "POST"])
def add_card():
    if request.method == "POST":
        card_number = request.form["card_number"]
        exp_date = request.form["exp_date"]
        security_code = request.form["security_code"]
        full_name = request.form["full_name"]
        shipping_address = request.form["shipping_address"]
        user_id = session["user_id"]

        try:
            conn = get_db_connection()
            conn.execute(
                "INSERT INTO card_details (user_id, card_number, exp_date, security_code, full_name, shipping_address) VALUES (?, ?, ?, ?, ?, ?)",
                (
                    user_id,
                    card_number,
                    exp_date,
                    security_code,
                    full_name,
                    shipping_address,
                ),
            )
            conn.commit()
            conn.close()

            return redirect("/payment")
        except Exception as e:
            return redirect("/login.html")
    return render_template("/add_card.html")


@app.route("/wishlist", methods=["GET", "POST"])
def wishlist():
    try:
        if request.method == "POST" and session["login_status"] == 1:
            product_id = request.form["product_id"]
            product_name = request.form["product_name"]
            product_price = request.form["product_price"]
            user_id = session["user_id"]

            try:
                conn = get_db_connection()
                conn.execute(
                    "INSERT INTO wishlist (user_id, product_id, product_name, product_price) VALUES (?, ?, ?, ?)",
                    (user_id, product_id, product_name, product_price),
                )
                conn.commit()
                conn.close()

                return redirect("/")

            except Exception as e:
                print(str(e))
                return render_template("index.html")

        elif request.method == "GET":
            conn = get_db_connection()
            shopping_cart = conn.execute(
                "SELECT * FROM wishlist WHERE user_id = ?", (session["user_id"],)
            ).fetchall()
            conn.close()

            return render_template("wishlist.html", shopping_cart=shopping_cart)
    except:
        return redirect("/login")


# Review part
reviewQuery = """
    SELECT R.product_id, R.review_id, R.user_id, R.review_title, R.review_description, R.review_rating, R.product_id, R.time_created, U.first_name
    FROM
    review R, users U
    WHERE
    R.product_id = ? AND R.user_id = U.user_id
"""


@app.route("/detailedItem/<product_id>", methods=["GET", "POST"])
def detailedItem(product_id):
    try:
        if request.method == "POST" and "reviewRating" in request.form:
            reviewTitle = request.form["reviewTitle"]
            reviewDescription = request.form["reviewDescription"]
            reviewRating = request.form["reviewRating"]
            user_id = session["user_id"]

            try:
                # Insert then Retrieve to reload page
                conn = get_db_connection()
                conn.execute(
                    "INSERT INTO review (user_id, review_title, review_description, review_rating, product_id) VALUES (?, ?, ?, ?, ?)",
                    (user_id, reviewTitle, reviewDescription, reviewRating, product_id),
                )
                conn.commit()
                reviews = conn.execute(reviewQuery, (product_id,)).fetchall()
                conn.close()
                # Get product info from mongodb
                product = db.product.find_one({"_id": ObjectId(product_id)})
                return render_template(
                    "detailedItem.html",
                    product_id=product_id,
                    product=product,
                    reviews=reviews,
                )

            except Exception as e:
                print(str(e))
                return render_template("index.html")

        elif request.method == "GET":
            conn = get_db_connection()
            reviews = conn.execute(reviewQuery, (product_id,)).fetchall()
            conn.close()
            product = db.product.find_one({"_id": ObjectId(product_id)})
            return render_template(
                "detailedItem.html",
                product_id=product_id,
                product=product,
                reviews=reviews,
            )

    except Exception as e:
        print(str(e))
        return redirect("/login")


@app.route("/remove_from_wishlist", methods=["POST"])
def remove_from_wishlist():
    if session["login_status"] == 1:
        product_id = request.form["product_id"]
        user_id = session["user_id"]

        try:
            conn = get_db_connection()
            conn.execute(
                "DELETE FROM wishlist WHERE user_id = ? AND product_id = ?",
                (user_id, product_id),
            )
            conn.commit()
            conn.close()

        except Exception as e:
            print(str(e))

    return redirect("/wishlist")


@app.route("/profile", methods=["GET"])
def profile():
    # Retrieve user data
    try:
        user_id = session["user_id"]
        conn = get_db_connection()
        user = conn.execute(
            "SELECT * FROM users WHERE user_id = ?", (user_id,)
        ).fetchone()
        conn.close()
        return render_template("profile.html", user=user)

    except Exception as e:
        print(str(e))
        return redirect("/login")


@app.route("/editprofile", methods=["POST"])
def editprofile():
    try:
        user_id = session["user_id"]
        first_name = request.form["first_name"]
        last_name = request.form["last_name"]
        address = request.form["address"]
        phone_number = request.form["phone_number"]

        conn = get_db_connection()
        conn.execute(
            "UPDATE users SET first_name = ?, last_name = ?, address = ?, phone_number = ? WHERE user_id = ?",
            (first_name, last_name, address, phone_number, user_id),
        )
        conn.commit()
        # To retrieve updated user value
        user = conn.execute(
            "SELECT * FROM users WHERE user_id = ?", (user_id,)
        ).fetchone()
        conn.close()
        return render_template("profile.html", user=user, edit_status=1)

    except Exception as e:
        print(str(e))
        return render_template("profile.html", user=user, edit_status=0)


@app.route("/user_purchase_history", methods=["GET"])
def user_purchase_history():
    try:
        user_id = session["user_id"]
        conn = get_db_connection()
        orders = conn.execute(
            "SELECT * FROM order_items oi JOIN orders o ON oi.order_id = o.order_id WHERE o.user_id = ?",
            (user_id,),
        ).fetchall()
        conn.close()
        return render_template("user_purchase_history.html", orders=orders)

    except Exception as e:
        print(str(e))
        return redirect("/")


if __name__ == "__main__":
    app.run(debug=True)
