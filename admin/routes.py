"""Admin routes for customer and file management"""
from flask import render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from datetime import datetime
from sqlalchemy import func, desc
from admin import admin_bp
from admin.decorators import admin_required, audit_log
from admin.forms import (CustomerCreateForm, CustomerEditForm, FileUploadForm,
                        FileEditForm, FileAssignmentForm, BulkAssignmentForm)
from models import db
from models.user import User
from models.file import File
from models.file_assignment import FileAssignment
from models.download_log import DownloadLog
from models.login_attempt import LoginAttempt
from utils.file_handler import save_uploaded_file, delete_file, get_file_size
from utils.email_service import send_welcome_email, send_new_file_notification
from auth.utils import generate_activation_token, generate_secure_password


@admin_bp.route('/dashboard')
@login_required
@admin_required
def dashboard():
    """Admin dashboard with statistics"""
    # Get statistics
    total_customers = User.query.filter_by(role='customer').count()
    active_customers = User.query.filter_by(role='customer', is_active=True).count()
    total_files = File.query.filter_by(is_active=True).count()
    total_downloads = DownloadLog.query.filter_by(success=True).count()
    
    # Recent downloads
    recent_downloads = DownloadLog.query.filter_by(success=True)\
        .order_by(desc(DownloadLog.download_date))\
        .limit(10)\
        .all()
    
    # Recent login attempts
    recent_logins = LoginAttempt.query\
        .order_by(desc(LoginAttempt.timestamp))\
        .limit(10)\
        .all()
    
    # Top downloaded files
    top_files = db.session.query(
        File,
        func.count(DownloadLog.id).label('download_count')
    ).join(DownloadLog)\
     .group_by(File.id)\
     .order_by(desc('download_count'))\
     .limit(5)\
     .all()
    
    return render_template('admin/dashboard.html',
                         total_customers=total_customers,
                         active_customers=active_customers,
                         total_files=total_files,
                         total_downloads=total_downloads,
                         recent_downloads=recent_downloads,
                         recent_logins=recent_logins,
                         top_files=top_files)


@admin_bp.route('/customers')
@login_required
@admin_required
def customers():
    """List all customers"""
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '')
    
    query = User.query.filter_by(role='customer')
    
    if search:
        query = query.filter(
            db.or_(
                User.username.ilike(f'%{search}%'),
                User.email.ilike(f'%{search}%'),
                User.company_name.ilike(f'%{search}%')
            )
        )
    
    customers = query.order_by(User.created_at.desc()).paginate(
        page=page, per_page=20, error_out=False
    )
    
    return render_template('admin/customers.html', customers=customers, search=search)


@admin_bp.route('/customers/create', methods=['GET', 'POST'])
@login_required
@admin_required
@audit_log('create_customer')
def create_customer():
    """Create a new customer account"""
    form = CustomerCreateForm()
    
    if form.validate_on_submit():
        # Check if username or email already exists
        if User.query.filter_by(username=form.username.data).first():
            flash('Username already exists.', 'danger')
            return render_template('admin/customer_create.html', form=form)
        
        if User.query.filter_by(email=form.email.data).first():
            flash('Email already exists.', 'danger')
            return render_template('admin/customer_create.html', form=form)
        
        # Create new customer
        user = User(
            username=form.username.data,
            email=form.email.data,
            company_name=form.company_name.data,
            contact_info=form.contact_info.data,
            role='customer',
            is_active=False  # Will be activated when they set password
        )
        
        # Set a temporary password (will be changed on activation)
        temp_password = generate_secure_password()
        user.set_password(temp_password)
        
        db.session.add(user)
        db.session.commit()
        
        # Generate activation token and send welcome email
        activation_token = generate_activation_token(user.id)
        activation_url = url_for('auth.activate_account', token=activation_token, _external=True)
        
        send_welcome_email(user, activation_url)
        
        flash(f'Customer account created successfully! Activation email sent to {user.email}', 'success')
        return redirect(url_for('admin.customers'))
    
    return render_template('admin/customer_create.html', form=form)


@admin_bp.route('/customers/<int:customer_id>')
@login_required
@admin_required
def customer_detail(customer_id):
    """View customer details"""
    customer = User.query.filter_by(id=customer_id, role='customer').first_or_404()
    
    # Get assigned files
    assigned_files = db.session.query(File, FileAssignment)\
        .join(FileAssignment, File.id == FileAssignment.file_id)\
        .filter(FileAssignment.user_id == customer_id)\
        .filter(FileAssignment.is_active == True)\
        .all()
    
    # Get download history
    downloads = DownloadLog.query.filter_by(user_id=customer_id)\
        .order_by(desc(DownloadLog.download_date))\
        .limit(20)\
        .all()
    
    # Get login history
    logins = LoginAttempt.query.filter_by(username=customer.username)\
        .order_by(desc(LoginAttempt.timestamp))\
        .limit(20)\
        .all()
    
    return render_template('admin/customer_detail.html',
                         customer=customer,
                         assigned_files=assigned_files,
                         downloads=downloads,
                         logins=logins)


@admin_bp.route('/customers/<int:customer_id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
@audit_log('edit_customer')
def edit_customer(customer_id):
    """Edit customer account"""
    customer = User.query.filter_by(id=customer_id, role='customer').first_or_404()
    form = CustomerEditForm(obj=customer)
    
    if form.validate_on_submit():
        # Check if email is taken by another user
        existing = User.query.filter_by(email=form.email.data).first()
        if existing and existing.id != customer_id:
            flash('Email already exists.', 'danger')
            return render_template('admin/customer_edit.html', form=form, customer=customer)
        
        customer.email = form.email.data
        customer.company_name = form.company_name.data
        customer.contact_info = form.contact_info.data
        customer.is_active = form.is_active.data
        
        db.session.commit()
        
        flash('Customer updated successfully!', 'success')
        return redirect(url_for('admin.customer_detail', customer_id=customer_id))
    
    return render_template('admin/customer_edit.html', form=form, customer=customer)


@admin_bp.route('/customers/<int:customer_id>/toggle-active', methods=['POST'])
@login_required
@admin_required
@audit_log('toggle_customer_active')
def toggle_customer_active(customer_id):
    """Toggle customer active status"""
    customer = User.query.filter_by(id=customer_id, role='customer').first_or_404()
    customer.is_active = not customer.is_active
    db.session.commit()
    
    status = 'activated' if customer.is_active else 'deactivated'
    flash(f'Customer account {status} successfully!', 'success')
    return redirect(url_for('admin.customer_detail', customer_id=customer_id))


@admin_bp.route('/files')
@login_required
@admin_required
def files():
    """List all files"""
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '')
    category = request.args.get('category', '')
    
    query = File.query.filter_by(is_active=True)
    
    if search:
        query = query.filter(
            db.or_(
                File.original_filename.ilike(f'%{search}%'),
                File.description.ilike(f'%{search}%'),
                File.product_type.ilike(f'%{search}%')
            )
        )
    
    if category:
        query = query.filter_by(category=category)
    
    files = query.order_by(desc(File.upload_date)).paginate(
        page=page, per_page=20, error_out=False
    )
    
    # Get all categories for filter
    categories = db.session.query(File.category).distinct().all()
    categories = [c[0] for c in categories if c[0]]
    
    return render_template('admin/files.html', 
                         files=files, 
                         search=search,
                         category=category,
                         categories=categories)


@admin_bp.route('/files/upload', methods=['GET', 'POST'])
@login_required
@admin_required
@audit_log('upload_file')
def upload_file():
    """Upload a new file"""
    form = FileUploadForm()
    
    if form.validate_on_submit():
        file = form.file.data
        
        # Save file
        success, filename, filepath, error = save_uploaded_file(file, form.category.data)
        
        if not success:
            flash(error, 'danger')
            return render_template('admin/file_upload.html', form=form)
        
        # Get file size
        file_size = get_file_size(filepath)
        
        # Determine display name
        display_name = form.original_filename.data if form.original_filename.data else file.filename
        
        # Create file record
        file_record = File(
            filename=filename,
            original_filename=display_name,
            file_path=filepath,
            file_size=file_size,
            file_type=filename.rsplit('.', 1)[1].lower() if '.' in filename else '',
            category=form.category.data,
            product_type=form.product_type.data,
            version=form.version.data,
            description=form.description.data,
            uploaded_by_id=current_user.id
        )
        
        db.session.add(file_record)
        db.session.commit()
        
        flash('File uploaded successfully!', 'success')
        return redirect(url_for('admin.files'))
    
    return render_template('admin/file_upload.html', form=form)


@admin_bp.route('/files/<int:file_id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
@audit_log('edit_file')
def edit_file(file_id):
    """Edit file metadata"""
    file = File.query.get_or_404(file_id)
    form = FileEditForm(obj=file)
    
    if form.validate_on_submit():
        file.original_filename = form.original_filename.data
        file.category = form.category.data
        file.product_type = form.product_type.data
        file.version = form.version.data
        file.description = form.description.data
        file.is_active = form.is_active.data
        
        db.session.commit()
        
        flash('File updated successfully!', 'success')
        return redirect(url_for('admin.files'))
    
    return render_template('admin/file_edit.html', form=form, file=file)


@admin_bp.route('/files/<int:file_id>/delete', methods=['POST'])
@login_required
@admin_required
@audit_log('delete_file')
def delete_file_record(file_id):
    """Delete a file (soft delete)"""
    file = File.query.get_or_404(file_id)
    
    # Soft delete - just mark as inactive
    file.is_active = False
    db.session.commit()
    
    flash('File deleted successfully!', 'success')
    return redirect(url_for('admin.files'))


@admin_bp.route('/assignments')
@login_required
@admin_required
def assignments():
    """View all file assignments"""
    page = request.args.get('page', 1, type=int)
    
    assignments = db.session.query(FileAssignment, User, File)\
        .join(User, FileAssignment.user_id == User.id)\
        .join(File, FileAssignment.file_id == File.id)\
        .filter(FileAssignment.is_active == True)\
        .order_by(desc(FileAssignment.assigned_date))\
        .paginate(page=page, per_page=20, error_out=False)
    
    return render_template('admin/assignments.html', assignments=assignments)


@admin_bp.route('/assignments/create', methods=['GET', 'POST'])
@login_required
@admin_required
@audit_log('create_assignment')
def create_assignment():
    """Assign a file to a customer"""
    form = FileAssignmentForm()
    
    # Populate choices
    form.customer_id.choices = [(u.id, f"{u.username} - {u.company_name}") 
                                 for u in User.query.filter_by(role='customer', is_active=True).all()]
    form.file_id.choices = [(f.id, f"{f.original_filename} ({f.category})") 
                            for f in File.query.filter_by(is_active=True).all()]
    
    if form.validate_on_submit():
        # Check if assignment already exists
        existing = FileAssignment.query.filter_by(
            user_id=form.customer_id.data,
            file_id=form.file_id.data,
            is_active=True
        ).first()
        
        if existing:
            flash('This file is already assigned to this customer.', 'warning')
            return render_template('admin/assignment_create.html', form=form)
        
        # Create assignment
        assignment = FileAssignment(
            user_id=form.customer_id.data,
            file_id=form.file_id.data,
            assigned_by_id=current_user.id,
            expiration_date=form.expiration_date.data
        )
        
        db.session.add(assignment)
        db.session.commit()
        
        # Send notification email
        user = User.query.get(form.customer_id.data)
        file = File.query.get(form.file_id.data)
        send_new_file_notification(user, file, current_user)
        
        flash('File assigned successfully! Notification email sent.', 'success')
        return redirect(url_for('admin.assignments'))
    
    return render_template('admin/assignment_create.html', form=form)


@admin_bp.route('/assignments/bulk', methods=['GET', 'POST'])
@login_required
@admin_required
@audit_log('bulk_assignment')
def bulk_assignment():
    """Bulk assign a file to multiple customers"""
    form = BulkAssignmentForm()
    
    # Populate choices
    form.file_id.choices = [(f.id, f"{f.original_filename} ({f.category})") 
                            for f in File.query.filter_by(is_active=True).all()]
    form.customer_ids.choices = [(u.id, f"{u.username} - {u.company_name}") 
                                  for u in User.query.filter_by(role='customer', is_active=True).all()]
    
    if form.validate_on_submit():
        file = File.query.get(form.file_id.data)
        assigned_count = 0
        
        for customer_id in form.customer_ids.data:
            # Check if assignment already exists
            existing = FileAssignment.query.filter_by(
                user_id=customer_id,
                file_id=form.file_id.data,
                is_active=True
            ).first()
            
            if not existing:
                assignment = FileAssignment(
                    user_id=customer_id,
                    file_id=form.file_id.data,
                    assigned_by_id=current_user.id,
                    expiration_date=form.expiration_date.data
                )
                db.session.add(assignment)
                assigned_count += 1
                
                # Send notification if requested
                if form.send_notification.data:
                    user = User.query.get(customer_id)
                    send_new_file_notification(user, file, current_user)
        
        db.session.commit()
        
        flash(f'File assigned to {assigned_count} customer(s) successfully!', 'success')
        return redirect(url_for('admin.assignments'))
    
    return render_template('admin/bulk_assignment.html', form=form)


@admin_bp.route('/assignments/<int:assignment_id>/revoke', methods=['POST'])
@login_required
@admin_required
@audit_log('revoke_assignment')
def revoke_assignment(assignment_id):
    """Revoke a file assignment"""
    assignment = FileAssignment.query.get_or_404(assignment_id)
    assignment.is_active = False
    db.session.commit()
    
    flash('File assignment revoked successfully!', 'success')
    return redirect(url_for('admin.assignments'))


@admin_bp.route('/activity')
@login_required
@admin_required
def activity():
    """View download activity logs"""
    page = request.args.get('page', 1, type=int)
    user_id = request.args.get('user_id', type=int)
    file_id = request.args.get('file_id', type=int)
    
    query = DownloadLog.query
    
    if user_id:
        query = query.filter_by(user_id=user_id)
    
    if file_id:
        query = query.filter_by(file_id=file_id)
    
    logs = query.order_by(desc(DownloadLog.download_date)).paginate(
        page=page, per_page=50, error_out=False
    )
    
    return render_template('admin/activity.html', logs=logs)


@admin_bp.route('/audit')
@login_required
@admin_required
def audit():
    """View security audit logs"""
    page = request.args.get('page', 1, type=int)
    username = request.args.get('username', '')
    
    query = LoginAttempt.query
    
    if username:
        query = query.filter(LoginAttempt.username.ilike(f'%{username}%'))
    
    logs = query.order_by(desc(LoginAttempt.timestamp)).paginate(
        page=page, per_page=50, error_out=False
    )
    
    return render_template('admin/audit.html', logs=logs, username=username)
