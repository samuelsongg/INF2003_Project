DROP TABLE IF EXISTS users;
DROP TABLE IF EXISTS shopping_cart;

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