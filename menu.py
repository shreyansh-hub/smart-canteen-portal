from flask import Blueprint, render_template, redirect, url_for, request, flash, jsonify, session
from flask_login import login_required, current_user
from models import MenuItem
from app import db

menu_bp = Blueprint('menu', __name__)

@menu_bp.route('/admin/dashboard')
@login_required
def admin_dashboard():
    if not current_user.is_admin:
        flash('Access denied: Admin privileges required', 'danger')
        return redirect(url_for('menu.user_dashboard'))
    
    return render_template('admin/dashboard.html')

@menu_bp.route('/admin/menu')
@login_required
def admin_menu():
    if not current_user.is_admin:
        flash('Access denied: Admin privileges required', 'danger')
        return redirect(url_for('menu.user_dashboard'))
    
    menu_list = MenuItem.query.all()
    categories = db.session.query(MenuItem.category).distinct().order_by(MenuItem.category).all()
    categories = [category[0] for category in categories]
    
    return render_template('admin/menu_management.html', menu_items=menu_list, categories=categories)

@menu_bp.route('/admin/menu/add', methods=['POST'])
@login_required
def add_menu_item():
    if not current_user.is_admin:
        flash('Access denied: Admin privileges required', 'danger')
        return redirect(url_for('menu.user_dashboard'))
    
    name = request.form.get('name')
    description = request.form.get('description')
    price = request.form.get('price')
    category = request.form.get('category')
    
    # Validate inputs
    if not name or not price or not category:
        flash('Name, price and category are required', 'danger')
        return redirect(url_for('menu.admin_menu'))
    
    try:
        price = float(price)
    except ValueError:
        flash('Price must be a number', 'danger')
        return redirect(url_for('menu.admin_menu'))
    
    # Create new menu item
    menu_item = MenuItem(
        name=name,
        description=description,
        price=price,
        category=category
    )
    
    db.session.add(menu_item)
    db.session.commit()
    
    flash('Menu item added successfully', 'success')
    return redirect(url_for('menu.admin_menu'))

@menu_bp.route('/admin/menu/toggle-availability/<int:item_id>')
@login_required
def toggle_availability(item_id):
    if not current_user.is_admin:
        flash('Access denied: Admin privileges required', 'danger')
        return redirect(url_for('menu.user_dashboard'))
    
    menu_item = MenuItem.query.get(item_id)
    
    if menu_item:
        menu_item.available = not menu_item.available
        db.session.commit()
        status = 'available' if menu_item.available else 'unavailable'
        flash(f'Item is now {status}', 'success')
    else:
        flash('Item not found', 'danger')
    
    return redirect(url_for('menu.admin_menu'))

@menu_bp.route('/admin/menu/delete/<int:item_id>')
@login_required
def delete_menu_item(item_id):
    if not current_user.is_admin:
        flash('Access denied: Admin privileges required', 'danger')
        return redirect(url_for('menu.user_dashboard'))
    
    menu_item = MenuItem.query.get(item_id)
    
    if menu_item:
        db.session.delete(menu_item)
        db.session.commit()
        flash('Item deleted successfully', 'success')
    else:
        flash('Item not found', 'danger')
    
    return redirect(url_for('menu.admin_menu'))

@menu_bp.route('/user/dashboard')
@login_required
def user_dashboard():
    if current_user.is_admin:
        return redirect(url_for('menu.admin_dashboard'))
    
    return render_template('user/dashboard.html')

@menu_bp.route('/user/menu')
@login_required
def user_menu():
    menu_list = MenuItem.query.filter_by(available=True).all()
    categories = db.session.query(MenuItem.category).filter(MenuItem.available == True).distinct().order_by(MenuItem.category).all()
    categories = [category[0] for category in categories]
    
    # Initialize cart in session if it doesn't exist
    if 'cart' not in session:
        session['cart'] = []
    
    return render_template('user/menu.html', menu_items=menu_list, categories=categories)

@menu_bp.route('/api/add-to-cart', methods=['POST'])
@login_required
def add_to_cart():
    if current_user.is_admin:
        return jsonify({'success': False, 'message': 'Admin cannot place orders'})
    
    data = request.get_json()
    item_id = data.get('item_id')
    quantity = int(data.get('quantity', 1))
    
    # Get menu item from database
    menu_item = MenuItem.query.get(item_id)
    
    if not menu_item:
        return jsonify({'success': False, 'message': 'Item not found'})
    
    if not menu_item.available:
        return jsonify({'success': False, 'message': 'Item is not available'})
    
    # Initialize cart in session if it doesn't exist
    if 'cart' not in session:
        session['cart'] = []
    
    cart = session['cart']
    
    # Check if item already in cart
    found = False
    for item in cart:
        if int(item['id']) == int(item_id):
            item['quantity'] += quantity
            found = True
            break
    
    # If not found, add to cart
    if not found:
        cart.append({
            'id': menu_item.id,
            'name': menu_item.name,
            'price': menu_item.price,
            'quantity': quantity
        })
    
    session['cart'] = cart
    
    return jsonify({
        'success': True, 
        'message': 'Item added to cart',
        'cart_count': sum(item['quantity'] for item in cart)
    })

@menu_bp.route('/user/cart')
@login_required
def view_cart():
    if current_user.is_admin:
        return redirect(url_for('menu.admin_dashboard'))
    
    if 'cart' not in session:
        session['cart'] = []
    
    cart = session['cart']
    total = sum(item['price'] * item['quantity'] for item in cart)
    
    return render_template('user/cart.html', cart=cart, total=total)

@menu_bp.route('/api/update-cart', methods=['POST'])
@login_required
def update_cart():
    if current_user.is_admin:
        return jsonify({'success': False, 'message': 'Admin cannot place orders'})
    
    data = request.get_json()
    item_id = data.get('item_id')
    quantity = int(data.get('quantity', 0))
    
    if 'cart' not in session:
        return jsonify({'success': False, 'message': 'Cart is empty'})
    
    cart = session['cart']
    
    if quantity <= 0:
        # Remove item from cart
        cart = [item for item in cart if int(item['id']) != int(item_id)]
    else:
        # Update quantity
        for item in cart:
            if int(item['id']) == int(item_id):
                item['quantity'] = quantity
                break
    
    session['cart'] = cart
    total = sum(item['price'] * item['quantity'] for item in cart)
    
    return jsonify({
        'success': True, 
        'message': 'Cart updated',
        'cart_count': sum(item['quantity'] for item in cart),
        'total': total
    })

@menu_bp.route('/api/clear-cart', methods=['POST'])
@login_required
def clear_cart():
    if 'cart' in session:
        session['cart'] = []
    
    return jsonify({'success': True, 'message': 'Cart cleared'})
