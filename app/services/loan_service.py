# 📦 Standard library
from datetime import timedelta, date, datetime


# 🌐 Third-party

# 📁 Local imports

def generate_payment_schedule(start_date, weeks=14):

    dates = []

    for i in range(weeks):
        dates.append(
            start_date + timedelta(weeks=i + 1)
        )

    return dates

def get_monday(input_date: date) -> date:
    return input_date - timedelta(days=input_date.weekday())

def check_loan_completed(loan):
    return all(payment.paid for payment in loan.payments)

def close_loan_if_completed(loan, db):

    if not check_loan_completed(loan):
        return

    loan.is_completed = True
    loan.completed_at = datetime.now()
    loan.status = "completed"

    db.commit()