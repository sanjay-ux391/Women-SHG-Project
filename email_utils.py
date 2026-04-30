"""
email_utils.py - Email utilities for OTP verification and reminders
"""

import smtplib
import random
import string
from datetime import datetime, timedelta
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from flask import render_template_string

# Email Configuration
EMAIL_CONFIG = {
    'sender_email': 'sarav.bala2005@gmail.com',  # CHANGE THIS
    'sender_password': 'xcsm cnbu imhi dmgm',   # CHANGE THIS (Gmail App Password)
    'smtp_server': 'smtp.gmail.com',
    'smtp_port': 587
}

def send_email(to_email, subject, html_content):
    """Send email using SMTP"""
    try:
        msg = MIMEMultipart('alternative')
        msg['Subject'] = subject
        msg['From'] = EMAIL_CONFIG['sender_email']
        msg['To'] = to_email
        
        # Attach HTML content
        part = MIMEText(html_content, 'html')
        msg.attach(part)
        
        # Send email
        with smtplib.SMTP(EMAIL_CONFIG['smtp_server'], EMAIL_CONFIG['smtp_port']) as server:
            server.starttls()
            server.login(EMAIL_CONFIG['sender_email'], EMAIL_CONFIG['sender_password'])
            server.sendmail(EMAIL_CONFIG['sender_email'], to_email, msg.as_string())
        
        return True
    except Exception as e:
        print(f"Error sending email: {e}")
        return False


def generate_otp(length=6):
    """Generate random OTP"""
    return ''.join(random.choices(string.digits, k=length))


def send_otp_email(to_email, otp):
    """Send OTP via email"""
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; background-color: #f4f4f4; }}
            .container {{ max-width: 500px; margin: 50px auto; background-color: white; padding: 30px; border-radius: 10px; box-shadow: 0 0 10px rgba(0,0,0,0.1); }}
            .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px; border-radius: 5px; text-align: center; }}
            .content {{ padding: 20px; text-align: center; }}
            .otp-box {{ background-color: #f9fafb; padding: 20px; margin: 20px 0; border-radius: 5px; border: 2px solid #667eea; }}
            .otp-code {{ font-size: 32px; font-weight: bold; color: #667eea; letter-spacing: 5px; }}
            .footer {{ color: #666; font-size: 12px; text-align: center; margin-top: 20px; }}
            .warning {{ color: #f59e0b; font-weight: bold; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h2>Women GateWay</h2>
            </div>
            <div class="content">
                <h3>Email Verification</h3>
                <p>Your One-Time Password (OTP) for email verification is:</p>
                <div class="otp-box">
                    <div class="otp-code">{otp}</div>
                </div>
                <p>This OTP will expire in <span class="warning">10 minutes</span>.</p>
                <p>Do not share this OTP with anyone.</p>
            </div>
            <div class="footer">
                <p>© 2024 Women GateWay. All rights reserved.</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    return send_email(to_email, "Your Email Verification OTP - Women GateWay", html_content)


def send_loan_reminder_email(user_email, user_name, loan_amount, due_date, days_remaining):
    """Send loan repayment reminder email"""
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; background-color: #f4f4f4; }}
            .container {{ max-width: 600px; margin: 50px auto; background-color: white; padding: 30px; border-radius: 10px; box-shadow: 0 0 10px rgba(0,0,0,0.1); }}
            .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px; border-radius: 5px; text-align: center; }}
            .content {{ padding: 20px; }}
            .alert {{ background-color: #fef3c7; color: #92400e; padding: 15px; border-radius: 5px; border-left: 4px solid #f59e0b; margin: 20px 0; }}
            .loan-details {{ background-color: #f9fafb; padding: 20px; border-radius: 5px; margin: 20px 0; }}
            .detail-row {{ display: flex; justify-content: space-between; padding: 10px 0; border-bottom: 1px solid #e5e7eb; }}
            .label {{ font-weight: bold; color: #667eea; }}
            .value {{ color: #1f2937; }}
            .footer {{ color: #666; font-size: 12px; text-align: center; margin-top: 20px; }}
            .button {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 12px 30px; text-decoration: none; border-radius: 5px; display: inline-block; margin-top: 20px; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h2>Women GateWay</h2>
            </div>
            <div class="content">
                <h3>Loan Repayment Reminder</h3>
                <p>Dear {user_name},</p>
                
                <div class="alert">
                    <strong>⚠️ Your loan is due in {days_remaining} day(s)!</strong>
                </div>
                
                <p>We are writing to remind you about your upcoming loan repayment.</p>
                
                <div class="loan-details">
                    <div class="detail-row">
                        <span class="label">Loan Amount:</span>
                        <span class="value">₹{loan_amount:,.2f}</span>
                    </div>
                    <div class="detail-row">
                        <span class="label">Due Date:</span>
                        <span class="value">{due_date.strftime('%d-%b-%Y')}</span>
                    </div>
                    <div class="detail-row">
                        <span class="label">Days Remaining:</span>
                        <span class="value">{days_remaining} day(s)</span>
                    </div>
                </div>
                
                <p><strong>Please ensure timely repayment to maintain your credit score and eligibility for future loans.</strong></p>
                
                <p>If you have any questions or need assistance, please contact us immediately.</p>
                
                <p>
                    <a href="https://yourwebsite.com/user/finance" class="button">View Loan Details</a>
                </p>
            </div>
            <div class="footer">
                <p>© 2024 Women GateWay. All rights reserved.</p>
                <p>This is an automated email. Please do not reply to this email.</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    return send_email(user_email, f"Loan Repayment Reminder - {days_remaining} Days Remaining", html_content)


def send_welcome_email(user_email, user_name):
    """Send welcome email after registration"""
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; background-color: #f4f4f4; }}
            .container {{ max-width: 600px; margin: 50px auto; background-color: white; padding: 30px; border-radius: 10px; box-shadow: 0 0 10px rgba(0,0,0,0.1); }}
            .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px; border-radius: 5px; text-align: center; }}
            .content {{ padding: 20px; }}
            .features {{ background-color: #ecfdf5; padding: 20px; border-radius: 5px; margin: 20px 0; border-left: 4px solid #10b981; }}
            .footer {{ color: #666; font-size: 12px; text-align: center; margin-top: 20px; }}
            .button {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 12px 30px; text-decoration: none; border-radius: 5px; display: inline-block; margin-top: 20px; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h2>Welcome to Women GateWay! 🎉</h2>
            </div>
            <div class="content">
                <h3>Hello {user_name},</h3>
                
                <p>Thank you for joining Women GateWay. We're excited to have you as part of our community!</p>
                
                <div class="features">
                    <h4 style="color: #065f46; margin-top: 0;">Here's what you can do now:</h4>
                    <ul>
                        <li>📊 Track your savings and credit score</li>
                        <li>💳 Apply for loans with easy process</li>
                        <li>📈 Access government schemes for women</li>
                        <li>👥 Connect with your SHG community</li>
                        <li>🎓 Get financial guidance from our AI Assistant</li>
                    </ul>
                </div>
                
                <p>Start your financial journey today by exploring your dashboard!</p>
                
                <p>
                    <a href="https://yourwebsite.com/user/dashboard" class="button">Go to Dashboard</a>
                </p>
            </div>
            <div class="footer">
                <p>© 2024 Women GateWay. All rights reserved.</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    return send_email(user_email, "Welcome to Women GateWay!", html_content)


def send_profile_verification_email(user_email, user_name):
    """Send email asking to complete profile"""
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; background-color: #f4f4f4; }}
            .container {{ max-width: 600px; margin: 50px auto; background-color: white; padding: 30px; border-radius: 10px; box-shadow: 0 0 10px rgba(0,0,0,0.1); }}
            .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px; border-radius: 5px; text-align: center; }}
            .content {{ padding: 20px; }}
            .alert {{ background-color: #eff6ff; color: #0c4a6e; padding: 15px; border-radius: 5px; border-left: 4px solid #0ea5e9; margin: 20px 0; }}
            .footer {{ color: #666; font-size: 12px; text-align: center; margin-top: 20px; }}
            .button {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 12px 30px; text-decoration: none; border-radius: 5px; display: inline-block; margin-top: 20px; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h2>Complete Your Profile</h2>
            </div>
            <div class="content">
                <h3>Hi {user_name},</h3>
                
                <div class="alert">
                    <strong>ℹ️ Please complete your profile to unlock all features</strong>
                </div>
                
                <p>We need some additional information to verify your account and enable loan access.</p>
                
                <p><strong>Please add the following details:</strong></p>
                <ul>
                    <li>✓ Aadhaar Number</li>
                    <li>✓ PAN Card Number</li>
                    <li>✓ Bank Account Details</li>
                    <li>✓ Phone Number</li>
                </ul>
                
                <p>Once verified, you'll have access to loans and all other features.</p>
                
                <p>
                    <a href="https://yourwebsite.com/user/profile" class="button">Complete Profile Now</a>
                </p>
            </div>
            <div class="footer">
                <p>© 2024 Women GateWay. All rights reserved.</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    return send_email(user_email, "Complete Your Profile - Women GateWay", html_content)
