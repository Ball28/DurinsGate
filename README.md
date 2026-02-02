# DurinsGate Secure Customer Portal

A professional, secure web portal enabling DurinsGate customers to authenticate and download manuals/files with comprehensive admin controls and enterprise-grade security features.

Please note, this is a working proof of concept and should not be used on a production level in this current state. 

## 🎯 Features

### Customer Features
- ✅ Secure login with username/password
- ✅ Multi-factor authentication (MFA) via email/authenticator app
- ✅ Password reset functionality
- ✅ Session timeout after 15 minutes of inactivity
- ✅ Account lockout after 5 failed login attempts
- ✅ Browse and search assigned files
- ✅ Secure, token-based file downloads (30-minute expiration)
- ✅ Download history tracking
- ✅ Profile management
- ✅ Terms of Service acceptance

### Admin Features
- ✅ Customer account management (create, edit, disable)
- ✅ File upload and management
- ✅ File assignment to customers (individual and bulk)
- ✅ Download activity monitoring
- ✅ Security audit logs
- ✅ Login attempt tracking
- ✅ Dashboard with statistics
- ✅ Expiration dates for file access

### Security Features
- ✅ bcrypt password hashing
- ✅ HTTPS/SSL ready
- ✅ CSRF protection
- ✅ Session management with secure cookies
- ✅ Rate limiting
- ✅ IP logging for all activities
- ✅ Temporary download tokens
- ✅ Security headers (XSS, clickjacking protection)
- ✅ Account lockout mechanism
- ✅ Comprehensive audit logging

## 📋 Requirements

- Python 3.8+
- pip
- Virtual environment (recommended)

## 🚀 Quick Start

### 1. Clone or Navigate to Project

```bash
cd c:\Users\eball\Desktop\Code\DurinsGate
```

### 2. Create Virtual Environment

```bash
python -m venv venv
```

### 3. Activate Virtual Environment

**Windows:**
```bash
venv\Scripts\activate
```

**Linux/Mac:**
```bash
source venv/bin/activate
```

### 4. Install Dependencies

```bash
pip install -r requirements.txt
```

### 5. Configure Environment Variables

Copy `.env.example` to `.env` and update the values:

```bash
copy .env.example .env
```

**Important settings to configure:**

```env
SECRET_KEY=your-secret-key-here  # Generate a strong random key
MAIL_USERNAME=your-email@example.com
MAIL_PASSWORD=your-app-password
```

**To generate a secret key:**
```python
python -c "import secrets; print(secrets.token_hex(32))"
```

### 6. Initialize Database

```bash
python init_db.py
```

This will create:
- Database tables
- Admin account (username: `admin`, password: `Admin@12345678`)
- Sample customer accounts
- Sample file records

### 7. Run the Application

```bash
python app.py
```

The application will be available at: **http://localhost:5000**

## 👤 Default Login Credentials

### Admin Account
- **URL:** http://localhost:5000/auth/login
- **Username:** `admin`
- **Password:** `Admin@12345678`

### Sample Customer Accounts
- **Usernames:** `acme_corp`, `globex`, or `initech`
- **Password:** `Customer@123`

**⚠️ IMPORTANT:** Change these passwords in production!

## 📁 Project Structure

```
DurinsGate/
├── app.py                      # Main Flask application
├── config.py                   # Configuration settings
├── init_db.py                  # Database initialization script
├── requirements.txt            # Python dependencies
├── .env.example               # Environment variable template
├── .gitignore                 # Git ignore rules
│
├── models/                     # Database models
│   ├── __init__.py
│   ├── user.py                # User model
│   ├── file.py                # File model
│   ├── file_assignment.py     # File-user assignments
│   ├── download_log.py        # Download audit logs
│   └── login_attempt.py       # Login attempt tracking
│
├── auth/                       # Authentication blueprint
│   ├── __init__.py
│   ├── routes.py              # Auth routes (login, logout, etc.)
│   ├── forms.py               # Auth forms
│   └── utils.py               # Auth utilities
│
├── admin/                      # Admin blueprint
│   ├── __init__.py
│   ├── routes.py              # Admin routes
│   ├── forms.py               # Admin forms
│   └── decorators.py          # Admin decorators
│
├── customer/                   # Customer blueprint
│   ├── __init__.py
│   ├── routes.py              # Customer routes
│   └── forms.py               # Customer forms
│
├── utils/                      # Utility modules
│   ├── file_handler.py        # File upload/download utilities
│   └── email_service.py       # Email notification service
│
├── templates/                  # HTML templates
│   ├── base.html              # Base template
│   ├── auth/                  # Auth templates
│   ├── admin/                 # Admin templates
│   ├── customer/              # Customer templates
│   └── emails/                # Email templates
│
├── static/                     # Static files
│   ├── css/
│   │   └── style.css          # Custom styles
│   └── js/
│       └── main.js            # Custom JavaScript
│
└── uploads/                    # File storage (created automatically)
```

## 🔧 Configuration

### Email Configuration

For email notifications to work, configure your SMTP settings in `.env`:

**Gmail Example:**
```env
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password  # Use App Password, not regular password
```

**SendGrid Example:**
```env
MAIL_SERVER=smtp.sendgrid.net
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=apikey
MAIL_PASSWORD=your-sendgrid-api-key
```

### reCAPTCHA (Optional)

To enable CAPTCHA on login:

1. Get keys from https://www.google.com/recaptcha/admin
2. Add to `.env`:
```env
RECAPTCHA_SITE_KEY=your-site-key
RECAPTCHA_SECRET_KEY=your-secret-key
```

### File Upload Settings

Configure in `.env`:
```env
MAX_FILE_SIZE_MB=500
ALLOWED_EXTENSIONS=pdf,zip,docx,doc,xlsx,xls,dwg,dxf,step,stp,iges,igs
```

## 📖 User Guides

### Admin User Guide

#### Creating a Customer Account

1. Log in as admin
2. Navigate to **Customers** → **Create Customer**
3. Fill in customer details
4. Click **Create Customer**
5. Customer receives activation email

#### Uploading Files

1. Navigate to **Files** → **Upload File**
2. Select file and fill in metadata
3. Click **Upload File**

#### Assigning Files to Customers

**Single Assignment:**
1. Navigate to **Assignments** → **Create Assignment**
2. Select customer and file
3. Optionally set expiration date
4. Click **Assign File**

**Bulk Assignment:**
1. Navigate to **Assignments** → **Bulk Assignment**
2. Select file and multiple customers
3. Choose whether to send notifications
4. Click **Assign to Selected Customers**

#### Monitoring Activity

- **Download Activity:** Navigate to **Activity**
- **Login Attempts:** Navigate to **Audit**
- **Dashboard:** View statistics and recent activity

### Customer User Guide

#### First Login

1. Receive activation email
2. Click activation link
3. Set your password (minimum 12 characters, mixed case, numbers, symbols)
4. Log in with username and password
5. Accept Terms of Service

#### Downloading Files

1. Navigate to **My Files**
2. Use search/filter to find files
3. Click **Download** button
4. File download begins automatically

#### Viewing Download History

1. Navigate to **History**
2. View all your past downloads

#### Setting Up MFA

1. Click your username → **MFA Settings**
2. Scan QR code with authenticator app
3. Enter verification code
4. MFA is now enabled

## 🔒 Security Best Practices

### For Production Deployment

1. **Change Default Passwords**
   - Update admin password immediately
   - Remove or update sample customer accounts

2. **Use Strong Secret Key**
   ```python
   python -c "import secrets; print(secrets.token_hex(32))"
   ```

3. **Enable HTTPS**
   - Use SSL/TLS certificates
   - Configure reverse proxy (nginx/Apache)

4. **Configure Firewall**
   - Only expose necessary ports
   - Use fail2ban for brute force protection

5. **Database**
   - Use PostgreSQL in production
   - Regular backups
   - Secure database credentials

6. **Email**
   - Use dedicated email service (SendGrid, AWS SES)
   - Configure SPF/DKIM records

7. **File Storage**
   - Consider S3 or similar for production
   - Implement file encryption at rest

8. **Monitoring**
   - Set up logging (Sentry, CloudWatch)
   - Monitor failed login attempts
   - Regular security audits

## 🐛 Troubleshooting

### Database Issues

**Error: "No such table"**
```bash
python init_db.py
```

### Email Not Sending

1. Check SMTP credentials in `.env`
2. For Gmail, use App Password (not regular password)
3. Check firewall allows outbound SMTP

### File Upload Fails

1. Check `UPLOAD_FOLDER` permissions
2. Verify file size under `MAX_FILE_SIZE_MB`
3. Check file extension in `ALLOWED_EXTENSIONS`

### Session Timeout Not Working

1. Ensure JavaScript is enabled
2. Check browser console for errors
3. Verify `SESSION_TIMEOUT_MINUTES` in config

## 🔄 Database Migrations

To make database schema changes:

```bash
# Initialize migrations (first time only)
flask db init

# Create migration
flask db migrate -m "Description of changes"

# Apply migration
flask db upgrade
```

## 📊 API Documentation

While this is primarily a web application, key endpoints:

### Authentication
- `POST /auth/login` - User login
- `GET /auth/logout` - User logout
- `POST /auth/forgot-password` - Request password reset
- `POST /auth/reset-password/<token>` - Reset password

### Customer
- `GET /customer/dashboard` - Customer dashboard
- `GET /customer/files` - List available files
- `GET /customer/download/<file_id>` - Generate download token
- `GET /customer/secure-download/<token>` - Download file with token

### Admin
- `GET /admin/dashboard` - Admin dashboard
- `GET /admin/customers` - List customers
- `POST /admin/customers/create` - Create customer
- `POST /admin/files/upload` - Upload file
- `POST /admin/assignments/create` - Assign file


## 📝 License

Proprietary - DurinsGate

## 🎉 Next Steps

### Phase 2 Features (Future Enhancements)

- [ ] Bulk file download (zip multiple files)
- [ ] File preview before download
- [ ] Comments/notes section for files
- [ ] Support ticket system
- [ ] API access for enterprise customers
- [ ] Single Sign-On (SSO) integration
- [ ] Mobile app version
- [ ] File encryption at rest
- [ ] Geographic download restrictions
- [ ] FedRAMP compliance features
- [ ] ITAR compliance features

---

**Built with Flask, Bootstrap 5, and Security Best Practices**
