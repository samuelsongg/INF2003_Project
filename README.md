# INF2003_Project

## Set Up Virtual Environment
1. `pip install virtualenv`
2. `virtualenv env`
3. `env\Scripts\activate`

## Libraries to Install
1. `pip install flask flask-sqlalchemy flask-login`

## Running Application
1. Make sure to activate the virtual environment:
    - `env\Scripts\activate`
2. Enter `python app.py` in powershell.
3. Navigate to `localhost:5000` in browser.

## Troubleshooting
- Make sure to activate the virtual environment:
    - `env\Scripts\activate`
- If you encounter an error: table not found, run the following in python shell:
    - `flask shell`
    - `from app import db`
    - `db.create_all()`
