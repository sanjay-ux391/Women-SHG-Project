from datetime import date

from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user

from models import db, Savings, Loan, Attendance
from forms import SavingsForm, LoanApplyForm, AttendanceForm

user_bp = Blueprint("user", __name__, url_prefix="/user")


@user_bp.route("/dashboard")
@login_required
def user_dashboard():
    score = current_user.credit_score()
    color_class = current_user.credit_score_color()

    total_savings = (
        db.session.query(db.func.sum(Savings.amount))
        .filter_by(user_id=current_user.id)
        .scalar()
        or 0
    )

    active_loans = Loan.query.filter(
        Loan.user_id == current_user.id, Loan.status.in_(["Pending", "Approved"])
    ).all()

    upcoming_due = [l for l in active_loans if l.is_due_soon(days=3)]

    month_str = date.today().strftime("%Y-%m")
    has_saving_this_month = (
        Savings.query.filter(
            Savings.user_id == current_user.id,
            db.func.strftime("%Y-%m", Savings.payment_date) == month_str,
        ).count()
        > 0
    )

    return render_template(
        "user/dashboard.html",
        score=score,
        score_color=color_class,
        total_savings=round(total_savings, 2),
        active_loans=active_loans,
        upcoming_due=upcoming_due,
        has_saving_this_month=has_saving_this_month,
    )


@user_bp.route("/finance", methods=["GET", "POST"])
@login_required
def finance_dashboard():
    sform = SavingsForm(prefix="s")
    lform = LoanApplyForm(prefix="l")

    if sform.validate_on_submit() and sform.submit.data:
        s = Savings(
            user_id=current_user.id,
            month=sform.month.data,
            amount=sform.amount.data,
            payment_date=sform.payment_date.data,
        )
        db.session.add(s)
        db.session.commit()
        flash("Savings recorded.", "success")
        return redirect(url_for("user.finance_dashboard"))

    if lform.validate_on_submit() and lform.submit.data:
        loan = Loan(
            user_id=current_user.id,
            loan_amount=lform.loan_amount.data,
            interest_rate=lform.interest_rate.data,
            issue_date=lform.issue_date.data,
            due_date=lform.due_date.data,
            status="Pending",
        )
        db.session.add(loan)
        db.session.commit()
        flash("Loan application submitted.", "success")
        return redirect(url_for("user.finance_dashboard"))

    savings = (
        Savings.query.filter_by(user_id=current_user.id)
        .order_by(Savings.payment_date.desc())
        .all()
    )
    loans = (
        Loan.query.filter_by(user_id=current_user.id)
        .order_by(Loan.issue_date.desc())
        .all()
    )

    return render_template(
        "user/finance_dashboard.html",
        sform=sform,
        lform=lform,
        savings=savings,
        loans=loans,
    )


@user_bp.route("/grow")
@login_required
def grow_scheme():
    schemes = [
        {
            "name": "PM Women SHG Loan Scheme",
            "eligibility": "Member of registered SHG for at least 6 months, regular savings.",
            "benefit": "Low-interest loans up to ₹1,00,000.",
        },
        {
            "name": "Tamil Nadu Mahalir Thittam",
            "eligibility": "Women SHGs registered in Tamil Nadu.",
            "benefit": "Subsidized loans, training, and entrepreneurship support.",
        },
    ]
    score = current_user.credit_score()
    return render_template("user/grow_scheme.html", schemes=schemes, score=score)


@user_bp.route("/attendance", methods=["GET", "POST"])
@login_required
def attendee_meeting():
    form = AttendanceForm()
    if form.validate_on_submit():
        record = Attendance(
            user_id=current_user.id,
            meeting_date=form.meeting_date.data,
            present=form.present.data,
        )
        db.session.add(record)
        db.session.commit()
        flash("Attendance saved.", "success")
        return redirect(url_for("user.attendee_meeting"))

    records = (
        Attendance.query.filter_by(user_id=current_user.id)
        .order_by(Attendance.meeting_date.desc())
        .all()
    )
    return render_template("user/attendee_meeting.html", form=form, records=records)


@user_bp.route("/seal-data")
@login_required
def seal_data():
    savings = (
        Savings.query.filter_by(user_id=current_user.id)
        .order_by(Savings.payment_date.desc())
        .all()
    )
    loans = (
        Loan.query.filter_by(user_id=current_user.id)
        .order_by(Loan.issue_date.desc())
        .all()
    )
    return render_template("user/seal_data.html", savings=savings, loans=loans)


@user_bp.route("/pending-sealed")
@login_required
def pending_sealed():
    pending_loans = Loan.query.filter_by(user_id=current_user.id, status="Pending").all()
    return render_template("user/pending_sealed.html", loans=pending_loans)


@user_bp.route("/bot")
@login_required
def bot():
    return render_template("user/bot.html")


@user_bp.route("/bot/ask", methods=["POST"])
@login_required
def bot_ask():
    data = request.get_json() or {}
    question = (data.get("question") or "").lower()

    answer = "I am not sure. Please contact your SHG leader for more details."
    if "saving" in question:
        answer = (
            "Regular savings improve your credit score and loan eligibility. "
            "Try to deposit every month without skipping."
        )
    elif "loan" in question and "interest" in question:
        answer = "Loans typically have 12–18% annual interest. Higher credit scores may get lower rates."
    elif "loan" in question:
        answer = "You can apply for a loan from the Finance Dashboard. Admin will review and approve it."
    elif "scheme" in question or "government" in question:
        answer = "Check the Grow Scheme page to see eligible government schemes and benefits."
    elif "credit score" in question:
        answer = (
            "Your credit score is calculated from savings regularity (40%), "
            "loan repayment (40%), and meeting attendance (20%)."
        )
    elif "attendance" in question or "meeting" in question:
        answer = "Mark your attendance for every SHG meeting to keep your credit score healthy."

    return jsonify({"answer": answer})

@user_bp.route("/profile")
@login_required
def profile():
    return render_template("profile.html")


@user_bp.route("/update-profile", methods=["POST"])
@login_required
def update_profile():
    current_user.full_name = request.form.get("full_name", current_user.full_name)
    current_user.gender = request.form.get("gender", current_user.gender)
    current_user.age = request.form.get("age", current_user.age)
    current_user.address = request.form.get("address", current_user.address)
    current_user.phone = request.form.get("phone", current_user.phone)
    current_user.aadhaar_number = request.form.get("aadhaar_number", current_user.aadhaar_number)
    current_user.pan_number = request.form.get("pan_number", current_user.pan_number)
    current_user.bank_account_number = request.form.get("bank_account_number", current_user.bank_account_number)
    current_user.ifsc_code = request.form.get("ifsc_code", current_user.ifsc_code)
    
    db.session.commit()
    flash("Profile updated successfully!", "success")
    return redirect(url_for("user.profile"))    
