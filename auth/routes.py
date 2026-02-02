"""Authentication routes"""
from flask import render_template, redirect, url_for, flash, request, session
from flask_login import login_user, logout_user, current_user, login_required
from datetime import datetime
from auth import auth_bp
from auth.forms import (LoginForm, PasswordResetRequestForm, PasswordResetForm,
                        SetPasswordForm, MFASetupForm, MFAVerifyForm)
from auth.utils import (validate_password_strength, generate_password_reset_token,
                        verify_password_reset_token, generate_mfa_secret,
                        generate_mfa_qr_uri, verify_mfa_token, get_client_ip,
                        get_user_agent, verify_activation_token)
from models import db
from models.user import User
from models.login_attempt import LoginAttempt
from utils.email_service import send_email
from flask import current_app
import qrcode
import io
import base64


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """User login with security features"""
    if current_user.is_authenticated:
        if current_user.is_admin():
            return redirect(url_for('admin.dashboard'))
        return redirect(url_for('customer.dashboard'))
    
    form = LoginForm()
    
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        
        user = User.query.filter_by(username=username).first()
        
        # Log the login attempt
        ip_address = get_client_ip()
        user_agent = get_user_agent()
        
        # Check if user exists
        if not user:
            log_attempt = LoginAttempt(
                username=username,
                ip_address=ip_address,
                user_agent=user_agent,
                success=False,
                failure_reason='Invalid username'
            )
            db.session.add(log_attempt)
            db.session.commit()
            
            flash('Invalid username or password', 'danger')
            return render_template('auth/login.html', form=form)
        
        # Check if account is locked
        if user.is_account_locked():
            log_attempt = LoginAttempt(
                username=username,
                ip_address=ip_address,
                user_agent=user_agent,
                success=False,
                failure_reason='Account locked'
            )
            db.session.add(log_attempt)
            db.session.commit()
            
            flash('Account is locked due to too many failed login attempts. Please try again later or contact support.', 'danger')
            return render_template('auth/login.html', form=form)
        
        # Check if account is active
        if not user.is_active:
            log_attempt = LoginAttempt(
                username=username,
                ip_address=ip_address,
                user_agent=user_agent,
                success=False,
                failure_reason='Account inactive'
            )
            db.session.add(log_attempt)
            db.session.commit()
            
            flash('Account is inactive. Please contact support.', 'danger')
            return render_template('auth/login.html', form=form)
        
        # Verify password
        if not user.check_password(password):
            user.increment_failed_login()
            
            log_attempt = LoginAttempt(
                username=username,
                ip_address=ip_address,
                user_agent=user_agent,
                success=False,
                failure_reason='Invalid password'
            )
            db.session.add(log_attempt)
            db.session.commit()
            
            # Check if we should lock the account
            if user.failed_login_attempts >= current_app.config['MAX_LOGIN_ATTEMPTS']:
                user.lock_account(current_app.config['ACCOUNT_LOCKOUT_DURATION'])
                flash(f'Account locked due to {current_app.config["MAX_LOGIN_ATTEMPTS"]} failed login attempts. Please try again later.', 'danger')
            else:
                remaining = current_app.config['MAX_LOGIN_ATTEMPTS'] - user.failed_login_attempts
                flash(f'Invalid username or password. {remaining} attempts remaining.', 'danger')
            
            return render_template('auth/login.html', form=form)
        
        # Password is correct - reset failed attempts
        user.reset_failed_login()
        
        # Check if MFA is enabled
        if user.mfa_enabled:
            # Store user ID in session for MFA verification
            session['mfa_user_id'] = user.id
            session['mfa_remember_me'] = form.remember_me.data
            return redirect(url_for('auth.verify_mfa'))
        
        # Log successful login
        log_attempt = LoginAttempt(
            username=username,
            ip_address=ip_address,
            user_agent=user_agent,
            success=True
        )
        db.session.add(log_attempt)
        
        # Update last login
        user.last_login = datetime.utcnow()
        db.session.commit()
        
        # Log the user in
        login_user(user, remember=form.remember_me.data)
        
        flash('Login successful!', 'success')
        
        # Redirect to appropriate dashboard
        next_page = request.args.get('next')
        if next_page:
            return redirect(next_page)
        
        if user.is_admin():
            return redirect(url_for('admin.dashboard'))
        else:
            # Check if user needs to accept terms
            if not user.terms_accepted:
                return redirect(url_for('customer.accept_terms'))
            return redirect(url_for('customer.dashboard'))
    
    return render_template('auth/login.html', form=form)


@auth_bp.route('/logout')
@login_required
def logout():
    """User logout"""
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('auth.login'))


@auth_bp.route('/activate/<token>', methods=['GET', 'POST'])
def activate_account(token):
    """Activate account and set password"""
    if current_user.is_authenticated:
        return redirect(url_for('customer.dashboard'))
    
    user_id = verify_activation_token(token)
    if not user_id:
        flash('Invalid or expired activation link.', 'danger')
        return redirect(url_for('auth.login'))
    
    user = User.query.get(user_id)
    if not user:
        flash('User not found.', 'danger')
        return redirect(url_for('auth.login'))
    
    if user.is_active and user.last_login:
        flash('Account already activated.', 'info')
        return redirect(url_for('auth.login'))
    
    form = SetPasswordForm()
    
    if form.validate_on_submit():
        user.set_password(form.password.data)
        user.is_active = True
        db.session.commit()
        
        flash('Account activated successfully! You can now log in.', 'success')
        return redirect(url_for('auth.login'))
    
    return render_template('auth/activate.html', form=form, user=user)


@auth_bp.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    """Request password reset"""
    if current_user.is_authenticated:
        return redirect(url_for('customer.dashboard'))
    
    form = PasswordResetRequestForm()
    
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        
        if user:
            token = generate_password_reset_token(user.id)
            reset_url = url_for('auth.reset_password', token=token, _external=True)
            
            # Send password reset email
            send_email(
                to=user.email,
                subject='Password Reset Request',
                template='emails/password_reset.html',
                user=user,
                reset_url=reset_url
            )
        
        # Always show success message to prevent email enumeration
        flash('If an account exists with that email, a password reset link has been sent.', 'info')
        return redirect(url_for('auth.login'))
    
    return render_template('auth/forgot_password.html', form=form)


@auth_bp.route('/reset-password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    """Reset password with token"""
    if current_user.is_authenticated:
        return redirect(url_for('customer.dashboard'))
    
    user_id = verify_password_reset_token(token)
    if not user_id:
        flash('Invalid or expired password reset link.', 'danger')
        return redirect(url_for('auth.forgot_password'))
    
    user = User.query.get(user_id)
    if not user:
        flash('User not found.', 'danger')
        return redirect(url_for('auth.forgot_password'))
    
    form = PasswordResetForm()
    
    if form.validate_on_submit():
        user.set_password(form.password.data)
        user.reset_failed_login()  # Reset any failed login attempts
        if user.is_locked:
            user.unlock_account()  # Unlock account if locked
        db.session.commit()
        
        flash('Password reset successful! You can now log in with your new password.', 'success')
        return redirect(url_for('auth.login'))
    
    return render_template('auth/reset_password.html', form=form)


@auth_bp.route('/setup-mfa', methods=['GET', 'POST'])
@login_required
def setup_mfa():
    """Setup MFA for user account"""
    if current_user.mfa_enabled:
        flash('MFA is already enabled for your account.', 'info')
        return redirect(url_for('customer.dashboard'))
    
    form = MFASetupForm()
    
    # Generate MFA secret if not already in session
    if 'mfa_secret' not in session:
        session['mfa_secret'] = generate_mfa_secret()
    
    mfa_secret = session['mfa_secret']
    
    # Generate QR code
    qr_uri = generate_mfa_qr_uri(current_user.username, mfa_secret)
    qr = qrcode.make(qr_uri)
    
    # Convert QR code to base64 for display
    buffer = io.BytesIO()
    qr.save(buffer, format='PNG')
    qr_base64 = base64.b64encode(buffer.getvalue()).decode()
    
    if form.validate_on_submit():
        if verify_mfa_token(mfa_secret, form.token.data):
            current_user.mfa_secret = mfa_secret
            current_user.mfa_enabled = True
            db.session.commit()
            
            # Clear session
            session.pop('mfa_secret', None)
            
            flash('MFA enabled successfully!', 'success')
            return redirect(url_for('customer.dashboard'))
        else:
            flash('Invalid verification code. Please try again.', 'danger')
    
    return render_template('auth/setup_mfa.html', form=form, 
                         qr_code=qr_base64, secret=mfa_secret)


@auth_bp.route('/verify-mfa', methods=['GET', 'POST'])
def verify_mfa():
    """Verify MFA token during login"""
    if current_user.is_authenticated:
        return redirect(url_for('customer.dashboard'))
    
    if 'mfa_user_id' not in session:
        flash('Invalid MFA verification request.', 'danger')
        return redirect(url_for('auth.login'))
    
    user = User.query.get(session['mfa_user_id'])
    if not user:
        session.pop('mfa_user_id', None)
        flash('User not found.', 'danger')
        return redirect(url_for('auth.login'))
    
    form = MFAVerifyForm()
    
    if form.validate_on_submit():
        if verify_mfa_token(user.mfa_secret, form.token.data):
            # Log successful login
            log_attempt = LoginAttempt(
                username=user.username,
                ip_address=get_client_ip(),
                user_agent=get_user_agent(),
                success=True
            )
            db.session.add(log_attempt)
            
            # Update last login
            user.last_login = datetime.utcnow()
            db.session.commit()
            
            # Log the user in
            remember_me = session.get('mfa_remember_me', False)
            login_user(user, remember=remember_me)
            
            # Clear session
            session.pop('mfa_user_id', None)
            session.pop('mfa_remember_me', None)
            
            flash('Login successful!', 'success')
            
            if user.is_admin():
                return redirect(url_for('admin.dashboard'))
            else:
                if not user.terms_accepted:
                    return redirect(url_for('customer.accept_terms'))
                return redirect(url_for('customer.dashboard'))
        else:
            flash('Invalid verification code. Please try again.', 'danger')
    
    return render_template('auth/verify_mfa.html', form=form)


@auth_bp.route('/disable-mfa', methods=['POST'])
@login_required
def disable_mfa():
    """Disable MFA for user account"""
    current_user.mfa_enabled = False
    current_user.mfa_secret = None
    db.session.commit()
    
    flash('MFA disabled successfully.', 'success')
    return redirect(url_for('customer.dashboard'))
