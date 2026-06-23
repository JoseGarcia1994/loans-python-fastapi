# 📦 Standard library
from datetime import timedelta, date

# 🌐 Third-party

# 📁 Local imports

def generate_payment_schedule(start_date, weeks=14):
    # Find Nex Monday
    days_ahead = 0 - start_date.weekday() + 7
    first_monday = start_date + timedelta(days=days_ahead)

    dates = []

    for i in range(weeks):
        payment_date = first_monday + timedelta(weeks=i)
        dates.append(payment_date)

    return dates

def get_monday(input_date: date) -> date:
    return input_date - timedelta(days=input_date.weekday())