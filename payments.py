import os
import json
import stripe
from flask import Blueprint, render_template, redirect, url_for, request, flash, jsonify, session, current_app
from flask_login import login_required, current_user
from models import Order
from models_extension import Payment
from app import db

# Set up Stripe with API key
stripe.api_key = os.environ.get('STRIPE_SECRET_KEY')

payments_bp = Blueprint('payments', __name__)

@payments_bp.route('/payment/process/<int:order_id>', methods=['POST'])
@login_required
def process_payment(order_id):
    if current_user.is_admin:
        flash('Admin cannot make payments', 'danger')
        return redirect(url_for('menu.admin_dashboard'))
    
    order = Order.query.get(order_id)
    
    if not order:
        flash('Order not found', 'danger')
        return redirect(url_for('menu.user_dashboard'))
    
    # Ensure the order belongs to the current user
    if order.user_id != current_user.id:
        flash('Access denied', 'danger')
        return redirect(url_for('menu.user_dashboard'))
    
    payment_method = request.form.get('payment_method')
    
    if not payment_method:
        flash('Please select a payment method', 'danger')
        return redirect(url_for('orders.checkout'))
    
    # Create payment record
    payment = Payment(
        order_id=order_id,
        amount=order.total_price,
        payment_method=payment_method
    )
    
    db.session.add(payment)
    
    # Get the domain for success/cancel URLs
    domain_url = request.host_url.rstrip('/')
    
    # Process payment based on method
    if payment_method == 'UPI':
        # For UPI, create a payment link that can be shared
        try:
            # Format amount for Stripe (in paise/cents)
            amount_in_cents = int(order.total_price * 100)
            
            payment_link = stripe.PaymentLink.create(
                line_items=[{
                    'price_data': {
                        'currency': 'inr',
                        'product_data': {
                            'name': f'Order #{order.id}',
                            'description': f'Payment for order #{order.id} via UPI',
                        },
                        'unit_amount': amount_in_cents,
                    },
                    'quantity': 1,
                }],
                payment_method_types=['upi'],
                after_completion={
                    'type': 'redirect',
                    'redirect': {
                        'url': f"{domain_url}{url_for('orders.order_confirmation', order_id=order_id)}",
                    },
                },
                metadata={
                    'order_id': order.id,
                    'user_id': current_user.id
                }
            )
            
            payment.transaction_id = f"pending_{payment_link.id}"
            payment.payment_status = 'pending'
            order.payment_status = 'pending'
            
            db.session.commit()
            
            # Redirect to the payment link
            return redirect(payment_link.url)
            
        except Exception as e:
            flash(f'Error processing UPI payment: {str(e)}', 'danger')
            return redirect(url_for('orders.checkout'))
        
    elif payment_method == 'Card':
        try:
            # Format amount for Stripe (in paise/cents)
            amount_in_cents = int(order.total_price * 100)
            
            # Create a Stripe Checkout Session
            checkout_session = stripe.checkout.Session.create(
                payment_method_types=['card'],
                line_items=[{
                    'price_data': {
                        'currency': 'inr',
                        'product_data': {
                            'name': f'Order #{order.id}',
                        },
                        'unit_amount': amount_in_cents,
                    },
                    'quantity': 1,
                }],
                mode='payment',
                success_url=f"{domain_url}{url_for('orders.order_confirmation', order_id=order_id)}",
                cancel_url=f"{domain_url}{url_for('menu.view_cart')}",
                metadata={
                    'order_id': order.id,
                    'user_id': current_user.id
                }
            )
            
            payment.transaction_id = f"pending_{checkout_session.id}"
            payment.payment_status = 'pending'
            order.payment_status = 'pending'
            
            db.session.commit()
            
            # Redirect to Stripe Checkout
            return redirect(checkout_session.url)
            
        except Exception as e:
            flash(f'Error processing card payment: {str(e)}', 'danger')
            return redirect(url_for('orders.checkout'))
        
    elif payment_method == 'Cash':
        # Cash payment
        payment.payment_status = 'pending'
        order.payment_status = 'pending'
        db.session.commit()
        
        flash('Cash payment will be collected at delivery!', 'success')
        return redirect(url_for('orders.order_confirmation', order_id=order_id))
    
    db.session.commit()
    
    flash('Payment initiated successfully!', 'success')
    return redirect(url_for('orders.order_confirmation', order_id=order_id))

@payments_bp.route('/payment/confirm/<int:order_id>', methods=['POST'])
@login_required
def confirm_payment(order_id):
    if not current_user.is_admin:
        flash('Access denied: Admin privileges required', 'danger')
        return redirect(url_for('menu.user_dashboard'))
    
    order = Order.query.get(order_id)
    
    if not order:
        flash('Order not found', 'danger')
        return redirect(url_for('orders.admin_orders'))
    
    payment = Payment.query.filter_by(order_id=order_id).first()
    
    if not payment:
        flash('Payment record not found', 'danger')
        return redirect(url_for('orders.admin_orders'))
    
    payment.payment_status = 'successful'
    order.payment_status = 'paid'
    db.session.commit()
    
    flash('Payment confirmed successfully!', 'success')
    return redirect(url_for('orders.admin_orders'))

@payments_bp.route('/payment/history')
@login_required
def payment_history():
    if current_user.is_admin:
        payments = Payment.query.join(Order).order_by(Payment.created_at.desc()).all()
        return render_template('admin/payment_history.html', payments=payments)
    else:
        payments = Payment.query.join(Order).filter(Order.user_id == current_user.id).order_by(Payment.created_at.desc()).all()
        return render_template('user/payment_history.html', payments=payments)