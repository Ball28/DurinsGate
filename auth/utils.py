"""Authentication utilities for password validation, token generation, and security"""
import re
import jwt
from datetime import datetime, timedelta
from flask import current_app, request
import pyotp
import secrets


def validate_password_strength(password):
    """
    Validate password meets security requirements:
    - Minimum 12 characters
    - At least one uppercase letter
    - At least one lowercase letter
    - At least one number
    - At least one special character
    
    Returns: (is_valid, error_message)
    """
    if len(password) < 12:
        return False, "Password must be at least 12 characters long"
    
    if not re.search(r'[A-Z]', password):
        return False, "Password must contain at least one uppercase letter"
    
    if not re.search(r'[a-z]', password):
        return False, "Password must contain at least one lowercase letter"
    
    if not re.search(r'\d', password):
        return False, "Password must contain at least one number"
    
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        return False, "Password must contain at least one special character (!@#$%^&*(),.?\":{}|<>)"
    
    return True, None


def generate_password_reset_token(user_id):
    """Generate a secure token for password reset"""
    expiration = datetime.utcnow() + current_app.config['PASSWORD_RESET_EXPIRATION']
    
    payload = {
        'user_id': user_id,
        'purpose': 'password_reset',
        'exp': expiration,
        'iat': datetime.utcnow()
    }
    
    token = jwt.encode(
        payload,
        current_app.config['SECRET_KEY'],
        algorithm='HS256'
    )
    
    return token


def verify_password_reset_token(token):
    """Verify and decode a password reset token"""
    try:
        payload = jwt.decode(
            token,
            current_app.config['SECRET_KEY'],
            algorithms=['HS256']
        )
        
        if payload.get('purpose') != 'password_reset':
            return None
        
        return payload.get('user_id')
    except jwt.ExpiredSignatureError:
        return None  # Token expired
    except jwt.InvalidTokenError:
        return None  # Invalid token


def generate_mfa_secret():
    """Generate a new MFA secret for TOTP"""
    return pyotp.random_base32()


def generate_mfa_qr_uri(username, secret):
    """Generate a QR code URI for MFA setup"""
    company_name = current_app.config['COMPANY_NAME']
    totp = pyotp.TOTP(secret)
    return totp.provisioning_uri(
        name=username,
        issuer_name=f"{company_name} Portal"
    )


def verify_mfa_token(secret, token):
    """Verify a TOTP token"""
    totp = pyotp.TOTP(secret)
    # Allow 1 period before and after for clock skew
    return totp.verify(token, valid_window=1)


def get_client_ip():
    """Get the client's IP address, accounting for proxies"""
    if request.headers.get('X-Forwarded-For'):
        # Get the first IP in the chain (client IP)
        return request.headers.get('X-Forwarded-For').split(',')[0].strip()
    elif request.headers.get('X-Real-IP'):
        return request.headers.get('X-Real-IP')
    else:
        return request.remote_addr


def get_user_agent():
    """Get the client's user agent string"""
    return request.headers.get('User-Agent', 'Unknown')


def generate_activation_token(user_id):
    """Generate a secure token for account activation"""
    expiration = datetime.utcnow() + timedelta(days=7)  # 7 days to activate
    
    payload = {
        'user_id': user_id,
        'purpose': 'account_activation',
        'exp': expiration,
        'iat': datetime.utcnow()
    }
    
    token = jwt.encode(
        payload,
        current_app.config['SECRET_KEY'],
        algorithm='HS256'
    )
    
    return token


def verify_activation_token(token):
    """Verify and decode an account activation token"""
    try:
        payload = jwt.decode(
            token,
            current_app.config['SECRET_KEY'],
            algorithms=['HS256']
        )
        
        if payload.get('purpose') != 'account_activation':
            return None
        
        return payload.get('user_id')
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None


def generate_secure_password():
    """Generate a secure random password for initial account creation"""
    # Generate a password that meets all requirements
    import string
    
    # Ensure we have at least one of each required character type
    password_chars = [
        secrets.choice(string.ascii_uppercase),
        secrets.choice(string.ascii_lowercase),
        secrets.choice(string.digits),
        secrets.choice('!@#$%^&*(),.?":{}|<>')
    ]
    
    # Fill the rest with random characters
    all_chars = string.ascii_letters + string.digits + '!@#$%^&*(),.?":{}|<>'
    password_chars.extend(secrets.choice(all_chars) for _ in range(12))
    
    # Shuffle to avoid predictable patterns
    secrets.SystemRandom().shuffle(password_chars)
    
    return ''.join(password_chars)
