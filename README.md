# INF2003_Project

## Libraries to Install
1. pip install virtualenv
2. pip install flask flask-sqlalchemy flask-login

## Troubleshooting
- Make sure you're in the virtual environment:
    - \enc\Scripts\activate.bat
- If you encounter an error: table not found, run the following in python shell:
    - flask shell
    - from app import db
    - db.create_all()
