import os
import logging
from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_required, current_user
from models import User, Order
from models_extension import Notification, Canteen
from app import db

# Configure module logger
logger = logging.getLogger(__name__)

notifications_bp = Blueprint('notifications', __name__)

# Email helper functions
def send_email(to_email, subject, html_content=None, text_content=None):
    """
    Send email using SendGrid
    """
    # Check if API key exists
    if not os.environ.get('SENDGRID_API_KEY'):
        logger.warning("SendGrid API key not found. Email not sent.")
        return False
    
    try:
        from sendgrid import SendGridAPIClient
        from sendgrid.helpers.mail import Mail, Email, To, Content
        
        sg = SendGridAPIClient(os.environ.get('SENDGRID_API_KEY'))
        
        from_email = Email("canteen@example.com")  # Replace with your verified sender
        to_email = To(to_email)
        
        message = Mail(
            from_email=from_email,
            to_emails=to_email,
            subject=subject
        )
        
        if html_content:
            message.content = Content("text/html", html_content)
        elif text_content:
            message.content = Content("text/plain", text_content)
        
        response = sg.send(message)
        logger.info(f"Email sent to {to_email} with status code {response.status_code}")
        return True
    except Exception as e:
        logger.error(f"Error sending email: {str(e)}")
        return False

# SMS helper functions
def send_sms(to_phone, message):
    """
    Send SMS using Twilio
    """
    # Check if Twilio credentials exist
    if not all([
        os.environ.get('TWILIO_ACCOUNT_SID'),
        os.environ.get('TWILIO_AUTH_TOKEN'),
        os.environ.get('TWILIO_PHONE_NUMBER')
    ]):
        logger.warning("Twilio credentials not found. SMS not sent.")
        return False
    
    try:
        from twilio.rest import Client
        
        account_sid = os.environ.get('TWILIO_ACCOUNT_SID')
        auth_token = os.environ.get('TWILIO_AUTH_TOKEN')
        from_number = os.environ.get('TWILIO_PHONE_NUMBER')
        
        client = Client(account_sid, auth_token)
        
        message = client.messages.create(
            body=message,
            from_=from_number,
            to=to_phone
        )
        
        logger.info(f"SMS sent to {to_phone} with SID: {message.sid}")
        return True
    except Exception as e:
        logger.error(f"Error sending SMS: {str(e)}")
        return False

# Notification creation
def create_notification(user_id, title, message, notification_type):
    """
    Create a notification record in the database
    """
    notification = Notification(
        user_id=user_id,
        title=title,
        message=message,
        notification_type=notification_type
    )
    
    db.session.add(notification)
    db.session.commit()
    return notification

# Welcome notification for new users
def send_welcome_notification(user):
    """
    Send welcome message to a new user
    """
    # Create notification in database
    create_notification(
        user_id=user.id,
        title="Welcome to Canteen Automation System",
        message=f"Hello {user.username}, welcome to our Canteen Automation System! We're excited to have you on board.",
        notification_type="email"
    )
    
    # Send email notification
    send_email(
        to_email=user.email,
        subject="Welcome to Canteen Automation System",
        html_content=f"""
        <div style="font-family: Arial, sans-serif; padding: 20px; max-width: 600px;">
            <h1 style="color: #4A6FFF;">Welcome to Canteen Automation System!</h1>
            <p>Hello {user.username},</p>
            <p>Thank you for registering with our Canteen Automation System. We're excited to have you on board!</p>
            <p>With our system, you can:</p>
            <ul>
                <li>Browse the menu from various canteens</li>
                <li>Place orders easily</li>
                <li>Pay securely using multiple methods</li>
                <li>Track your order status in real-time</li>
            </ul>
            <p>If you have any questions or need assistance, please don't hesitate to contact us.</p>
            <p>Happy ordering!</p>
            <p>The Canteen Automation Team</p>
        </div>
        """
    )

# Order confirmation notification
def send_order_notification(order):
    """
    Send order notification to both customer and canteen
    """
    # Get user info
    user = User.query.get(order.user_id)
    
    if not user:
        logger.error(f"User not found for order {order.id}")
        return False
    
    # Create customer notification
    create_notification(
        user_id=user.id,
        title=f"Order #{order.id} Confirmed",
        message=f"Your order has been confirmed and is being processed. Total: ${order.total_price:.2f}",
        notification_type="email"
    )
    
    # Send email to customer
    send_email(
        to_email=user.email,
        subject=f"Order #{order.id} Confirmed",
        html_content=f"""
        <div style="font-family: Arial, sans-serif; padding: 20px; max-width: 600px;">
            <h1 style="color: #4A6FFF;">Order Confirmation</h1>
            <p>Hello {user.username},</p>
            <p>Your order (#{order.id}) has been confirmed and is being processed.</p>
            <p><strong>Order Details:</strong></p>
            <ul>
                {''.join([f'<li>{item.item_name} x {item.quantity} - ${item.price * item.quantity:.2f}</li>' for item in order.items])}
            </ul>
            <p><strong>Total Amount:</strong> ${order.total_price:.2f}</p>
            <p><strong>Payment Method:</strong> {order.payment_method}</p>
            <p><strong>Order Status:</strong> {order.status.capitalize()}</p>
            <p>You will receive another notification when your order is ready for pickup.</p>
            <p>Thank you for your order!</p>
            <p>The Canteen Automation Team</p>
        </div>
        """
    )
    
    # TODO: Add notification for canteen owner
    return True

# Order ready notification
def send_order_ready_notification(order):
    """
    Send notification when order is ready for pickup
    """
    # Get user info
    user = User.query.get(order.user_id)
    
    if not user:
        logger.error(f"User not found for order {order.id}")
        return False
    
    # Create notification
    create_notification(
        user_id=user.id,
        title=f"Order #{order.id} Ready for Pickup",
        message=f"Your order is now ready for pickup. Order number: {order.id}",
        notification_type="sms"
    )
    
    # Send SMS to customer if phone number is available
    # Note: This is a placeholder, in a real app you'd store user's phone number
    # and get it from the user model
    if hasattr(user, 'phone_number') and user.phone_number:
        send_sms(
            to_phone=user.phone_number,
            message=f"Your order #{order.id} is ready for pickup. Thank you for using our Canteen Automation System!"
        )
    
    # Send email as backup
    send_email(
        to_email=user.email,
        subject=f"Order #{order.id} Ready for Pickup",
        html_content=f"""
        <div style="font-family: Arial, sans-serif; padding: 20px; max-width: 600px;">
            <h1 style="color: #4A6FFF;">Order Ready for Pickup</h1>
            <p>Hello {user.username},</p>
            <p>Great news! Your order (#{order.id}) is now ready for pickup.</p>
            <p><strong>Order Details:</strong></p>
            <ul>
                {''.join([f'<li>{item.item_name} x {item.quantity}</li>' for item in order.items])}
            </ul>
            <p>Please collect your order from the canteen counter.</p>
            <p>Thank you for using our Canteen Automation System!</p>
            <p>The Canteen Automation Team</p>
        </div>
        """
    )
    
    return True

# Blueprint routes
@notifications_bp.route('/notifications')
@login_required
def view_notifications():
    """
    View all notifications for current user
    """
    notifications = Notification.query.filter_by(user_id=current_user.id).order_by(Notification.created_at.desc()).all()
    return render_template('notifications/list.html', notifications=notifications)

@notifications_bp.route('/notifications/mark-read/<int:notification_id>')
@login_required
def mark_notification_read(notification_id):
    """
    Mark a notification as read
    """
    notification = Notification.query.get(notification_id)
    
    if not notification or notification.user_id != current_user.id:
        flash('Notification not found', 'danger')
        return redirect(url_for('notifications.view_notifications'))
    
    notification.is_read = True
    db.session.commit()
    
    flash('Notification marked as read', 'success')
    return redirect(url_for('notifications.view_notifications'))