from datetime import date

from flask_login import UserMixin
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class User(UserMixin, db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    phone = db.Column(db.String(20))
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), default="USER", nullable=False)

    aadhaar_number = db.Column(db.String(12))
    pan_number = db.Column(db.String(10))
    address = db.Column(db.String(255))
    bank_account_number = db.Column(db.String(32))
    ifsc_code = db.Column(db.String(20))
    gender = db.Column(db.String(20))        
    age = db.Column(db.Integer)              

    join_date = db.Column(db.Date, default=date.today)
    join_date = db.Column(db.Date, default=date.today)
    email_verified = db.Column(db.Boolean, default=False) 

    savings = db.relationship("Savings", backref="user", lazy="dynamic")
    loans = db.relationship("Loan", backref="user", lazy="dynamic")
    attendance_records = db.relationship("Attendance", backref="user", lazy="dynamic")

    def is_admin(self):
        return self.role.upper() == "ADMIN"

    def get_credit_score_components(self):
        today = date.today()

        # Savings regularity in last 6 months
        last_6_months = {((today.year if today.month - i > 0 else today.year - 1),
                          ((today.month - i - 1) % 12) + 1)
                         for i in range(6)}
        months_with_saving = set(
            (s.payment_date.year, s.payment_date.month) for s in self.savings
        )
        savings_regularity = (
            len(last_6_months & months_with_saving) / len(last_6_months)
            if last_6_months else 0.0
        )

        # Loan repayment rate
        total_loans = self.loans.count()
        paid_loans = self.loans.filter_by(status="Paid").count()
        loan_repayment_rate = (paid_loans / total_loans) if total_loans > 0 else 0.0

        # Attendance: last 10 meetings
        last_10 = (
            self.attendance_records.order_by(Attendance.meeting_date.desc())
            .limit(10)
            .all()
        )
        if last_10:
            present_count = sum(1 for a in last_10 if a.present)
            attendance_rate = present_count / len(last_10)
        else:
            attendance_rate = 0.0

        return savings_regularity, loan_repayment_rate, attendance_rate

    def credit_score(self):
        s_reg, loan_rep, att = self.get_credit_score_components()
        score = s_reg * 40 + loan_rep * 40 + att * 20
        return round(score, 2)

    def credit_score_color(self):
        score = self.credit_score()
        if score >= 80:
            return "bg-success"
        if score >= 60:
            return "bg-warning"
        return "bg-danger"
    
    def set_password(self, password):
        from werkzeug.security import generate_password_hash
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        from werkzeug.security import check_password_hash
        return check_password_hash(self.password_hash, password)


class Savings(db.Model):
    __tablename__ = "savings"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    month = db.Column(db.String(20), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    payment_date = db.Column(db.Date, default=date.today, nullable=False)


class Loan(db.Model):
    __tablename__ = "loans"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    loan_amount = db.Column(db.Float, nullable=False)
    interest_rate = db.Column(db.Float, nullable=False)
    issue_date = db.Column(db.Date, default=date.today, nullable=False)
    due_date = db.Column(db.Date, nullable=False)
    status = db.Column(db.String(20), default="Pending", nullable=False)

    def is_due_soon(self, days=3):
        return self.status in {"Pending", "Approved"} and (
            (self.due_date - date.today()).days <= days
        )


class Attendance(db.Model):
    __tablename__ = "attendance"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    meeting_date = db.Column(db.Date, default=date.today, nullable=False)
    present = db.Column(db.Boolean, default=True, nullable=False)


def calculate_admin_analytics():
    total_savings = db.session.query(db.func.sum(Savings.amount)).scalar() or 0
    total_loans = db.session.query(db.func.sum(Loan.loan_amount)).scalar() or 0

    total_loans_count = Loan.query.count()
    paid_loans = Loan.query.filter_by(status="Paid").count()
    repayment_rate = (paid_loans / total_loans_count * 100) if total_loans_count else 0.0

    users = User.query.all()
    scores = [u.credit_score() for u in users] if users else []
    avg_score = sum(scores) / len(scores) if scores else 0.0

    return {
        "total_savings": round(total_savings, 2),
        "total_loans": round(total_loans, 2),
        "repayment_rate": round(repayment_rate, 2),
        "avg_score": round(avg_score, 2),
    }
