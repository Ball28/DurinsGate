"""Authentication forms with validation"""
from flask_wtf import FlaskForm, RecaptchaField
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Email, Length, EqualTo, ValidationError
from flask import current_app
from auth.utils import validate_password_strength


class LoginForm(FlaskForm):
    """Login form with CAPTCHA"""
    username = StringField('Username', validators=[
        DataRequired(message='Username is required'),
        Length(min=3, max=80)
    ])
    password = PasswordField('Password', validators=[
        DataRequired(message='Password is required')
    ])
    remember_me = BooleanField('Remember Me')
    recaptcha = RecaptchaField()
    submit = SubmitField('Login')

    def __init__(self, *args, **kwargs):
        super(LoginForm, self).__init__(*args, **kwargs)
        if not current_app.config.get('RECAPTCHA_ENABLED'):
            del self.recaptcha


class PasswordResetRequestForm(FlaskForm):
    """Request password reset form"""
    email = StringField('Email Address', validators=[
        DataRequired(message='Email is required'),
        Email(message='Invalid email address')
    ])
    recaptcha = RecaptchaField()
    submit = SubmitField('Request Password Reset')

    def __init__(self, *args, **kwargs):
        super(PasswordResetRequestForm, self).__init__(*args, **kwargs)
        if not current_app.config.get('RECAPTCHA_ENABLED'):
            del self.recaptcha


class PasswordResetForm(FlaskForm):
    """Reset password form with strength validation"""
    password = PasswordField('New Password', validators=[
        DataRequired(message='Password is required'),
        Length(min=12, message='Password must be at least 12 characters')
    ])
    password_confirm = PasswordField('Confirm Password', validators=[
        DataRequired(message='Please confirm your password'),
        EqualTo('password', message='Passwords must match')
    ])
    submit = SubmitField('Reset Password')
    
    def validate_password(self, field):
        """Custom validator for password strength"""
        is_valid, error_message = validate_password_strength(field.data)
        if not is_valid:
            raise ValidationError(error_message)


class SetPasswordForm(FlaskForm):
    """Set password form for account activation"""
    password = PasswordField('Password', validators=[
        DataRequired(message='Password is required'),
        Length(min=12, message='Password must be at least 12 characters')
    ])
    password_confirm = PasswordField('Confirm Password', validators=[
        DataRequired(message='Please confirm your password'),
        EqualTo('password', message='Passwords must match')
    ])
    submit = SubmitField('Activate Account')
    
    def validate_password(self, field):
        """Custom validator for password strength"""
        is_valid, error_message = validate_password_strength(field.data)
        if not is_valid:
            raise ValidationError(error_message)


class MFASetupForm(FlaskForm):
    """MFA setup form"""
    token = StringField('Verification Code', validators=[
        DataRequired(message='Verification code is required'),
        Length(min=6, max=6, message='Code must be 6 digits')
    ])
    submit = SubmitField('Enable MFA')


class MFAVerifyForm(FlaskForm):
    """MFA verification form"""
    token = StringField('Verification Code', validators=[
        DataRequired(message='Verification code is required'),
        Length(min=6, max=6, message='Code must be 6 digits')
    ])
    submit = SubmitField('Verify')
