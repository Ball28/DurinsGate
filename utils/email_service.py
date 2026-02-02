"""Email service for sending notifications"""
from flask import current_app, render_template
from flask_mail import Message
from models import mail
from threading import Thread


def send_async_email(app, msg):
    """Send email asynchronously"""
    with app.app_context():
        try:
            mail.send(msg)
        except Exception as e:
            # Log error (in production, use proper logging)
            print(f"Error sending email: {str(e)}")


def send_email(to, subject, template, **kwargs):
    """
    Send an email using a template
    
    Args:
        to: Recipient email address
        subject: Email subject
        template: Path to email template
        **kwargs: Variables to pass to template
    """
    app = current_app._get_current_object()
    
    msg = Message(
        subject=f"[{app.config['COMPANY_NAME']}] {subject}",
        recipients=[to] if isinstance(to, str) else to,
        sender=app.config['MAIL_DEFAULT_SENDER']
    )
    
    # Render HTML template
    msg.html = render_template(template, **kwargs)
    
    # Send asynchronously
    thread = Thread(target=send_async_email, args=(app, msg))
    thread.start()
    
    return thread


def send_welcome_email(user, activation_url):
    """Send welcome email with activation link"""
    return send_email(
        to=user.email,
        subject='Welcome to the Customer Portal',
        template='emails/welcome.html',
        user=user,
        activation_url=activation_url
    )


def send_password_reset_email(user, reset_url):
    """Send password reset email"""
    return send_email(
        to=user.email,
        subject='Password Reset Request',
        template='emails/password_reset.html',
        user=user,
        reset_url=reset_url
    )


def send_new_file_notification(user, file, assigned_by):
    """Send notification when new file is assigned"""
    return send_email(
        to=user.email,
        subject='New File Available',
        template='emails/new_file.html',
        user=user,
        file=file,
        assigned_by=assigned_by
    )


def send_file_update_notification(user, file, updated_by):
    """Send notification when file is updated"""
    return send_email(
        to=user.email,
        subject='File Updated',
        template='emails/file_update.html',
        user=user,
        file=file,
        updated_by=updated_by
    )


def send_download_confirmation(user, file):
    """Send download confirmation email (optional)"""
    return send_email(
        to=user.email,
        subject='Download Confirmation',
        template='emails/download_confirmation.html',
        user=user,
        file=file
    )
