# 📦 Standard library
from datetime import date

# ─── Constants ────────────────────────────────────────────────────────────────

EARLY_PAYMENT_RATE    = 0.0015   # paid before due date
ON_TIME_PAYMENT_RATE  = 0.0010   # paid on due date
LATE_1_7_RATE         = 0.0010   # 1-7 days late  (penalty)
LATE_8_14_RATE        = 0.0020   # 8-14 days late (penalty)
LATE_15_PLUS_RATE     = 0.0040   # 15+ days late  (penalty)

LIQUIDATION_EARLY_RATE  = 0.0050  # liquidate at week 9 or earlier
LIQUIDATION_LATE_RATE   = 0.0030  # liquidate at week 10-13

RENEWAL_RATE            = 0.0030  # renewal bonus

POINTS_TO_PESOS         = 0.50   # 1 point = $0.50 MXN
LATE_STREAK_LIMIT       = 3      # consecutive late payments before reset


# ─── Payment Points ───────────────────────────────────────────────────────────

def calculate_payment_points(payment) -> int:
    """
    Calculate points earned or lost based on how early/late the payment was made.
    Points scale with the loan amount so larger loans earn/lose more.
    """
    today = date.today()
    days_difference = (today - payment.payment_date).days
    loan_amount = payment.loan.amount

    if days_difference < 0:
        # Paid before due date
        return max(1, int(loan_amount * EARLY_PAYMENT_RATE))

    if days_difference == 0:
        # Paid on due date
        return max(1, int(loan_amount * ON_TIME_PAYMENT_RATE))

    if 1 <= days_difference <= 7:
        return -max(1, int(loan_amount * LATE_1_7_RATE))

    if 8 <= days_difference <= 14:
        return -max(1, int(loan_amount * LATE_8_14_RATE))

    return -max(1, int(loan_amount * LATE_15_PLUS_RATE))


# ─── Liquidation Points ───────────────────────────────────────────────────────

def calculate_liquidation_points(remaining_payments: int, loan_amount: int) -> int:
    """
    Bonus points awarded when a client pays off their loan early.
    remaining_payments: number of payments settled in bulk.
    Bonus scales with loan amount.
    """
    if remaining_payments >= 6:
        # Liquidated at week 9 or earlier
        return max(1, int(loan_amount * LIQUIDATION_EARLY_RATE))

    if remaining_payments >= 1:
        # Liquidated at week 10-13
        return max(1, int(loan_amount * LIQUIDATION_LATE_RATE))

    return 0


# ─── Renewal Points ───────────────────────────────────────────────────────────

def calculate_renewal_points(loan_amount: int) -> int:
    """
    Bonus points awarded when a client renews their loan.
    Scales with the new loan amount.
    """
    return max(1, int(loan_amount * RENEWAL_RATE))


# ─── Apply Points ─────────────────────────────────────────────────────────────

def apply_points(client, points: int) -> int:
    """
    Apply points to client, ensuring total never goes below 0.
    Returns the new total.
    """
    client.loyalty_points = max(0, client.loyalty_points + points)
    return client.loyalty_points


# ─── Late Streak ──────────────────────────────────────────────────────────────

def update_late_streak(client, points: int) -> bool:
    """
    Track consecutive late payments.
    If client reaches LATE_STREAK_LIMIT, reset all points and streak.
    Returns True if reset was triggered.
    """
    if points >= 0:
        # On time or early — reset streak
        client.consecutive_late_payments = 0
    else:
        client.consecutive_late_payments += 1

    if client.consecutive_late_payments >= LATE_STREAK_LIMIT:
        client.loyalty_points = 0
        client.consecutive_late_payments = 0
        return True

    return False