"""
auth.py - Authentication routes with OTP verification
FIXED VERSION - Correct template paths
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from flask_login import login_user, logout_user, login_required, current_user
from datetime import datetime, timedelta
from models import db, User
from forms import LoginForm, RegistrationForm
from email_utils import send_otp_email, generate_otp, send_welcome_email

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    """Login route - existing code"""
    if current_user.is_authenticated:
        return redirect(url_for("user.user_dashboard"))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        
        # Check if user exists and password is correct
        if user is None or not user.check_password(form.password.data):
            flash("Invalid email or password", "danger")
            return redirect(url_for("auth.login"))
        
        # Check if email is verified
        if not getattr(user, 'email_verified', False):
            flash("Please verify your email first", "warning")
            session['pending_user_email'] = user.email
            return redirect(url_for("auth.verify_email"))
        
        # Login user
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get("next")
        return redirect(next_page) if next_page else redirect(url_for("user.user_dashboard"))
    
    return render_template("login.html", form=form)


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    """Register route with OTP"""
    if current_user.is_authenticated:
        return redirect(url_for("user.user_dashboard"))
    
    form = RegistrationForm()
    if form.validate_on_submit():
        # Check if email already exists
        if User.query.filter_by(email=form.email.data).first():
            flash("Email already registered. Please login.", "danger")
            return redirect(url_for("auth.login"))
        
        try:
            # Create new user
            user = User(
                full_name=form.full_name.data,
                email=form.email.data,
                phone=form.phone.data if hasattr(form, 'phone') else None,
                aadhaar_number=form.aadhaar_number.data if hasattr(form, 'aadhaar_number') else None,
                pan_number=form.pan_number.data if hasattr(form, 'pan_number') else None,
                bank_account_number=form.bank_account_number.data if hasattr(form, 'bank_account_number') else None,
                ifsc_code=form.ifsc_code.data if hasattr(form, 'ifsc_code') else None,
                address=form.address.data if hasattr(form, 'address') else None,
                email_verified=False  # Not verified until OTP is entered
            )
            
            # Set password using the method
            user.set_password(form.password.data)
            
            db.session.add(user)
            db.session.commit()
            
            # Generate OTP
            otp = generate_otp()
            session['otp'] = otp
            session['otp_time'] = datetime.now().isoformat()
            session['pending_user_email'] = user.email
            
            # Send OTP email
            if send_otp_email(user.email, otp):
                flash("Registration successful! Check your email for OTP.", "success")
                return redirect(url_for("auth.verify_email"))
            else:
                # Even if email fails, redirect to verify page
                flash("Account created! Please check your email for OTP.", "info")
                return redirect(url_for("auth.verify_email"))
        
        except Exception as e:
            db.session.rollback()
            flash(f"Error during registration: {str(e)}", "danger")
            return redirect(url_for("auth.register"))
    
    return render_template("register.html", form=form)


@auth_bp.route("/verify-email", methods=["GET", "POST"])
def verify_email():
    """Verify email with OTP"""
    if not session.get('pending_user_email'):
        flash("No pending email verification. Please register first.", "danger")
        return redirect(url_for("auth.register"))
    
    pending_email = session.get('pending_user_email')
    
    if request.method == "POST":
        entered_otp = request.form.get("otp", "").strip()
        
        # Check if OTP exists in session
        if not session.get('otp'):
            flash("OTP not found. Please register again.", "danger")
            session.clear()
            return redirect(url_for("auth.register"))
        
        try:
            # Check OTP expiry (10 minutes)
            otp_time_str = session.get('otp_time')
            if otp_time_str:
                otp_time = datetime.fromisoformat(otp_time_str)
                if datetime.now() - otp_time > timedelta(minutes=10):
                    flash("OTP expired. Please request a new one.", "danger")
                    session.pop('otp', None)
                    session.pop('otp_time', None)
                    return redirect(url_for("auth.resend_otp"))
        except Exception as e:
            print(f"Error checking OTP time: {e}")
        
        # Verify OTP matches
        if entered_otp == session.get('otp'):
            # Mark user as verified
            user = User.query.filter_by(email=pending_email).first()
            if user:
                user.email_verified = True
                db.session.commit()
                
                # Send welcome email
                try:
                    send_welcome_email(user.email, user.full_name)
                except Exception as e:
                    print(f"Error sending welcome email: {e}")
                
                # Clear session
                session.pop('otp', None)
                session.pop('otp_time', None)
                session.pop('pending_user_email', None)
                
                flash("Email verified successfully! Please login.", "success")
                return redirect(url_for("auth.login"))
            else:
                flash("User not found. Please register again.", "danger")
                return redirect(url_for("auth.register"))
        else:
            flash("Invalid OTP. Please try again.", "danger")
    
    # FIXED: Use correct template path
    return render_template("auth/verify_email.html", email=pending_email)


@auth_bp.route("/resend-otp", methods=["GET", "POST"])
def resend_otp():
    """Resend OTP to email"""
    if not session.get('pending_user_email'):
        flash("No pending email verification. Please register first.", "danger")
        return redirect(url_for("auth.register"))
    
    pending_email = session.get('pending_user_email')
    
    if request.method == "POST":
        try:
            # Generate new OTP
            otp = generate_otp()
            session['otp'] = otp
            session['otp_time'] = datetime.now().isoformat()
            
            if send_otp_email(pending_email, otp):
                flash("New OTP sent to your email!", "success")
                return redirect(url_for("auth.verify_email"))
            else:
                flash("Failed to send OTP. Please check your email connection.", "danger")
        except Exception as e:
            flash(f"Error: {str(e)}", "danger")
    
    # FIXED: Use correct template path
    return render_template("auth/resend_otp.html", email=pending_email)


@auth_bp.route("/logout")
@login_required
def logout():
    """Logout user"""
    logout_user()
    flash("You have been logged out successfully", "info")
    return redirect(url_for("auth.login"))
