import os
import sys
from app import create_app
from models import db, User, File

def verify_system():
    print("Verifying system setup...")
    app = create_app('testing')
    
    with app.app_context():
        # 1. Check Database Connection
        try:
            db.create_all()
            print("✅ Database connection successful")
        except Exception as e:
            print(f"❌ Database connection failed: {e}")
            return False

        # 2. Check Admin User
        try:
            admin = User.query.filter_by(username='admin').first()
            if admin:
                print("✅ Admin user exists")
            else:
                print("❌ Admin user missing")
                return False
        except Exception as e:
            print(f"❌ Admin user check failed: {e}")
            return False

        # 3. Check Directories
        upload_folder = app.config['UPLOAD_FOLDER']
        if os.path.exists(upload_folder):
            print(f"✅ Upload directory exists: {upload_folder}")
        else:
            print(f"❌ Upload directory missing: {upload_folder}")
            return False

        # 4. Check Blueprints
        blueprints = ['auth', 'admin', 'customer']
        for bp in blueprints:
            if bp in app.blueprints:
                print(f"✅ Blueprint '{bp}' registered")
            else:
                print(f"❌ Blueprint '{bp}' missing")
                return False

    print("\n🎉 System verification completed successfully!")
    return True

if __name__ == '__main__':
    if verify_system():
        sys.exit(0)
    else:
        sys.exit(1)
