from datetime import datetime
from database import get_patients_due_for_reminder, log_reminder

# ─────────────────────────────────────────
# Simulate SMS Reminder
# ─────────────────────────────────────────
def simulate_sms(patient_name, phone, medicine, days_remaining):
    """Simulate sending SMS — like real CVS text messages!"""
    
    now = datetime.now().strftime("%B %d %Y %I:%M %p")
    
    if days_remaining < 0:
        message = f"CVS Pharmacy: URGENT! Your {medicine} prescription is OVERDUE for refill. Call 1-800-SHOP-CVS or visit cvs.com now. Reply STOP to opt out."
    elif days_remaining <= 3:
        message = f"CVS Pharmacy: Your {medicine} refill is due in {days_remaining} day(s). Visit cvs.com or call 1-800-SHOP-CVS to refill today! Reply STOP to opt out."
    else:
        message = f"CVS Pharmacy: Reminder! Your {medicine} prescription refill is due in {days_remaining} days. Visit cvs.com or your local CVS to refill. Reply STOP to opt out."
    
    sms_display = f"""
📱 SMS MESSAGE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
From: CVS Pharmacy (+1-800-746-7287)
To: {phone} ({patient_name})
Time: {now}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
{message}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
[SIMULATED — Real SMS not sent]
"""
    return sms_display, message

# ─────────────────────────────────────────
# Simulate Phone Call Reminder
# ─────────────────────────────────────────
def simulate_call(patient_name, phone, medicine, days_remaining, doctor):
    """Simulate automated phone call — like real CVS calls!"""
    
    now = datetime.now().strftime("%B %d %Y %I:%M %p")
    
    if days_remaining < 0:
        voice_message = f"""Hello, may I speak with {patient_name}? 

This is an automated message from CVS Pharmacy.

We are calling to let you know that your prescription 
for {medicine} prescribed by {doctor} is OVERDUE 
for a refill.

To refill your prescription please:
- Visit your nearest CVS Pharmacy location
- Call us at 1-800-SHOP-CVS
- Go online at cvs.com
- Use the CVS Pharmacy mobile app

Please refill your prescription as soon as possible
to avoid any interruption in your medication.

Thank you for choosing CVS Pharmacy.
Have a healthy day!"""

    elif days_remaining <= 3:
        voice_message = f"""Hello, may I speak with {patient_name}?

This is an automated message from CVS Pharmacy.

We are calling to remind you that your prescription
for {medicine} prescribed by {doctor} needs to be
refilled within {days_remaining} day(s).

To refill your prescription please:
- Visit your nearest CVS Pharmacy location
- Call us at 1-800-SHOP-CVS
- Go online at cvs.com
- Use the CVS Pharmacy mobile app

Don't run out of your medication!
Please refill your prescription today.

Thank you for choosing CVS Pharmacy.
Have a healthy day!"""

    else:
        voice_message = f"""Hello, may I speak with {patient_name}?

This is a friendly reminder from CVS Pharmacy.

Your prescription for {medicine} prescribed by
{doctor} will need to be refilled in {days_remaining} days.

You can refill your prescription by:
- Visiting your nearest CVS Pharmacy location
- Calling us at 1-800-SHOP-CVS
- Going online at cvs.com
- Using the CVS Pharmacy mobile app

Thank you for choosing CVS Pharmacy
for your healthcare needs.
Have a healthy day!"""
    
    call_display = f"""
📞 AUTOMATED PHONE CALL
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
From: CVS Pharmacy (+1-800-746-7287)
To: {phone} ({patient_name})
Time: {now}
Duration: Automated Message
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🔊 VOICE MESSAGE:

{voice_message}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
[SIMULATED — Real call not made]
"""
    return call_display, voice_message

# ─────────────────────────────────────────
# Run All Reminders Automatically
# ─────────────────────────────────────────
def run_automatic_reminders():
    """Check database and send all due reminders automatically"""
    
    print("\n" + "=" * 50)
    print("🔍 CVS Auto Reminder System Starting...")
    print("=" * 50)
    print(f"Checking database at {datetime.now().strftime('%B %d %Y %I:%M %p')}")
    print("Looking for patients due for refill...\n")
    
    # Get patients due for reminder
    patients = get_patients_due_for_reminder()
    
    if not patients:
        print("✅ No reminders needed today! All patients have enough supply.\n")
        return "No reminders needed today!"
    
    print(f"Found {len(patients)} patient(s) due for reminder!\n")
    
    all_reminders = ""
    
    for patient in patients:
        patient_id = patient[0]
        name = patient[1]
        phone = patient[2]
        email = patient[3]
        prescription_id = patient[4]
        medicine = patient[5]
        doctor = patient[6]
        refill_date_str = patient[8]
        
        # Calculate days remaining
        refill_date = datetime.strptime(refill_date_str, "%Y-%m-%d")
        days_remaining = (refill_date - datetime.now()).days
        
        print(f"Processing: {name} — {medicine} — {days_remaining} days remaining")
        
        # Send SMS
        sms_display, sms_message = simulate_sms(name, phone, medicine, days_remaining)
        print(sms_display)
        
        # Log SMS
        log_reminder(patient_id, prescription_id, "SMS", sms_message)
        
        # Make call
        call_display, call_message = simulate_call(name, phone, medicine, days_remaining, doctor)
        print(call_display)
        
        # Log call
        log_reminder(patient_id, prescription_id, "CALL", call_message)
        
        all_reminders += f"✅ Reminded {name} for {medicine}\n"
    
    summary = f"\n{'=' * 50}\n"
    summary += f"✅ Reminder Summary:\n"
    summary += f"Total patients reminded: {len(patients)}\n"
    summary += all_reminders
    summary += f"{'=' * 50}\n"
    
    print(summary)
    return summary