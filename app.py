import os
import logging
from datetime import timedelta

from dotenv import load_dotenv
load_dotenv()  # This loads the variables from .env

from flask import Flask
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase

# Configure logging
logging.basicConfig(level=logging.DEBUG)

# Base class for SQLAlchemy models
class Base(DeclarativeBase):
    pass

# Initialize extensions
db = SQLAlchemy(model_class=Base)
login_manager = LoginManager()
login_manager.session_protection = 'strong'

# Initialize the Flask application
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "canteen-automation-secret")
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SESSION_PERMANENT'] = False
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=2)

# Configure database with PostgreSQL 
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL")
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
}
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Initialize extensions with app
db.init_app(app)
login_manager.init_app(app)
login_manager.login_view = 'auth.login'
login_manager.login_message = 'Please log in to access this page.'
login_manager.login_message_category = 'warning'

# Import and register blueprints
from auth import auth_bp
from menu import menu_bp
from orders import orders_bp
from canteen import canteen_bp
from payments import payments_bp
from notifications import notifications_bp

app.register_blueprint(auth_bp)
app.register_blueprint(menu_bp)
app.register_blueprint(orders_bp)
app.register_blueprint(canteen_bp)
app.register_blueprint(payments_bp)
app.register_blueprint(notifications_bp)

# Import models and user loader
from models import load_user, User, MenuItem, Order, OrderItem
from models_extension import Canteen, BankAccount, Payment, Notification

login_manager.user_loader(load_user)

# Create tables and sample data on startup
with app.app_context():
    # Drop all tables and recreate them to handle schema changes
    db.drop_all()
    db.create_all()
    
    # Create sample data after tables exist
    from models import create_sample_data
    create_sample_data()

# Default route
@app.route('/')
def index():
    from flask import redirect, url_for
    return redirect(url_for('auth.login'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
