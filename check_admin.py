from app import create_app
from models import db, User

app = create_app('development')
with app.app_context():
    user = User.query.filter_by(username='admin').first()
    if user:
        print(f"Username: {user.username}")
        print(f"Active: {user.is_active}")
        print(f"Locked: {user.is_locked}")
        print(f"Failed Attempts: {user.failed_login_attempts}")
        if user.is_locked:
            print("Unlocking account...")
            user.unlock_account()
            print("Account unlocked.")
    else:
        print("User not found")
