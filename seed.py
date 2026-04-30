from datetime import date, timedelta
from werkzeug.security import generate_password_hash

from app import create_app
from models import db, User, Savings, Loan, Attendance

app = create_app()

with app.app_context():
    db.drop_all()
    db.create_all()

    admin = User(
    full_name="Admin User",
    email="admin@gmail.com",
    phone="9999999999",
    password_hash=generate_password_hash("admin123"),
    role="ADMIN",
    address="Chennai",
)

    user = User(
        full_name="Test Member",
        email="user@gmail.com",
        phone="8888888888",
        password_hash=generate_password_hash("user123"),
        role="USER",
        address="Chennai"
    )
    db.session.add_all([admin, user])
    db.session.commit()

    for i in range(4):
        s = Savings(
            user_id=user.id,
            month=f"2026-{i+1:02d}",
            amount=1000 + i * 200,
            payment_date=date(2026, i + 1, 5),
        )
        db.session.add(s)

    loan1 = Loan(
        user_id=user.id,
        loan_amount=5000,
        interest_rate=12,
        issue_date=date.today() - timedelta(days=60),
        due_date=date.today() + timedelta(days=2),
        status="Approved",
    )
    loan2 = Loan(
        user_id=user.id,
        loan_amount=3000,
        interest_rate=15,
        issue_date=date.today() - timedelta(days=200),
        due_date=date.today() - timedelta(days=10),
        status="Paid",
    )
    db.session.add_all([loan1, loan2])

    for i in range(10):
        a = Attendance(
            user_id=user.id,
            meeting_date=date.today() - timedelta(days=i * 7),
            present=True if i != 3 else False,
        )
        db.session.add(a)

    db.session.commit()
    print("Seed data created.")
