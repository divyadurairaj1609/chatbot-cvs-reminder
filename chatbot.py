import anthropic
import os
from dotenv import load_dotenv
from database import setup_database, get_all_patients
from reminder import run_automatic_reminders

load_dotenv()

claude = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

# ─────────────────────────────────────────
# Setup database and run auto reminders
# This happens AUTOMATICALLY on startup!
# ─────────────────────────────────────────
print("=" * 50)
print("   CVS Pharmacy Prescription Reminder Bot")
print("=" * 50)

# Step 1: Setup database
print("\n📦 Setting up database...")
setup_database()

# Step 2: Auto run reminders on startup!
print("\n🔔 Running automatic reminder check...")
run_automatic_reminders()

print("\n" + "=" * 50)
print("💬 Chat with CVS Bot")
print("=" * 50)
print("You can ask me:")
print("  Show all patients")
print("  Check who needs reminders")
print("  Send reminders again")
print("Type 'quit' to exit\n")

# Define tools
tools = [
    {
        "name": "get_all_patients",
        "description": "Show all patients in the CVS database with their prescription status. Use when user asks to see all patients or prescriptions.",
        "input_schema": {
            "type": "object",
            "properties": {},
            "required": []
        }
    },
    {
        "name": "run_automatic_reminders",
        "description": "Check database and send reminders to all patients due for refill. Use when user asks to send reminders or check who needs refills.",
        "input_schema": {
            "type": "object",
            "properties": {},
            "required": []
        }
    }
]

# Conversation history
history = []

def handle_tool_call(tool_name, tool_input):
    if tool_name == "get_all_patients":
        return get_all_patients()
    elif tool_name == "run_automatic_reminders":
        return run_automatic_reminders()
    return "Function not found"

# Main chat loop
while True:
    user_input = input("\nYou: ").strip()

    if user_input.lower() == "quit":
        print("Goodbye!")
        break

    if not user_input:
        continue

    history.append({
        "role": "user",
        "content": user_input
    })

    response = claude.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1000,
        system="""You are a CVS Pharmacy prescription reminder assistant.
You help pharmacists manage patient prescription refills.
You have access to the CVS patient database.
Be professional, caring and helpful.""",
        tools=tools,
        messages=history
    )

    while response.stop_reason == "tool_use":
        tool_use = next(block for block in response.content
                       if block.type == "tool_use")

        tool_name = tool_use.name
        tool_input = tool_use.input

        print(f"\nChecking database...")
        result = handle_tool_call(tool_name, tool_input)

        history.append({
            "role": "assistant",
            "content": response.content
        })

        history.append({
            "role": "user",
            "content": [
                {
                    "type": "tool_result",
                    "tool_use_id": tool_use.id,
                    "content": result
                }
            ]
        })

        response = claude.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=1000,
            system="""You are a CVS Pharmacy prescription reminder assistant.
You help pharmacists manage patient prescription refills.
You have access to the CVS patient database.
Be professional, caring and helpful.""",
            tools=tools,
            messages=history
        )

    reply = response.content[0].text
    history.append({
        "role": "assistant",
        "content": reply
    })

    print(f"\nClaude: {reply}")
    print("-" * 50)