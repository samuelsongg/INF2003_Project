# INF2003_Project

## Set Up Virtual Environment
1. `pip install virtualenv`
2. `virtualenv env`
3. `env\Scripts\activate`

## Libraries to Install
1. `pip install flask`
2. `pip install flask_pymongo`

## Running Application
1. Make sure to activate the virtual environment:
    - `env\Scripts\activate`
2. Enter `python app.py` in powershell.
3. Navigate to `localhost:5000` in browser.
    - Admin account:
        - Username: `admin@gmail.com`
        - Password: `admin`

## Troubleshooting
- Make sure to activate the virtual environment:
    - `env\Scripts\activate`
- To reset all SQL databases run `python init_db.py`.
