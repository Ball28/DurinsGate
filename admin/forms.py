"""Admin forms"""
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired, FileAllowed
from wtforms import StringField, TextAreaField, SelectField, BooleanField, SubmitField, SelectMultipleField
from wtforms.validators import DataRequired, Email, Length, Optional
from wtforms.fields import DateTimeLocalField


class CustomerCreateForm(FlaskForm):
    """Form for creating a new customer account"""
    username = StringField('Username', validators=[
        DataRequired(message='Username is required'),
        Length(min=3, max=80, message='Username must be between 3 and 80 characters')
    ])
    email = StringField('Email', validators=[
        DataRequired(message='Email is required'),
        Email(message='Invalid email address')
    ])
    company_name = StringField('Company Name', validators=[
        DataRequired(message='Company name is required'),
        Length(max=200)
    ])
    contact_info = TextAreaField('Contact Information', validators=[Optional()])
    is_active = BooleanField('Active Account', default=True)
    submit = SubmitField('Create Customer')


class CustomerEditForm(FlaskForm):
    """Form for editing customer account"""
    email = StringField('Email', validators=[
        DataRequired(message='Email is required'),
        Email(message='Invalid email address')
    ])
    company_name = StringField('Company Name', validators=[
        DataRequired(message='Company name is required'),
        Length(max=200)
    ])
    contact_info = TextAreaField('Contact Information', validators=[Optional()])
    is_active = BooleanField('Active Account')
    submit = SubmitField('Update Customer')


class FileUploadForm(FlaskForm):
    """Form for uploading files"""
    file = FileField('File', validators=[
        FileRequired(message='Please select a file'),
        FileAllowed(['pdf', 'zip', 'docx', 'doc', 'xlsx', 'xls', 'dwg', 'dxf', 'step', 'stp', 'iges', 'igs'], 
                   'Invalid file type')
    ])
    original_filename = StringField('Display Name (optional)', validators=[Optional()])
    category = StringField('Category', validators=[
        DataRequired(message='Category is required'),
        Length(max=100)
    ])
    product_type = StringField('Product Type', validators=[Optional(), Length(max=100)])
    version = StringField('Version', validators=[Optional(), Length(max=50)])
    description = TextAreaField('Description', validators=[Optional()])
    submit = SubmitField('Upload File')


class FileEditForm(FlaskForm):
    """Form for editing file metadata"""
    original_filename = StringField('Display Name', validators=[
        DataRequired(message='Display name is required'),
        Length(max=255)
    ])
    category = StringField('Category', validators=[
        DataRequired(message='Category is required'),
        Length(max=100)
    ])
    product_type = StringField('Product Type', validators=[Optional(), Length(max=100)])
    version = StringField('Version', validators=[Optional(), Length(max=50)])
    description = TextAreaField('Description', validators=[Optional()])
    is_active = BooleanField('Active')
    submit = SubmitField('Update File')


class FileAssignmentForm(FlaskForm):
    """Form for assigning files to customers"""
    customer_id = SelectField('Customer', coerce=int, validators=[
        DataRequired(message='Please select a customer')
    ])
    file_id = SelectField('File', coerce=int, validators=[
        DataRequired(message='Please select a file')
    ])
    expiration_date = DateTimeLocalField('Expiration Date (optional)', 
                                        format='%Y-%m-%dT%H:%M',
                                        validators=[Optional()])
    submit = SubmitField('Assign File')


class BulkAssignmentForm(FlaskForm):
    """Form for bulk file assignments"""
    file_id = SelectField('File', coerce=int, validators=[
        DataRequired(message='Please select a file')
    ])
    customer_ids = SelectMultipleField('Customers', coerce=int, validators=[
        DataRequired(message='Please select at least one customer')
    ])
    expiration_date = DateTimeLocalField('Expiration Date (optional)', 
                                        format='%Y-%m-%dT%H:%M',
                                        validators=[Optional()])
    send_notification = BooleanField('Send Email Notification', default=True)
    submit = SubmitField('Assign to Selected Customers')
