A Python chatbot that automatically checks a patient database
and sends prescription refill reminders — just like the real CVS reminder system!

### How It Works
Bot starts automatically

↓

Checks SQLite patient database

↓

Finds who needs refill reminder

↓

Simulates SMS message to patient

Simulates phone call to patient

↓

Opens chat for questions!

## Real World Use Case

This replicates exactly how CVS Pharmacy works:
- CVS stores patient prescriptions in a database
- System checks daily who needs refills
- Automatically sends SMS and makes calls
- Patients get reminded before running out!

## 🛠️ Functions We Built

### 📦 database.py
- setup_database() → Creates SQLite database with sample patients
- get_patients_due_for_reminder() → Finds who needs refill
- log_reminder() → Logs every reminder sent
- get_all_patients() → Lists all patients and status

### 📱 reminder.py
- simulate_sms() → Shows what SMS would be sent
- simulate_call() → Shows automated call script
- run_automatic_reminders() → Runs all reminders automatically
