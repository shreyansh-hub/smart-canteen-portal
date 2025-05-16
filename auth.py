import logging
from flask import Blueprint, render_template, redirect, url_for, request, flash, session
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash
from models import User
from models_extension import PasswordResetToken
from app import db, app
from notifications import send_email

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        if current_user.is_admin:
            return redirect(url_for('menu.admin_dashboard'))
        else:
            return redirect(url_for('menu.user_dashboard'))
            
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        # Find user by username
        user = User.query.filter_by(username=username).first()
        
        if user and user.check_password(password):
            login_user(user)
            next_page = request.args.get('next')
            
            if user.is_admin:
                return redirect(next_page or url_for('menu.admin_dashboard'))
            else:
                return redirect(next_page or url_for('menu.user_dashboard'))
        else:
            flash('Invalid username or password', 'danger')
    
    return render_template('login.html')

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('menu.user_dashboard'))
        
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        phone_number = request.form.get('phone_number')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        
        # Check if username already exists
        if User.query.filter_by(username=username).first():
            flash('Username already exists', 'danger')
            return render_template('register.html')
            
        # Check if email already exists
        if User.query.filter_by(email=email).first():
            flash('Email already exists', 'danger')
            return render_template('register.html')
            
        # Check if passwords match
        if password != confirm_password:
            flash('Passwords do not match', 'danger')
            return render_template('register.html')
            
        # Create new user
        user = User(
            username=username,
            email=email,
            password=password,
            phone_number=phone_number
        )
        
        # Save to database
        db.session.add(user)
        db.session.commit()
        
        # Send welcome notification
        try:
            from notifications import send_welcome_notification
            send_welcome_notification(user)
            logging.info(f"Welcome notification sent to user {user.id}")
        except Exception as e:
            logging.error(f"Error sending welcome notification: {str(e)}")
        
        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('auth.login'))
    
    return render_template('register.html')

@auth_bp.route('/logout')
@login_required
def logout():
    # Clear user's cart if exists
    if 'cart' in session:
        session.pop('cart')
    
    logout_user()
    flash('You have been logged out', 'info')
    return redirect(url_for('auth.login'))

@auth_bp.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    if current_user.is_authenticated:
        return redirect(url_for('menu.user_dashboard'))
        
    if request.method == 'POST':
        email = request.form.get('email')
        
        if not email:
            flash('Email is required', 'danger')
            return render_template('forgot_password.html')
            
        # Find user by email
        user = User.query.filter_by(email=email).first()
        
        if not user:
            # For security reasons, don't reveal that the email doesn't exist
            flash('If your email exists in our system, you will receive a password reset link shortly.', 'info')
            return redirect(url_for('auth.login'))
            
        # Delete existing tokens for this user
        existing_tokens = PasswordResetToken.query.filter_by(user_id=user.id).all()
        for token in existing_tokens:
            db.session.delete(token)
            
        # Create new token
        token = PasswordResetToken(user_id=user.id)
        db.session.add(token)
        db.session.commit()
        
        # Generate reset URL
        reset_url = url_for('auth.reset_password', token=token.token, _external=True)
        
        # Send email with reset link
        try:
            html_content = f"""
            <div style="font-family: Arial, sans-serif; padding: 20px; max-width: 600px;">
                <h1 style="color: #4A6FFF;">Reset Your Password</h1>
                <p>Hello {user.username},</p>
                <p>We received a request to reset your password for the Canteen Automation System.</p>
                <p>To reset your password, click the button below:</p>
                <p style="text-align: center;">
                    <a href="{reset_url}" style="background-color: #4A6FFF; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px; display: inline-block; margin: 20px 0;">Reset Password</a>
                </p>
                <p>If you didn't request this password reset, you can safely ignore this email. Your password will remain unchanged.</p>
                <p>This link will expire in 1 hour.</p>
                <p>The Canteen Automation Team</p>
            </div>
            """
            
            send_email(
                to_email=user.email,
                subject="Reset Your Password - Canteen Automation System",
                html_content=html_content
            )
            logging.info(f"Password reset email sent to {user.email}")
        except Exception as e:
            logging.error(f"Error sending password reset email: {str(e)}")
            
        flash('If your email exists in our system, you will receive a password reset link shortly.', 'info')
        return redirect(url_for('auth.login'))
        
    return render_template('forgot_password.html')

@auth_bp.route('/reset-password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for('menu.user_dashboard'))
        
    # Verify token
    token_obj = PasswordResetToken.get_valid_token(token)
    
    if not token_obj:
        flash('Invalid or expired password reset link', 'danger')
        return redirect(url_for('auth.login'))
        
    if request.method == 'POST':
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        
        if not password or not confirm_password:
            flash('Both password fields are required', 'danger')
            return render_template('reset_password.html', token=token)
            
        if password != confirm_password:
            flash('Passwords do not match', 'danger')
            return render_template('reset_password.html', token=token)
            
        # Update user's password
        user = User.query.get(token_obj.user_id)
        user.password_hash = generate_password_hash(password)
        
        # Delete the token and all other tokens for this user
        tokens = PasswordResetToken.query.filter_by(user_id=user.id).all()
        for t in tokens:
            db.session.delete(t)
            
        db.session.commit()
        
        flash('Your password has been reset successfully. Please log in with your new password.', 'success')
        return redirect(url_for('auth.login'))
        
    return render_template('reset_password.html', token=token)
