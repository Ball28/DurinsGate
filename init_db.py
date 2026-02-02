"""Database initialization script"""
import os
import sys
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from models import db
from models.user import User
from models.file import File
from models.file_assignment import FileAssignment
from auth.utils import generate_activation_token
from utils.email_service import send_welcome_email


def init_database():
    """Initialize database with tables and sample data"""
    app = create_app('development')
    
    with app.app_context():
        print("Creating database tables...")
        db.create_all()
        
        # Check if admin already exists
        admin = User.query.filter_by(username='admin').first()
        
        if not admin:
            print("\nCreating admin account...")
            admin = User(
                username='admin',
                email='admin@durinsgate.com',
                company_name='DurinsGate Administration',
                role='admin',
                is_active=True,
                terms_accepted=True
            )
            admin.set_password('Admin@12345678')  # Change this in production!
            db.session.add(admin)
            db.session.commit()
            
            print(f"✓ Admin account created")
            print(f"  Username: admin")
            print(f"  Password: Admin@12345678")
            print(f"  Email: admin@durinsgate.com")
        else:
            print("\n✓ Admin account already exists")
        
        # Create sample customers
        print("\nCreating sample customer accounts...")
        
        sample_customers = [
            {
                'username': 'acme_corp',
                'email': 'contact@acmecorp.com',
                'company_name': 'ACME Corporation',
                'contact_info': 'John Doe\n555-1234\nPurchasing Department'
            },
            {
                'username': 'globex',
                'email': 'admin@globex.com',
                'company_name': 'Globex Industries',
                'contact_info': 'Jane Smith\n555-5678\nEngineering'
            },
            {
                'username': 'initech',
                'email': 'support@initech.com',
                'company_name': 'Initech Solutions',
                'contact_info': 'Bob Johnson\n555-9012\nMaintenance'
            }
        ]
        
        created_customers = []
        for customer_data in sample_customers:
            existing = User.query.filter_by(username=customer_data['username']).first()
            if not existing:
                customer = User(
                    username=customer_data['username'],
                    email=customer_data['email'],
                    company_name=customer_data['company_name'],
                    contact_info=customer_data['contact_info'],
                    role='customer',
                    is_active=True,  # Set to True for demo purposes
                    terms_accepted=True  # Set to True for demo purposes
                )
                # Set a demo password (in production, use activation flow)
                customer.set_password('Customer@123')
                db.session.add(customer)
                created_customers.append(customer)
                print(f"  ✓ Created customer: {customer_data['username']}")
        
        db.session.commit()
        
        # Create sample files (metadata only - no actual files)
        print("\nCreating sample file records...")
        
        sample_files = [
            {
                'original_filename': 'DurinsGate_Pump_Model_X_Manual_v2.1.pdf',
                'category': 'User Manual',
                'product_type': 'Pump Model X',
                'version': 'v2.1',
                'description': 'Complete user manual for DurinsGate Pump Model X including installation, operation, and maintenance procedures.'
            },
            {
                'original_filename': 'Technical_Specifications_Valve_Series_Y.pdf',
                'category': 'Technical Specification',
                'product_type': 'Valve Series Y',
                'version': 'Rev C',
                'description': 'Detailed technical specifications and engineering drawings for Valve Series Y.'
            },
            {
                'original_filename': 'Safety_Guidelines_2024.pdf',
                'category': 'Safety Documentation',
                'product_type': 'General',
                'version': '2024',
                'description': 'Updated safety guidelines and compliance documentation for all DurinsGate products.'
            },
            {
                'original_filename': 'CAD_Drawings_Pump_X.zip',
                'category': 'CAD Files',
                'product_type': 'Pump Model X',
                'version': 'v2.1',
                'description': 'Complete CAD drawings in DWG and STEP formats for Pump Model X.'
            }
        ]
        
        created_files = []
        for file_data in sample_files:
            existing = File.query.filter_by(original_filename=file_data['original_filename']).first()
            if not existing:
                # Create a placeholder file path (in production, actual files would be uploaded)
                file_record = File(
                    filename=file_data['original_filename'],
                    original_filename=file_data['original_filename'],
                    file_path=f"uploads/sample/{file_data['original_filename']}",
                    file_size=1024000,  # 1MB placeholder
                    file_type=file_data['original_filename'].rsplit('.', 1)[1].lower(),
                    category=file_data['category'],
                    product_type=file_data['product_type'],
                    version=file_data['version'],
                    description=file_data['description'],
                    uploaded_by_id=admin.id
                )
                db.session.add(file_record)
                created_files.append(file_record)
                print(f"  ✓ Created file: {file_data['original_filename']}")
        
        db.session.commit()
        
        # Assign files to customers
        if created_customers and created_files:
            print("\nAssigning files to customers...")
            for customer in created_customers:
                for file in created_files[:2]:  # Assign first 2 files to each customer
                    assignment = FileAssignment(
                        user_id=customer.id,
                        file_id=file.id,
                        assigned_by_id=admin.id
                    )
                    db.session.add(assignment)
                    print(f"  ✓ Assigned '{file.original_filename}' to {customer.username}")
            
            db.session.commit()
        
        print("\n" + "="*60)
        print("Database initialization complete!")
        print("="*60)
        print("\nLogin Credentials:")
        print("-" * 60)
        print("\nADMIN ACCOUNT:")
        print("  URL: http://localhost:5000/auth/login")
        print("  Username: admin")
        print("  Password: Admin@12345678")
        print("\nSAMPLE CUSTOMER ACCOUNTS:")
        print("  Username: acme_corp, globex, or initech")
        print("  Password: Customer@123")
        print("\n" + "="*60)
        print("\nNOTE: Sample files are metadata only.")
        print("To test file downloads, upload actual files through the admin panel.")
        print("="*60)


if __name__ == '__main__':
    init_database()
