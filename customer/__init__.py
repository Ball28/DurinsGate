"""Customer blueprint initialization"""
from flask import Blueprint

customer_bp = Blueprint('customer', __name__, url_prefix='/customer')

from customer import routes
