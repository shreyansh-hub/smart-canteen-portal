from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_required, current_user
from models_extension import Canteen, BankAccount
from app import db

canteen_bp = Blueprint('canteen', __name__)

@canteen_bp.route('/canteen/register', methods=['GET', 'POST'])
@login_required
def register_canteen():
    # Check if user already has a registered canteen
    existing_canteen = Canteen.query.filter_by(owner_id=current_user.id).first()
    if existing_canteen:
        flash('You already have a registered canteen', 'warning')
        return redirect(url_for('canteen.manage_canteen'))
    
    if request.method == 'POST':
        name = request.form.get('name')
        address = request.form.get('address')
        contact_number = request.form.get('contact_number')
        email = request.form.get('email')
        description = request.form.get('description')
        
        # Validate inputs
        if not name or not address or not contact_number or not email:
            flash('All fields are required except description', 'danger')
            return render_template('canteen/register.html')
        
        # Check if email already exists
        if Canteen.query.filter_by(email=email).first():
            flash('Email already registered with another canteen', 'danger')
            return render_template('canteen/register.html')
        
        # Create new canteen
        canteen = Canteen(
            name=name,
            address=address,
            contact_number=contact_number,
            email=email,
            owner_id=current_user.id,
            description=description
        )
        
        db.session.add(canteen)
        db.session.commit()
        
        flash('Canteen registered successfully! Please add your bank details.', 'success')
        return redirect(url_for('canteen.add_bank_details', canteen_id=canteen.id))
    
    return render_template('canteen/register.html')

@canteen_bp.route('/canteen/bank-details/<int:canteen_id>', methods=['GET', 'POST'])
@login_required
def add_bank_details(canteen_id):
    canteen = Canteen.query.get(canteen_id)
    
    if not canteen or canteen.owner_id != current_user.id:
        flash('Canteen not found or you do not have permission', 'danger')
        return redirect(url_for('canteen.register_canteen'))
    
    if canteen.bank_details:
        flash('Bank details already added. You can update them below.', 'info')
        return redirect(url_for('canteen.update_bank_details', canteen_id=canteen_id))
    
    if request.method == 'POST':
        account_holder = request.form.get('account_holder')
        account_number = request.form.get('account_number')
        bank_name = request.form.get('bank_name')
        ifsc_code = request.form.get('ifsc_code')
        upi_id = request.form.get('upi_id')
        
        # Validate inputs
        if not account_holder or not account_number or not bank_name or not ifsc_code:
            flash('All fields are required except UPI ID', 'danger')
            return render_template('canteen/bank_details.html', canteen=canteen)
        
        # Create bank details
        bank_account = BankAccount(
            canteen_id=canteen_id,
            account_holder=account_holder,
            account_number=account_number,
            bank_name=bank_name,
            ifsc_code=ifsc_code,
            upi_id=upi_id
        )
        
        db.session.add(bank_account)
        db.session.commit()
        
        flash('Bank details added successfully!', 'success')
        return redirect(url_for('canteen.manage_canteen'))
    
    return render_template('canteen/bank_details.html', canteen=canteen)

@canteen_bp.route('/canteen/update-bank-details/<int:canteen_id>', methods=['GET', 'POST'])
@login_required
def update_bank_details(canteen_id):
    canteen = Canteen.query.get(canteen_id)
    
    if not canteen or canteen.owner_id != current_user.id:
        flash('Canteen not found or you do not have permission', 'danger')
        return redirect(url_for('canteen.register_canteen'))
    
    bank_account = canteen.bank_details
    if not bank_account:
        flash('No bank details found. Please add your bank details.', 'warning')
        return redirect(url_for('canteen.add_bank_details', canteen_id=canteen_id))
    
    if request.method == 'POST':
        bank_account.account_holder = request.form.get('account_holder')
        bank_account.account_number = request.form.get('account_number')
        bank_account.bank_name = request.form.get('bank_name')
        bank_account.ifsc_code = request.form.get('ifsc_code')
        bank_account.upi_id = request.form.get('upi_id')
        
        db.session.commit()
        
        flash('Bank details updated successfully!', 'success')
        return redirect(url_for('canteen.manage_canteen'))
    
    return render_template('canteen/update_bank_details.html', canteen=canteen, bank_account=bank_account)

@canteen_bp.route('/canteen/manage')
@login_required
def manage_canteen():
    canteen = Canteen.query.filter_by(owner_id=current_user.id).first()
    
    if not canteen:
        flash('No canteen found. Please register a canteen.', 'warning')
        return redirect(url_for('canteen.register_canteen'))
    
    return render_template('canteen/manage.html', canteen=canteen)

@canteen_bp.route('/admin/canteens')
@login_required
def admin_canteens():
    if not current_user.is_admin:
        flash('Access denied: Admin privileges required', 'danger')
        return redirect(url_for('menu.user_dashboard'))
    
    canteens = Canteen.query.all()
    return render_template('admin/canteens.html', canteens=canteens)

@canteen_bp.route('/admin/canteen/<int:canteen_id>/update-status', methods=['POST'])
@login_required
def update_canteen_status(canteen_id):
    if not current_user.is_admin:
        flash('Access denied: Admin privileges required', 'danger')
        return redirect(url_for('menu.user_dashboard'))
    
    canteen = Canteen.query.get(canteen_id)
    
    if not canteen:
        flash('Canteen not found', 'danger')
        return redirect(url_for('canteen.admin_canteens'))
    
    status = request.form.get('status')
    if status not in ['pending', 'approved', 'rejected']:
        flash('Invalid status', 'danger')
        return redirect(url_for('canteen.admin_canteens'))
    
    canteen.status = status
    db.session.commit()
    
    flash(f'Canteen status updated to {status}', 'success')
    return redirect(url_for('canteen.admin_canteens'))