"""Customer forms"""
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Email, Optional


class ProfileUpdateForm(FlaskForm):
    """Form for updating customer profile"""
    email = StringField('Email', validators=[
        DataRequired(message='Email is required'),
        Email(message='Invalid email address')
    ])
    company_name = StringField('Company Name', validators=[
        DataRequired(message='Company name is required')
    ])
    contact_info = TextAreaField('Contact Information', validators=[Optional()])
    submit = SubmitField('Update Profile')


class TermsAcceptanceForm(FlaskForm):
    """Form for accepting terms of service"""
    accept_terms = BooleanField('I accept the Terms of Service and Privacy Policy', validators=[
        DataRequired(message='You must accept the terms to continue')
    ])
    submit = SubmitField('Accept and Continue')
