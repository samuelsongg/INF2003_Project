from flask import Blueprint
from . import app

main = Blueprint('main', __name__)

@main.route('/')
def index():
    return 'Index'

@main.route('/profile')
def profile():
    return 'Profile'

@main.route('/add_item')
def add_item():
    return 'Add_item'