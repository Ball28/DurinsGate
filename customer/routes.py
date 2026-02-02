"""Customer routes for file access and profile management"""
from flask import render_template, redirect, url_for, flash, request, send_file, abort
from flask_login import login_required, current_user
from datetime import datetime
from sqlalchemy import desc, or_
from customer import customer_bp
from customer.forms import ProfileUpdateForm, TermsAcceptanceForm
from models import db
from models.user import User
from models.file import File
from models.file_assignment import FileAssignment
from models.download_log import DownloadLog
from auth.utils import get_client_ip, get_user_agent
import os


def customer_required(f):
    """Decorator to ensure user is a customer (not admin)"""
    from functools import wraps
    
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if current_user.is_admin():
            flash('This page is for customers only.', 'warning')
            return redirect(url_for('admin.dashboard'))
        return f(*args, **kwargs)
    
    return decorated_function


@customer_bp.route('/dashboard')
@login_required
@customer_required
def dashboard():
    """Customer dashboard showing available files"""
    # Check if user needs to accept terms
    if not current_user.terms_accepted:
        return redirect(url_for('customer.accept_terms'))
    
    # Get assigned files
    assigned_files = db.session.query(File, FileAssignment)\
        .join(FileAssignment, File.id == FileAssignment.file_id)\
        .filter(FileAssignment.user_id == current_user.id)\
        .filter(FileAssignment.is_active == True)\
        .filter(File.is_active == True)\
        .order_by(desc(FileAssignment.assigned_date))\
        .all()
    
    # Filter out expired assignments
    available_files = []
    for file, assignment in assigned_files:
        if not assignment.is_expired():
            available_files.append((file, assignment))
    
    # Get recent downloads
    recent_downloads = DownloadLog.query.filter_by(
        user_id=current_user.id,
        success=True
    ).order_by(desc(DownloadLog.download_date)).limit(5).all()
    
    # Get statistics
    total_files = len(available_files)
    total_downloads = DownloadLog.query.filter_by(
        user_id=current_user.id,
        success=True
    ).count()
    
    return render_template('customer/dashboard.html',
                         available_files=available_files,
                         recent_downloads=recent_downloads,
                         total_files=total_files,
                         total_downloads=total_downloads)


@customer_bp.route('/files')
@login_required
@customer_required
def files():
    """List all available files with search and filter"""
    if not current_user.terms_accepted:
        return redirect(url_for('customer.accept_terms'))
    
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '')
    category = request.args.get('category', '')
    
    # Base query for assigned files
    query = db.session.query(File, FileAssignment)\
        .join(FileAssignment, File.id == FileAssignment.file_id)\
        .filter(FileAssignment.user_id == current_user.id)\
        .filter(FileAssignment.is_active == True)\
        .filter(File.is_active == True)
    
    # Apply search filter
    if search:
        query = query.filter(
            or_(
                File.original_filename.ilike(f'%{search}%'),
                File.description.ilike(f'%{search}%'),
                File.product_type.ilike(f'%{search}%'),
                File.category.ilike(f'%{search}%')
            )
        )
    
    # Apply category filter
    if category:
        query = query.filter(File.category == category)
    
    # Get paginated results
    files_page = query.order_by(desc(File.upload_date)).paginate(
        page=page, per_page=20, error_out=False
    )
    
    # Filter out expired assignments
    filtered_items = []
    for file, assignment in files_page.items:
        if not assignment.is_expired():
            filtered_items.append((file, assignment))
    
    # Get available categories for this user
    categories_query = db.session.query(File.category.distinct())\
        .join(FileAssignment, File.id == FileAssignment.file_id)\
        .filter(FileAssignment.user_id == current_user.id)\
        .filter(FileAssignment.is_active == True)\
        .filter(File.is_active == True)
    
    categories = [c[0] for c in categories_query.all() if c[0]]
    
    return render_template('customer/files.html',
                         files=filtered_items,
                         pagination=files_page,
                         search=search,
                         category=category,
                         categories=categories)


@customer_bp.route('/download/<int:file_id>')
@login_required
@customer_required
def download_file(file_id):
    """Generate download token and redirect to secure download"""
    if not current_user.terms_accepted:
        flash('You must accept the terms of service before downloading files.', 'warning')
        return redirect(url_for('customer.accept_terms'))
    
    file = File.query.get_or_404(file_id)
    
    # Verify user has access to this file
    if not file.is_assigned_to_user(current_user.id):
        flash('You do not have access to this file.', 'danger')
        return redirect(url_for('customer.files'))
    
    # Generate download token
    token = file.get_download_token(current_user.id)
    
    # Redirect to secure download endpoint
    return redirect(url_for('customer.secure_download', token=token))


@customer_bp.route('/secure-download/<token>')
def secure_download(token):
    """Secure file download with token verification"""
    # Verify token
    payload = File.verify_download_token(token)
    
    if not payload:
        flash('Invalid or expired download link.', 'danger')
        return redirect(url_for('customer.files'))
    
    file_id = payload.get('file_id')
    user_id = payload.get('user_id')
    
    # Get file
    file = File.query.get_or_404(file_id)
    
    # Verify file still exists and is accessible
    if not os.path.exists(file.file_path):
        # Log failed download
        log = DownloadLog(
            user_id=user_id,
            file_id=file_id,
            ip_address=get_client_ip(),
            user_agent=get_user_agent(),
            success=False,
            error_message='File not found on server'
        )
        db.session.add(log)
        db.session.commit()
        
        flash('File not found on server. Please contact support.', 'danger')
        return redirect(url_for('customer.files'))
    
    # Log successful download
    log = DownloadLog(
        user_id=user_id,
        file_id=file_id,
        ip_address=get_client_ip(),
        user_agent=get_user_agent(),
        success=True
    )
    db.session.add(log)
    db.session.commit()
    
    # Send file
    return send_file(
        file.file_path,
        as_attachment=True,
        download_name=file.original_filename
    )


@customer_bp.route('/download-history')
@login_required
@customer_required
def download_history():
    """View download history"""
    if not current_user.terms_accepted:
        return redirect(url_for('customer.accept_terms'))
    
    page = request.args.get('page', 1, type=int)
    
    downloads = DownloadLog.query.filter_by(user_id=current_user.id)\
        .order_by(desc(DownloadLog.download_date))\
        .paginate(page=page, per_page=20, error_out=False)
    
    return render_template('customer/download_history.html', downloads=downloads)


@customer_bp.route('/profile', methods=['GET', 'POST'])
@login_required
@customer_required
def profile():
    """View and update profile"""
    form = ProfileUpdateForm(obj=current_user)
    
    if form.validate_on_submit():
        # Check if email is taken by another user
        existing = User.query.filter_by(email=form.email.data).first()
        if existing and existing.id != current_user.id:
            flash('Email already exists.', 'danger')
            return render_template('customer/profile.html', form=form)
        
        current_user.email = form.email.data
        current_user.company_name = form.company_name.data
        current_user.contact_info = form.contact_info.data
        
        db.session.commit()
        
        flash('Profile updated successfully!', 'success')
        return redirect(url_for('customer.profile'))
    
    return render_template('customer/profile.html', form=form)


@customer_bp.route('/accept-terms', methods=['GET', 'POST'])
@login_required
@customer_required
def accept_terms():
    """Accept terms of service"""
    if current_user.terms_accepted:
        return redirect(url_for('customer.dashboard'))
    
    form = TermsAcceptanceForm()
    
    if form.validate_on_submit():
        current_user.terms_accepted = True
        current_user.terms_accepted_date = datetime.utcnow()
        db.session.commit()
        
        flash('Terms accepted. Welcome to the portal!', 'success')
        return redirect(url_for('customer.dashboard'))
    
    return render_template('customer/accept_terms.html', form=form)
