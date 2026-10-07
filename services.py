import datetime
from decimal import Decimal, ROUND_HALF_UP
import httpx # Use httpx for sync/async HTTP requests to the PaySwift sandbox

# --- 1. Payout Calculation Engine ---
def calculate_owed_payout(rider_id: str, dispute_date_str: str, trips_data: list) -> dict:
    """
    Applies the exact ops wiki payout policy to a list of trip records[cite: 1].
    trips_data should be a list of dicts: 
    [{'status': 'completed', 'distance_km': 3.5, 'surge_multiplier': 1.2}, ...]
    """
    dispute_date = datetime.datetime.strptime(dispute_date_str, "%Y-%m-%d").date()
    today = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=5, minutes=30))).date() # IST timezone
    
    # Check the 7-day limit policy[cite: 1]
    if (today - dispute_date).days > 7:
        return {"error": "Dispute date is older than 7 days. Cannot process."}

    total_owed = Decimal('0.0')
    completed_trips_count = 0
    rider_cancellations = 0

    for trip in trips_data:
        if trip['status'] == 'completed':
            completed_trips_count += 1
            distance = Decimal(str(trip['distance_km']))
            surge = Decimal(str(trip['surge_multiplier']))
            
            # Base 25 + 6 per km after first 2km[cite: 1]
            fare = Decimal('25.0')
            if distance > Decimal('2.0'):
                fare += (distance - Decimal('2.0')) * Decimal('6.0')
            
            # Surge applies to the whole fare[cite: 1]
            fare = fare * surge
            
            # Round to nearest rupee, 0.5 rounds up[cite: 1]
            fare = fare.quantize(Decimal('1'), rounding=ROUND_HALF_UP)
            total_owed += fare
            
        elif trip['status'] == 'cancelled':
            # ₹10 penalty for rider cancellations[cite: 1]
            rider_cancellations += 1
            total_owed -= Decimal('10.0')
            
        # 'customer_cancelled' does nothing (earns nothing, no penalty)[cite: 1]

    # Apply daily incentive for 12 or more trips[cite: 1]
    if completed_trips_count >= 12:
        total_owed += Decimal('150.0')

    return {
        "status": "success",
        "calculated_owed": float(total_owed),
        "completed_trips": completed_trips_count,
        "penalties": rider_cancellations * 10
    }

# --- 2. Auto-Pay & Ops Escalation Logic ---
def execute_payout(rider_id: str, amount_owed: float, already_paid: float) -> dict:
    """
    Enforces the finance department's auto-pay limits[cite: 1].
    """
    dispute_amount = amount_owed - already_paid
    
    if dispute_amount <= 0:
        return {"action": "rejected", "reason": "Rider has already been fully paid."}
        
    # Auto-pay limit is up to 200 per dispute[cite: 1]
    if dispute_amount <= 200:
        # TODO: Implement database check here to ensure they haven't been auto-paid today[cite: 1]
        
        # 1. Call PaySwift Sandbox via HTTP POST to process the transaction[cite: 1, 2]
        # payswift_response = httpx.post("http://localhost:8080/payout", json={"rider_id": rider_id, "amount": dispute_amount})
        
        # 2. Record the payout in your database
        return {"action": "auto_paid", "amount": dispute_amount}
        
    else:
        # Amount exceeds 200; escalate to ops team[cite: 1]
        # TODO: Insert record into 'pending_approvals' database table[cite: 1, 2]
        return {"action": "escalated", "reason": "Amount exceeds 200 auto-pay limit. Sent to ops for approval."}