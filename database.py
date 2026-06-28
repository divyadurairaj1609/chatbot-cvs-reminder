import sqlite3
from datetime import datetime, timedelta

# Connect to SQLite database
# This creates cvs.db file automatically!
def get_connection():
    return sqlite3.connect("cvs.db")

# ─────────────────────────────────────────
# Create tables and add sample patients
# ─────────────────────────────────────────
def setup_database():
    """Create database tables and add sample CVS patients"""
    
    conn = get_connection()
    cursor = conn.cursor()
    
    # Create patients table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS patients (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            phone TEXT NOT NULL,
            email TEXT,
            date_of_birth TEXT,
            address TEXT
        )
    """)
    
    # Create prescriptions table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS prescriptions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            patient_id INTEGER,
            medicine_name TEXT NOT NULL,
            doctor_name TEXT,
            total_tablets INTEGER,
            tablets_per_day INTEGER,
            start_date TEXT,
            refill_date TEXT,
            last_reminder_sent TEXT,
            status TEXT DEFAULT 'active',
            FOREIGN KEY (patient_id) REFERENCES patients(id)
        )
    """)

    # Create reminders log table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS reminder_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            patient_id INTEGER,
            prescription_id INTEGER,
            reminder_type TEXT,
            sent_at TEXT,
            message TEXT,
            FOREIGN KEY (patient_id) REFERENCES patients(id)
        )
    """)
    
    # Check if sample data already exists
    cursor.execute("SELECT COUNT(*) FROM patients")
    count = cursor.fetchone()[0]
    
    if count == 0:
        # Add sample CVS patients
        today = datetime.now()
        
        sample_patients = [
            {
                "name": "John Smith",
                "phone": "+1-555-123-4567",
                "email": "john.smith@email.com",
                "dob": "1975-03-15",
                "address": "123 Main St, Boston MA",
                "medicine": "Lisinopril 10mg",
                "doctor": "Dr. Johnson",
                "tablets": 30,
                "per_day": 1,
                "days_ago": 25  # Started 25 days ago → needs refill in 5 days!
            },
            {
                "name": "Mary Johnson",
                "phone": "+1-555-987-6543",
                "email": "mary.j@email.com",
                "dob": "1982-07-22",
                "address": "456 Oak Ave, Boston MA",
                "medicine": "Metformin 500mg",
                "doctor": "Dr. Williams",
                "tablets": 60,
                "per_day": 2,
                "days_ago": 25  # Started 25 days ago → needs refill in 5 days!
            },
            {
                "name": "Bob Williams",
                "phone": "+1-555-456-7890",
                "email": "bob.w@email.com",
                "dob": "1968-11-30",
                "address": "789 Pine Rd, Boston MA",
                "medicine": "Atorvastatin 20mg",
                "doctor": "Dr. Brown",
                "tablets": 90,
                "per_day": 1,
                "days_ago": 85  # Started 85 days ago → needs refill in 5 days!
            },
            {
                "name": "Sarah Davis",
                "phone": "+1-555-321-0987",
                "email": "sarah.d@email.com",
                "dob": "1990-05-10",
                "address": "321 Elm St, Boston MA",
                "medicine": "Amoxicillin 250mg",
                "doctor": "Dr. Martinez",
                "tablets": 30,
                "per_day": 3,
                "days_ago": 3  # Started 3 days ago → no reminder needed yet
            },
            {
                "name": "Michael Brown",
                "phone": "+1-555-654-3210",
                "email": "michael.b@email.com",
                "dob": "1955-09-18",
                "address": "654 Maple Dr, Boston MA",
                "medicine": "Amlodipine 5mg",
                "doctor": "Dr. Wilson",
                "tablets": 30,
                "per_day": 1,
                "days_ago": 28  # Started 28 days ago → OVERDUE!
            }
        ]
        
        for p in sample_patients:
            # Insert patient
            cursor.execute("""
                INSERT INTO patients (name, phone, email, date_of_birth, address)
                VALUES (?, ?, ?, ?, ?)
            """, (p["name"], p["phone"], p["email"], p["dob"], p["address"]))
            
            patient_id = cursor.lastrowid
            
            # Calculate dates
            start_date = today - timedelta(days=p["days_ago"])
            days_supply = p["tablets"] // p["per_day"]
            refill_date = start_date + timedelta(days=days_supply)
            
            # Insert prescription
            cursor.execute("""
                INSERT INTO prescriptions 
                (patient_id, medicine_name, doctor_name, total_tablets, 
                 tablets_per_day, start_date, refill_date, status)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                patient_id,
                p["medicine"],
                p["doctor"],
                p["tablets"],
                p["per_day"],
                start_date.strftime("%Y-%m-%d"),
                refill_date.strftime("%Y-%m-%d"),
                "active"
            ))
        
        print("✅ Sample patient database created with 5 patients!")
    
    conn.commit()
    conn.close()

# ─────────────────────────────────────────
# Get patients who need reminders
# ─────────────────────────────────────────
def get_patients_due_for_reminder():
    """Get all patients who need refill reminder"""
    
    conn = get_connection()
    cursor = conn.cursor()
    
    today = datetime.now().strftime("%Y-%m-%d")
    reminder_threshold = (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d")
    
    cursor.execute("""
        SELECT 
            p.id, p.name, p.phone, p.email,
            pr.id as prescription_id,
            pr.medicine_name, pr.doctor_name,
            pr.tablets_per_day, pr.refill_date,
            pr.last_reminder_sent
        FROM patients p
        JOIN prescriptions pr ON p.id = pr.patient_id
        WHERE pr.status = 'active'
        AND pr.refill_date <= ?
        ORDER BY pr.refill_date ASC
    """, (reminder_threshold,))
    
    patients = cursor.fetchall()
    conn.close()
    
    return patients

# ─────────────────────────────────────────
# Log reminder sent
# ─────────────────────────────────────────
def log_reminder(patient_id, prescription_id, reminder_type, message):
    """Log that a reminder was sent"""
    
    conn = get_connection()
    cursor = conn.cursor()
    
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    cursor.execute("""
        INSERT INTO reminder_log 
        (patient_id, prescription_id, reminder_type, sent_at, message)
        VALUES (?, ?, ?, ?, ?)
    """, (patient_id, prescription_id, reminder_type, now, message))
    
    # Update last reminder sent
    cursor.execute("""
        UPDATE prescriptions 
        SET last_reminder_sent = ?
        WHERE id = ?
    """, (now, prescription_id))
    
    conn.commit()
    conn.close()

# ─────────────────────────────────────────
# Get all patients
# ─────────────────────────────────────────
def get_all_patients():
    """Get all patients from database"""
    
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT 
            p.name, p.phone, p.email,
            pr.medicine_name, pr.doctor_name,
            pr.total_tablets, pr.tablets_per_day,
            pr.refill_date, pr.status
        FROM patients p
        JOIN prescriptions pr ON p.id = pr.patient_id
        ORDER BY pr.refill_date ASC
    """)
    
    patients = cursor.fetchall()
    conn.close()
    
    result = f"\n📋 CVS Patient Database ({len(patients)} prescriptions):\n"
    result += "=" * 50 + "\n"
    
    today = datetime.now()
    
    for p in patients:
        refill_date = datetime.strptime(p[7], "%Y-%m-%d")
        days_remaining = (refill_date - today).days
        
        if days_remaining < 0:
            status_emoji = "❗ OVERDUE"
        elif days_remaining <= 3:
            status_emoji = "🚨 URGENT"
        elif days_remaining <= 7:
            status_emoji = "⚠️ DUE SOON"
        else:
            status_emoji = "✅ OK"
        
        result += f"""
Patient: {p[0]}
Phone: {p[1]}
Medicine: {p[3]}
Doctor: {p[4]}
Refill Date: {p[7]}
Days Remaining: {days_remaining} days
Status: {status_emoji}
{"-" * 40}"""
    
    return result