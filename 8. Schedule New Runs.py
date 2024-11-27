import os
import random
import requests
import ast
import sys
from datetime import datetime
from airtable import Airtable
from dotenv import load_dotenv

load_dotenv()

# Constants
BASE_ID = os.getenv("AIRTABLE_BASE_ID", "")
PAT = os.getenv("AIRTABLE_PAT", "")
SCHEDULED_RUNS_TABLE_NAME = os.getenv("SCHEDULED_RUNS_TABLE_NAME", "Scheduled Runs Badoo")
PROFILES_TABLE_NAME = os.getenv("PROFILES_TABLE_NAME", "Profiles Badoo")
DOLPHIN_ANTY_API_URL = os.getenv("DOLPHIN_ANTY_API_URL", "https://dolphin-anty-api.com/browser_profiles/")
DISCORD_WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL", "")

# Airtable tables
scheduled_runs_table = Airtable(BASE_ID, SCHEDULED_RUNS_TABLE_NAME, PAT)
profiles_table = Airtable(BASE_ID, PROFILES_TABLE_NAME, PAT)

# Run configurations
RUN_CONFIG = {
    'runs': (1, 3),  
    'swipe_amount': (30, 120),  
}

TIME_SLOTS = {
    'all_day': (10, 2359, 20),
    'afternoon': (1200, 1700, 30),  
}


def send_to_discord(message):
    """
    Sends a message to Discord via webhook.

    Args:
        message (str): Content of the message to send.
    """
    if not DISCORD_WEBHOOK_URL:
        print("Discord webhook URL is not configured.")
        return

    try:
        requests.post(DISCORD_WEBHOOK_URL, json={'content': message, 'username': 'Scheduler Bot'})
    except requests.RequestException as e:
        print(f"Error sending message to Discord: {e}")


def get_dolphin_id_from_file(file_path):
    """
    Retrieves the Dolphin ID from a given file.

    Args:
        file_path (str): Path to the file containing Dolphin profile data.

    Returns:
        str: First Dolphin ID found in the file.
    """
    try:
        with open(file_path, 'r') as file:
            file_contents = file.read()
            profile_names = ast.literal_eval(file_contents.split('=', 1)[1].strip())
            return next(iter(profile_names))
    except Exception as e:
        print(f"Error reading Dolphin ID from file: {e}")
        sys.exit(1)


def fetch_dolphin_anty_profile_details(dolphin_id):
    """
    Fetches Dolphin Anty profile details, including tags and name.

    Args:
        dolphin_id (str): ID of the Dolphin profile.

    Returns:
        tuple: Tags (list) and Dolphin name (str).
    """
    api_key = os.getenv("DOLPHIN_ANTY_API_KEY", "")
    if not api_key:
        print("Dolphin Anty API key is not configured.")
        sys.exit(1)

    headers = {"Authorization": f"Bearer {api_key}"}
    try:
        response = requests.get(f"{DOLPHIN_ANTY_API_URL}{dolphin_id}", headers=headers)
        response.raise_for_status()
        profile_data = response.json()
        return profile_data['data'].get('tags', []), profile_data['data'].get('name', '')
    except requests.RequestException as e:
        print(f"Error fetching Dolphin Anty profile details: {e}")
        send_to_discord(f"Failed to fetch Dolphin Anty profile for ID {dolphin_id}. Error: {e}")
        return [], ''


def schedule_swipes_for_new_profile(dolphin_id, model_name):
    """
    Schedules swipes for a new profile in the Airtable tables.

    Args:
        dolphin_id (str): ID of the Dolphin profile.
        model_name (str): Name of the model associated with the profile.
    """
    tags, dolphin_name = fetch_dolphin_anty_profile_details(dolphin_id)
    now = datetime.now()

    runs_per_day = random.randint(*RUN_CONFIG['runs'])
    swipe_amount_range = RUN_CONFIG['swipe_amount']
    scheduled_times = []

    for _ in range(runs_per_day):
        while True:
            random_number = random.randint(1, 100)
            selected_time_slot = TIME_SLOTS['all_day']
            for slot, (start_time, end_time, probability) in TIME_SLOTS.items():
                if random_number <= probability:
                    selected_time_slot = (start_time, end_time)
                    break

            random_hour = random.randint(selected_time_slot[0] // 100, selected_time_slot[1] // 100)
            random_minute = random.randint(0, 59)
            time_to_run = datetime(now.year, now.month, now.day, random_hour, random_minute)

            if time_to_run > now:
                scheduled_times.append(time_to_run)
                break

    for time_to_run in scheduled_times:
        swipe_amount = random.randint(*swipe_amount_range)

        # Insert into Scheduled Runs table
        scheduled_runs_table.insert({
            'Model Name': model_name,
            'Dolphin ID': int(dolphin_id),
            'Dolphin Name': dolphin_name,
            'Status': ['Stage 1'],
            'Tags': tags,
            'Date To Run': time_to_run.strftime('%Y-%m-%d'),
            'Time To Run': int(time_to_run.strftime('%H%M')),
            'Swipe Amount': swipe_amount,
            'Running Progress': ["Scheduled"],
        })

        # Insert into Profiles table
        profiles_table.insert({
            'Dolphin ID': int(dolphin_id),
            'Dolphin Name': dolphin_name,
            'Model Name': model_name,
            'Status': ['Stage 1'],
            'Tags': tags,
        })


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python ScheduleNewProfiles.py <model_name>")
        sys.exit(1)

    model_name = sys.argv[1]
    file_path = os.getenv("FILE_PATH", "path_to_dolphin_file.txt")  # Replace with the actual path or use an env variable
    dolphin_id = get_dolphin_id_from_file(file_path)

    schedule_swipes_for_new_profile(dolphin_id, model_name)
