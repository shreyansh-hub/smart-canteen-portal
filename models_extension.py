from datetime import datetime, timedelta
import secrets
from app import db
from models import User

# Canteen Registration Model
class Canteen(db.Model):
    __tablename__ = 'canteens'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    address = db.Column(db.Text, nullable=False)
    contact_number = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(120), nullable=False, unique=True)
    description = db.Column(db.Text)
    owner_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now)
    status = db.Column(db.String(20), default='pending')  # pending, approved, rejected
    
    # Relationships
    bank_details = db.relationship('BankAccount', backref='canteen', uselist=False, cascade='all, delete-orphan')
    
    def __init__(self, name, address, contact_number, email, owner_id, description=None):
        self.name = name
        self.address = address
        self.contact_number = contact_number
        self.email = email
        self.owner_id = owner_id
        self.description = description
        
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'address': self.address,
            'contact_number': self.contact_number,
            'email': self.email,
            'description': self.description,
            'status': self.status,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S')
        }

# Bank Account Details
class BankAccount(db.Model):
    __tablename__ = 'bank_accounts'
    
    id = db.Column(db.Integer, primary_key=True)
    canteen_id = db.Column(db.Integer, db.ForeignKey('canteens.id'), nullable=False)
    account_holder = db.Column(db.String(100), nullable=False)
    account_number = db.Column(db.String(50), nullable=False)
    bank_name = db.Column(db.String(100), nullable=False)
    ifsc_code = db.Column(db.String(20), nullable=False)
    upi_id = db.Column(db.String(50))
    
    def __init__(self, canteen_id, account_holder, account_number, bank_name, ifsc_code, upi_id=None):
        self.canteen_id = canteen_id
        self.account_holder = account_holder
        self.account_number = account_number
        self.bank_name = bank_name
        self.ifsc_code = ifsc_code
        self.upi_id = upi_id
        
    def to_dict(self):
        return {
            'id': self.id,
            'canteen_id': self.canteen_id,
            'account_holder': self.account_holder,
            'account_number': self.account_number[-4:].rjust(len(self.account_number), '*'),  # Masked for security
            'bank_name': self.bank_name,
            'ifsc_code': self.ifsc_code,
            'upi_id': self.upi_id
        }

# Payment Details Model
class Payment(db.Model):
    __tablename__ = 'payments'
    
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    payment_method = db.Column(db.String(50), nullable=False)  # UPI, Card, Cash
    transaction_id = db.Column(db.String(100))
    payment_status = db.Column(db.String(20), default='pending')  # pending, successful, failed
    created_at = db.Column(db.DateTime, default=datetime.now)
    
    # Relationships
    order = db.relationship('Order', backref='payment_details')
    
    def __init__(self, order_id, amount, payment_method, transaction_id=None, payment_status='pending'):
        self.order_id = order_id
        self.amount = amount
        self.payment_method = payment_method
        self.transaction_id = transaction_id
        self.payment_status = payment_status
        
    def to_dict(self):
        return {
            'id': self.id,
            'order_id': self.order_id,
            'amount': self.amount,
            'payment_method': self.payment_method,
            'transaction_id': self.transaction_id,
            'payment_status': self.payment_status,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S')
        }

# Notification Model
class Notification(db.Model):
    __tablename__ = 'notifications'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    title = db.Column(db.String(100), nullable=False)
    message = db.Column(db.Text, nullable=False)
    notification_type = db.Column(db.String(20), nullable=False)  # email, sms
    is_read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.now)
    
    # Relationships
    user = db.relationship('User', backref='notifications')
    
    def __init__(self, user_id, title, message, notification_type):
        self.user_id = user_id
        self.title = title
        self.message = message
        self.notification_type = notification_type
        
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'title': self.title,
            'message': self.message,
            'notification_type': self.notification_type,
            'is_read': self.is_read,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S')
        }
        
# Password Reset Token Model
class PasswordResetToken(db.Model):
    __tablename__ = 'password_reset_tokens'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    token = db.Column(db.String(100), nullable=False, unique=True)
    expires_at = db.Column(db.DateTime, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now)
    
    # Relationships
    user = db.relationship('User', backref='reset_tokens')
    
    def __init__(self, user_id):
        self.user_id = user_id
        self.token = secrets.token_urlsafe(32)  # Generate a secure token
        self.expires_at = datetime.now() + timedelta(hours=1)  # Token expires in 1 hour
    
    def is_valid(self):
        return datetime.now() < self.expires_at
    
    @classmethod
    def get_valid_token(cls, token):
        """Retrieve a valid token by its value"""
        token_obj = cls.query.filter_by(token=token).first()
        if token_obj and token_obj.is_valid():
            return token_obj
        return None