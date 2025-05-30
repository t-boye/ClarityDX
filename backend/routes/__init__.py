from flask import Blueprint

disease_bp = Blueprint("diseases", __name__)

from .diseases import *  # Import all route handlers
