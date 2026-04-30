from datetime import datetime, timedelta
from models import db, User, Loan
from email_utils import send_loan_reminder_email

def send_loan_reminders():
    """
    Send reminder emails for loans due in 3 days
    """
    try:
        # Get today's date
        today = datetime.now().date()
        due_in_3_days = today + timedelta(days=3)
        
        # Find loans due in 3 days that are still pending/approved
        pending_loans = Loan.query.filter(
            Loan.due_date <= due_in_3_days,
            Loan.due_date > today,
            Loan.status.in_(["Pending", "Approved"])
        ).all()
        
        reminder_count = 0
        for loan in pending_loans:
            user = User.query.get(loan.user_id)
            if user:
                days_remaining = (loan.due_date - today).days
                
                # Send email
                if send_loan_reminder_email(
                    user.email,
                    user.full_name,
                    loan.loan_amount,
                    loan.due_date,
                    days_remaining
                ):
                    reminder_count += 1
                    print(f"Reminder sent to {user.email} for loan due in {days_remaining} days")
        
        print(f"Total reminders sent: {reminder_count}")
        return True
    except Exception as e:
        print(f"Error sending loan reminders: {e}")
        return False
