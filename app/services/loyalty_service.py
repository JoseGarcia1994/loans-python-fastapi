from datetime import date


def calculate_payment_points(payment):

    today = date.today()

    days_difference = (
        today - payment.payment_date
    ).days

    if days_difference < 0:

        return 15

    if days_difference == 0:

        return 10

    if 1 <= days_difference <= 7:

        return -10

    if 8 <= days_difference <= 14:

        return -20

    return -40


def apply_points(
    client,
    points,
):

    client.loyalty_points = max(
        0,
        client.loyalty_points + points
    )

    return client.loyalty_points


def update_late_streak(
    client,
    points,
):

    if points >= 0:

        client.consecutive_late_payments = 0

    else:

        client.consecutive_late_payments += 1

    if client.consecutive_late_payments >= 3:

        client.loyalty_points = 0

        client.consecutive_late_payments = 0

        return True

    return False