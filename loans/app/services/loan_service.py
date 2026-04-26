from datetime import timedelta


def generate_payment_schedule(start_date, weeks=14):
    # Find Nex Monday
    days_ahead = 0 - start_date.weekday() + 7
    first_monday = start_date + timedelta(days=days_ahead)

    dates = []

    for i in range(weeks):
        payment_date = first_monday + timedelta(weeks=i)
        dates.append(payment_date)

    return dates