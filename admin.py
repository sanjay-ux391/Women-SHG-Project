from datetime import date, timedelta
from functools import wraps

from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user

from models import db, User, Loan, Savings, calculate_admin_analytics
from forms import ApproveLoanForm, SimpleSearchForm

admin_bp = Blueprint("admin", __name__, url_prefix="/admin")


def admin_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin():
            flash("Admin access required.", "danger")
            return redirect(url_for("auth.login"))
        return func(*args, **kwargs)

    return wrapper


@admin_bp.route("/dashboard")
@login_required
@admin_required
def admin_dashboard():
    stats = calculate_admin_analytics()
    total_users = User.query.count()
    pending_loans = Loan.query.filter_by(status="Pending").count()
    flagged_accounts = 0

    upcoming_due_loans = Loan.query.filter(
        Loan.due_date <= (date.today() + timedelta(days=3)),
        Loan.status.in_(["Pending", "Approved"]),
    ).all()

    month_str = date.today().strftime("%Y-%m")
    users_no_savings = []
    for u in User.query.all():
        has_saving = (
            u.savings.filter(
                db.func.strftime("%Y-%m", Savings.payment_date) == month_str
            ).count()
            > 0
        )
        if not has_saving:
            users_no_savings.append(u)

    return render_template(
        "admin/dashboard.html",
        total_users=total_users,
        pending_approvals=pending_loans,
        total_income=stats["total_savings"],
        flagged_accounts=flagged_accounts,
        analytics=stats,
        upcoming_due_loans=upcoming_due_loans,
        users_no_savings=users_no_savings,
    )


@admin_bp.route("/subadmin")
@login_required
@admin_required
def subadmin_list():
    form = SimpleSearchForm(request.args)
    query = User.query.filter_by(role="USER")
    if form.query.data:
        like = f"%{form.query.data}%"
        query = query.filter(User.full_name.ilike(like))
    users = query.order_by(User.full_name).all()
    return render_template("admin/subadmin.html", users=users, form=form)


@admin_bp.route("/loans", methods=["GET", "POST"])
@login_required
@admin_required
def durable_payments():
    loans = Loan.query.order_by(Loan.due_date.desc()).all()
    return render_template("admin/durable_payments.html", loans=loans)


@admin_bp.route("/loans/<int:loan_id>/update", methods=["GET", "POST"])
@login_required
@admin_required
def update_loan(loan_id):
    loan = Loan.query.get_or_404(loan_id)
    form = ApproveLoanForm(status=loan.status)
    if form.validate_on_submit():
        loan.status = form.status.data
        db.session.commit()
        flash("Loan status updated.", "success")
        return redirect(url_for("admin.durable_payments"))
    return render_template("admin/meeting_approve.html", loan=loan, form=form)


@admin_bp.route("/analytics.json")
@login_required
@admin_required
def analytics_json():
    stats = calculate_admin_analytics()
    labels = ["Total Savings", "Total Loans"]
    data = [stats["total_savings"], stats["total_loans"]]
    repayment_rate = stats["repayment_rate"]
    avg_score = stats["avg_score"]
    return jsonify(
        {
            "bar": {"labels": labels, "data": data},
            "pie": {
                "labels": ["Repaid %", "Pending %"],
                "data": [repayment_rate, 100 - repayment_rate],
            },
            "avg_score": avg_score,
        }
    )
