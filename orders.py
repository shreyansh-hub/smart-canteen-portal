from datetime import datetime
from flask import Blueprint, render_template, redirect, url_for, request, flash, session, jsonify
from flask_login import login_required, current_user
from models import Order, OrderItem
from app import db

orders_bp = Blueprint('orders', __name__)

@orders_bp.route('/user/checkout', methods=['GET', 'POST'])
@login_required
def checkout():
    if current_user.is_admin:
        flash('Admin cannot place orders', 'danger')
        return redirect(url_for('menu.admin_dashboard'))
    
    if 'cart' not in session or not session['cart']:
        flash('Your cart is empty', 'warning')
        return redirect(url_for('menu.user_menu'))
    
    cart = session['cart']
    total = sum(item['price'] * item['quantity'] for item in cart)
    
    if request.method == 'POST':
        payment_method = request.form.get('payment_method')
        
        if not payment_method:
            flash('Please select a payment method', 'danger')
            return render_template('user/cart.html', cart=cart, total=total)
        
        # Create order
        order = Order(
            user_id=current_user.id,
            items_list=cart,  # Just passing for the constructor, will be added below
            total_price=total,
            payment_method=payment_method,
            status='confirmed'  # Simulating successful payment
        )
        
        # Save to database first to get the order id
        db.session.add(order)
        db.session.flush()  # Get the ID without committing
        
        # Add order items
        for item in cart:
            order_item = OrderItem(
                order_id=order.id,
                item_name=item['name'],
                price=item['price'],
                quantity=item['quantity']
            )
            db.session.add(order_item)
        
        # Commit all changes
        db.session.commit()
        
        # Clear cart
        session['cart'] = []
        
        # TODO: Implement email notifications for order placed
        
        return redirect(url_for('orders.order_confirmation', order_id=order.id))
    
    return render_template('user/cart.html', cart=cart, total=total)

@orders_bp.route('/user/order-confirmation/<int:order_id>')
@login_required
def order_confirmation(order_id):
    if current_user.is_admin:
        flash('Admin cannot place orders', 'danger')
        return redirect(url_for('menu.admin_dashboard'))
    
    order = Order.query.get(order_id)
    
    if not order:
        flash('Order not found', 'danger')
        return redirect(url_for('menu.user_dashboard'))
    
    # Ensure the order belongs to the current user
    if order.user_id != current_user.id:
        flash('Access denied', 'danger')
        return redirect(url_for('menu.user_dashboard'))
    
    return render_template('user/order_confirmation.html', order=order)

@orders_bp.route('/user/orders')
@login_required
def user_orders():
    if current_user.is_admin:
        flash('Admin cannot view user orders from this page', 'danger')
        return redirect(url_for('menu.admin_dashboard'))
    
    user_orders_list = Order.query.filter_by(user_id=current_user.id).order_by(Order.created_at.desc()).all()
    
    return render_template('user/dashboard.html', orders=user_orders_list)

@orders_bp.route('/admin/orders')
@login_required
def admin_orders():
    if not current_user.is_admin:
        flash('Access denied: Admin privileges required', 'danger')
        return redirect(url_for('menu.user_dashboard'))
    
    all_orders = Order.query.order_by(Order.created_at.desc()).all()
    
    return render_template('admin/dashboard.html', orders=all_orders)

@orders_bp.route('/admin/order/<int:order_id>/update-status', methods=['POST'])
@login_required
def update_order_status(order_id):
    if not current_user.is_admin:
        flash('Access denied: Admin privileges required', 'danger')
        return redirect(url_for('menu.user_dashboard'))
    
    order = Order.query.get(order_id)
    
    if not order:
        flash('Order not found', 'danger')
        return redirect(url_for('orders.admin_orders'))
    
    status = request.form.get('status')
    if status not in ['pending', 'confirmed', 'preparing', 'ready', 'delivered', 'cancelled']:
        flash('Invalid status', 'danger')
        return redirect(url_for('orders.admin_orders'))
    
    order.status = status
    db.session.commit()
    
    # TODO: Send notification to customer if status is 'ready'
    
    flash(f'Order status updated to {status}', 'success')
    
    return redirect(url_for('orders.admin_orders'))
