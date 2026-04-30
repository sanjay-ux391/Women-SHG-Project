"""
forms.py - WTForms for authentication and user management
"""

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, DateField, IntegerField, TextAreaField, SelectField
from wtforms.validators import DataRequired, Email, EqualTo, ValidationError, Length, Regexp
from models import User


class LoginForm(FlaskForm):
    """Login form"""
    email = StringField('Email', validators=[
        DataRequired(message='Email is required'),
        Email(message='Invalid email address')
    ])
    password = PasswordField('Password', validators=[
        DataRequired(message='Password is required')
    ])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')


class RegistrationForm(FlaskForm):
    """Registration form with all required fields"""
    full_name = StringField('Full Name', validators=[
        DataRequired(message='Full name is required'),
        Length(min=3, max=120, message='Full name must be 3-120 characters')
    ])
    email = StringField('Email', validators=[
        DataRequired(message='Email is required'),
        Email(message='Invalid email address')
    ])
    phone = StringField('Phone Number', validators=[
        DataRequired(message='Phone number is required'),
        Length(min=10, max=20, message='Phone number must be 10-20 characters')
    ])
    aadhaar_number = StringField('Aadhaar Number', validators=[
        DataRequired(message='Aadhaar number is required'),
        Length(min=12, max=12, message='Aadhaar number must be 12 digits')
    ])
    pan_number = StringField('PAN Number', validators=[
        DataRequired(message='PAN number is required'),
        Length(min=10, max=10, message='PAN number must be 10 characters')
    ])
    bank_account_number = StringField('Bank Account Number', validators=[
        DataRequired(message='Bank account number is required'),
        Length(min=9, max=18, message='Bank account number must be 9-18 characters')
    ])
    ifsc_code = StringField('IFSC Code', validators=[
        DataRequired(message='IFSC code is required'),
        Length(min=11, max=11, message='IFSC code must be 11 characters')
    ])
    address = TextAreaField('Address', validators=[
        DataRequired(message='Address is required'),
        Length(min=10, max=255, message='Address must be 10-255 characters')
    ])
    password = PasswordField('Password', validators=[
        DataRequired(message='Password is required'),
        Length(min=6, message='Password must be at least 6 characters')
    ])
    password_confirm = PasswordField('Confirm Password', validators=[
        DataRequired(message='Please confirm password'),
        EqualTo('password', message='Passwords must match')
    ])
    submit = SubmitField('Register')

    def validate_email(self, email):
        """Check if email is already registered"""
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('Email already registered. Please login.')

    def validate_aadhaar_number(self, aadhaar_number):
        """Validate Aadhaar number is 12 digits"""
        if not aadhaar_number.data.isdigit():
            raise ValidationError('Aadhaar number must contain only digits')

    def validate_pan_number(self, pan_number):
        """Validate PAN number format"""
        import re
        pan_pattern = r'^[A-Z]{5}[0-9]{4}[A-Z]{1}$'
        if not re.match(pan_pattern, pan_number.data.upper()):
            raise ValidationError('PAN number format is invalid (e.g., AAAAA0000A)')


class SavingsForm(FlaskForm):
    """Form for recording savings"""
    month = StringField('Month', validators=[DataRequired()])
    amount = StringField('Amount (₹)', validators=[DataRequired()])
    payment_date = DateField('Payment Date', validators=[DataRequired()])
    submit = SubmitField('Record Saving')


class LoanApplyForm(FlaskForm):
    """Form for applying loan"""
    loan_amount = StringField('Loan Amount (₹)', validators=[DataRequired()])
    interest_rate = StringField('Interest Rate (%)', validators=[DataRequired()])
    issue_date = DateField('Issue Date', validators=[DataRequired()])
    due_date = DateField('Due Date', validators=[DataRequired()])
    submit = SubmitField('Apply for Loan')


class AttendanceForm(FlaskForm):
    """Form for recording meeting attendance"""
    meeting_date = DateField('Meeting Date', validators=[DataRequired()])
    present = BooleanField('Present')
    submit = SubmitField('Record Attendance')


class ApproveLoanForm(FlaskForm):
    """Form for approving loans (Admin)"""
    status = SelectField('Loan Status', choices=[
        ('Pending', 'Pending'),
        ('Approved', 'Approved'),
        ('Rejected', 'Rejected'),
        ('Paid', 'Paid')
    ], validators=[DataRequired()])
    submit = SubmitField('Update Loan Status')


class SimpleSearchForm(FlaskForm):
    """Simple search form for admin"""
    search = StringField('Search', validators=[DataRequired()])
    submit = SubmitField('Search')
