DROP TABLE IF EXISTS users;
DROP TABLE IF EXISTS shopping_cart;
DROP TABLE IF EXISTS wishlist;
DROP TABLE IF EXISTS payment;
DROP TABLE IF EXISTS card_details;
DROP TABLE IF EXISTS orders;


CREATE TABLE users (
    user_id INTEGER PRIMARY KEY AUTOINCREMENT,
    first_name varchar(50) NOT NULL,
    last_name varchar(50),
    email varchar(50) NOT NULL UNIQUE,
    password varchar(50) NOT NULL,
    address varchar(100),
    phone_number varchar(20),
    account_type varchar(10) NOT NULL DEFAULT "user",
    time_created DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE shopping_cart (
    cart_id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    product_id INTEGER NOT NULL,
    product_name varchar(100) NOT NULL,
    product_quantity INTEGER NOT NULL,
    product_price INTEGER NOT NULL,
    time_created DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);

CREATE TABLE wishlist (
    wishlist_id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    product_id INTEGER NOT NULL,
    product_name varchar(100) NOT NULL,
    product_price INTEGER NOT NULL,
    time_created DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);

CREATE TABLE payment (
    payment_id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    payment_method INTEGER NOT NULL,
    payment_amnt DECIMAL(10, 2) NOT NULL,
    time_created DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);

CREATE TABLE card_details (
    card_id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    card_number VARCHAR(40) NOT NULL,
    exp_date DATETIME NOT NULL,
    security_code VARCHAR(3) NOT NULL,
    full_name VARCHAR(50) NOT NULL,
    shipping_address varchar(100) NOT NULL,
    time_created DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);

CREATE TABLE orders (
    order_id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    order_date DATETIME DEFAULT CURRENT_TIMESTAMP,
    order_price DECIMAL(10, 2) NOT NULL,
    order_payment_method VARCHAR(255) NOT NULL,
    card_id INTEGER,  
    FOREIGN KEY (user_id) REFERENCES users(user_id),
    FOREIGN KEY (card_id) REFERENCES card_details(card_id)  
);

CREATE TABLE orders (
    order_id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    order_date DATETIME DEFAULT CURRENT_TIMESTAMP,
    order_price DECIMAL(10, 2) NOT NULL,
    order_payment_method VARCHAR(255) NOT NULL,
    card_id INTEGER,  
    FOREIGN KEY (user_id) REFERENCES users(user_id),
    FOREIGN KEY (card_id) REFERENCES card_details(card_id)  
);

CREATE TABLE order_items (
    order_item_id INTEGER PRIMARY KEY AUTOINCREMENT,
    order_id INT,
    product_id INT,
    product_name VARCHAR(255),
    product_price DECIMAL(10, 2),
    quantity INT,
    FOREIGN KEY (order_id) REFERENCES orders(order_id)
);


CREATE TABLE review (
    review_id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    review_title varchar(100) NOT NULL,
    review_description varchar(200),
    review_rating INTEGER NOT NULL,
    product_id VARCHAR(100) NOT NULL,
    time_created DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);