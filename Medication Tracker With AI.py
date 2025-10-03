# This application combines data persistence (saving/loading medication data)
# with LLM integration (getting a quick AI fact about the medication) and dose tracking.

import json
import os
import sys
import requests
import time
from datetime import datetime

# --- CONFIGURATION (YOUR KEY IS NOW DIRECTLY INCLUDED) ---
# Ensure your API key is correctly inserted here for access.
API_KEY = "AIzaSyDHLgMqeD8vvKmOVPfYPszGfx7rVE6CY98" 
GEMINI_MODEL = "gemini-2.5-flash-preview-05-20"
GEMINI_API_URL = f"https://generativelanguage.googleapis.com/v1beta/models/{GEMINI_MODEL}:generateContent?key={API_KEY}"

# --- GLOBAL VARIABLES ---
DATA_FILE = "meds_ai_data.json"
medication_list = []

# --- SECTION 1: DATA PERSISTENCE (Load/Save Functions) ---

def load_medications():
    """Loads the medication list from the JSON file and normalizes old data."""
    global medication_list
    
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, 'r') as file:
                medication_list = json.load(file)
            
            # --- FIX: Data Migration/Normalization ---
            # This loop ensures every loaded medication object has the 'doses_taken' key,
            # which prevents the KeyError when viewing/tracking doses on old records.
            for med in medication_list:
                if 'doses_taken' not in med:
                    med['doses_taken'] = []
            # ----------------------------------------
            
            print(f"✅ Successfully loaded {len(medication_list)} medication records.")
        except json.JSONDecodeError:
            print(f"⚠️ Warning: Data file {DATA_FILE} is corrupted or empty. Starting fresh.")
            medication_list = []
    else:
        print(f"✨ Starting new session. No previous data found.")

def save_medications():
    """Saves the current medication list back to the JSON file."""
    try:
        with open(DATA_FILE, 'w') as file:
            json.dump(medication_list, file, indent=4)
        print(f"\n✅ Data saved successfully to {DATA_FILE}. Program exiting.")
    except IOError:
        print("❌ Error: Could not save data to file.")

# --- SECTION 2: LLM INTEGRATION (AI Function) ---

def generate_ai_fact(med_name):
    """
    Connects to the Gemini API to generate detailed, structured facts about the medication.
    The system prompt has been updated for clinical details and bullet points.
    """
    
    # --- UPDATED SYSTEM PROMPT FOR CLINICAL INFO ---
    system_prompt = (
        "You are a specialized clinical pharmacist. "
        "Provide one common side effect and one serious drug interaction "
        "for the requested medication. Use two bullet points for clarity."
    )
    user_query = f"Provide clinical details for the medication: {med_name}."
    
    payload = {
        "contents": [{"parts": [{"text": user_query}]}],
        "systemInstruction": {"parts": [{"text": system_prompt}]},
    }
    
    max_retries = 3
    for attempt in range(max_retries):
        try:
            response = requests.post(
                GEMINI_API_URL, 
                headers={'Content-Type': 'application/json'}, 
                data=json.dumps(payload)
            )
            response.raise_for_status()
            data = response.json()
            
            if 'candidates' in data and len(data['candidates']) > 0:
                text = data['candidates'][0]['content']['parts'][0]['text']
                return text
            else:
                return "AI response structure empty."

        except requests.exceptions.RequestException as e:
            print(f"⚠️ API Error (Attempt {attempt + 1}/{max_retries}): {e}")
            if attempt < max_retries - 1:
                sleep_time = 2 ** attempt
                time.sleep(sleep_time)
            else:
                return "Failed to connect to the AI service after multiple retries."
        
        except (KeyError, IndexError):
            return "An error occurred while parsing the AI's response."
            
    return "AI request failed."

# --- SECTION 3: APPLICATION LOGIC (Core Functions) ---

def add_medication():
    """Prompts the user for details and adds a new medication record."""
    print("\n--- Add New Medication ---")
    
    name = input("Enter medication name: ").strip()
    dosage = input("Enter dosage (e.g., 200mg): ").strip()
    frequency = input("Enter frequency (e.g., once daily): ").strip()
    
    if not name:
        print("Medication name cannot be empty. Canceled.")
        return

    # Initialize doses_taken list for the new tracking feature
    new_med = {
        "name": name,
        "dosage": dosage,
        "frequency": frequency,
        "added_date": time.strftime("%Y-%m-%d"),
        "doses_taken": []
    }
    
    medication_list.append(new_med)
    print(f"'{name}' added successfully!")
    
    # Prompt user for AI interaction
    ai_choice = input("Would you like an AI clinical summary for this medication? (y/n): ").strip().lower()
    if ai_choice == 'y':
        print("🧠 Connecting to AI for clinical data...")
        fact = generate_ai_fact(name)
        print("\n--- AI Clinical Summary ---")
        print(fact)
        print("---------------------------")


def view_medications():
    """Displays all current medications and their dose history."""
    print("\n--- Current Medications & History ---")
    
    if not medication_list:
        print("Your medication list is currently empty.")
        return

    for i, med in enumerate(medication_list):
        print(f"--- Record {i + 1} ({med['name']}) ---")
        print(f"Dosage: {med['dosage']}")
        print(f"Frequency: {med['frequency']}")
        
        # This line is now safe because we ensured 'doses_taken' exists in load_medications()
        print(f"Doses Taken ({len(med['doses_taken'])} total):")
        
        # Display the last 3 doses taken, or all if fewer than 3
        history = med['doses_taken']
        if history:
            # Displaying in reverse order so the newest dose is at the top
            for j, dose_time in enumerate(reversed(history[:3])):
                print(f"  - {dose_time} (Most Recent Dose)")
        else:
            print("  - No doses recorded yet.")
    print("-------------------------------------")

def record_dose():
    """Allows the user to select a medication and record a dose taken now."""
    if not medication_list:
        print("\n❌ Cannot record dose. Please add a medication first (Option 1).")
        return

    print("\n--- Record Dose Taken ---")
    for i, med in enumerate(medication_list):
        # Display the name, dosage, and frequency
        print(f"{i + 1}. {med['name']} ({med['dosage']}, {med['frequency']})")

    try:
        choice = int(input("Enter the number of the medication taken: "))
        if 1 <= choice <= len(medication_list):
            med_index = choice - 1
            
            # Record the current date and time
            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            medication_list[med_index]['doses_taken'].append(now)
            
            name = medication_list[med_index]['name']
            print(f"✅ Dose of '{name}' recorded successfully at {now}.")
        else:
            print("Invalid number entered.")
    except ValueError:
        print("Invalid input. Please enter a number.")


# --- SECTION 4: MAIN EXECUTION (The Control Flow) ---

def main_menu():
    """Runs the main program loop."""
    load_medications() # Load data when the program starts
    
    while True:
        print("\n--- Digital Health Tracker ---")
        print("1. Add Medication")
        print("2. View Medications")
        print("3. Record Dose Taken")
        print("4. Exit and Save Data")
        
        choice = input("Enter your choice (1, 2, 3, or 4): ").strip()
        
        if choice == '1':
            add_medication()
        elif choice == '2':
            view_medications()
        elif choice == '3':
            record_dose()
        elif choice == '4':
            save_medications() # Save data when the program exits
            sys.exit(0)
        else:
            print("Invalid choice. Please enter 1, 2, 3, or 4.")

# Standard Python entry point
if __name__ == "__main__":
    main_menu()
