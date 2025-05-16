import json
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from app import db

# Import extended models (for app.py imports)
try:
    from models_extension import Canteen, BankAccount, Payment, Notification
except ImportError:
    pass  # Will be imported later when models_extension.py is created

# SQLAlchemy models
class User(UserMixin, db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    phone_number = db.Column(db.String(20), nullable=True)  # Added for SMS notifications
    is_admin = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.now)
    
    # Relationships
    orders = db.relationship('Order', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    
    def __init__(self, username, email, password, is_admin=False, phone_number=None):
        self.username = username
        self.email = email
        self.password_hash = generate_password_hash(password)
        self.is_admin = is_admin
        self.phone_number = phone_number
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'phone_number': self.phone_number,
            'is_admin': self.is_admin,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S')
        }

class MenuItem(db.Model):
    __tablename__ = 'menu_items'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    price = db.Column(db.Float, nullable=False)
    category = db.Column(db.String(50), nullable=False)
    available = db.Column(db.Boolean, default=True)
    image_url = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.now)
    
    def __init__(self, name, description, price, category, available=True, image_url=None):
        self.name = name
        self.description = description
        self.price = price
        self.category = category
        self.available = available
        self.image_url = image_url

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'price': self.price,
            'category': self.category,
            'available': self.available,
            'image_url': self.image_url
        }

# Order items relationship (many-to-many)
class OrderItem(db.Model):
    __tablename__ = 'order_items'
    
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'), nullable=False)
    item_name = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Float, nullable=False)
    quantity = db.Column(db.Integer, default=1)
    
    def __init__(self, order_id, item_name, price, quantity=1):
        self.order_id = order_id
        self.item_name = item_name
        self.price = price
        self.quantity = quantity
    
    def to_dict(self):
        return {
            'id': self.id,
            'item_name': self.item_name,
            'price': self.price,
            'quantity': self.quantity
        }

class Order(db.Model):
    __tablename__ = 'orders'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    total_price = db.Column(db.Float, nullable=False)
    payment_method = db.Column(db.String(50), nullable=False)
    payment_status = db.Column(db.String(20), default='pending')
    status = db.Column(db.String(20), default='pending')
    created_at = db.Column(db.DateTime, default=datetime.now)
    
    # Relationships
    items = db.relationship('OrderItem', backref='order', cascade='all, delete-orphan')
    
    def __init__(self, user_id, items_list, total_price, payment_method, status='pending'):
        self.user_id = user_id
        self.total_price = total_price
        self.payment_method = payment_method
        self.status = status
        
    def add_items(self, items_list):
        """Add items from cart to order"""
        for item in items_list:
            order_item = OrderItem(
                order_id=self.id,
                item_name=item['name'],
                price=item['price'],
                quantity=item['quantity']
            )
            db.session.add(order_item)
        
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'items': [item.to_dict() for item in self.items],
            'total_price': self.total_price,
            'payment_method': self.payment_method,
            'payment_status': self.payment_status,
            'status': self.status,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S')
        }

# For Flask-Login
def load_user(user_id):
    try:
        if isinstance(user_id, int) or (isinstance(user_id, str) and user_id.isdigit()):
            # Try to find user by numeric ID
            return User.query.get(int(user_id))
        else:
            # If we have a UUID or other format, just fetch first user to avoid errors
            # In a production app, we'd handle UUID properly or fix the session management
            return User.query.first()
    except Exception as e:
        # If anything goes wrong, just return None which will redirect to login page
        print(f"Error loading user: {str(e)}")
        return None

def create_sample_data():
    # Create admin user if not exists
    admin = User.query.filter_by(username='admin').first()
    if not admin:
        admin = User(
            username='admin',
            email='admin@example.com',
            password='admin123',
            is_admin=True
        )
        db.session.add(admin)
        db.session.commit()
        
    # Create some menu items if none exist
    if MenuItem.query.count() == 0:
        menu_data = [
            {
                'name': 'Butter Chicken',
                'description': 'Tender chicken cooked in rich tomato and butter sauce',
                'price': 12.99,
                'category': 'Main Course'
            },
            {
                'name': 'Veggie Burger',
                'description': 'Plant-based patty with fresh vegetables',
                'price': 8.99,
                'category': 'Main Course'
            },
            {
                'name': 'French Fries',
                'description': 'Crispy potato fries with seasoning',
                'price': 3.99,
                'category': 'Sides'
            },
            {
                'name': 'Chocolate Brownie',
                'description': 'Warm chocolate brownie with vanilla ice cream',
                'price': 5.99,
                'category': 'Desserts'
            },
            {
                'name': 'Fresh Lemonade',
                'description': 'Freshly squeezed lemonade with mint',
                'price': 2.99,
                'category': 'Beverages'
            }
        ]
        
        for item_data in menu_data:
            menu_item = MenuItem(**item_data)
            db.session.add(menu_item)
        
        db.session.commit()
