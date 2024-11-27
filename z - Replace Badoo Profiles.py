import os
import time
import json
import requests
import subprocess
from airtable import Airtable
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Environment Variables
PAT = os.getenv("AIRTABLE_PAT", "")
BASE_ID = os.getenv("AIRTABLE_BASE_ID", "")
TABLE_NAME = os.getenv("AIRTABLE_TABLE_NAME", "To Be Made copy")
CREATE_ACCOUNT_PATH = os.getenv("MAKE_A_PROFILE_PATH", "path_to_create_account_script")
CREATE_DOLPHIN_PROFILE_PATH = os.getenv("CREATE_DOLPHIN_PROFILE", "path_to_dolphin_script")
DISCORD_WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL", "")

# Initialize Airtable object
airtable = Airtable(BASE_ID, TABLE_NAME, PAT)


def send_to_discord(message):
    """
    Sends a message to Discord via webhook.
    
    Args:
        message (str): The message content to send.
    """
    if not DISCORD_WEBHOOK_URL:
        print("Discord webhook URL is not configured.")
        return

    try:
        requests.post(DISCORD_WEBHOOK_URL, json={'content': message, 'username': 'Scheduler Bot'})
    except requests.RequestException as e:
        print(f"Error sending message to Discord: {e}")


def process_create_badoo_account(record_id):
    """
    Processes creating a Badoo account for a specific record.
    
    Args:
        record_id (str): Airtable record ID.
    """
    try:
        airtable.update(record_id, {'Badoo Status': ['Making']})
        subprocess.run(['python', CREATE_ACCOUNT_PATH], check=True)
        print("Successfully created a Badoo account.")
        airtable.update(record_id, {'Badoo Status': ['Made']})
    except Exception as e:
        airtable.update(record_id, {'Badoo Status': ['Failed']})
        print(f"Error creating Badoo account: {e}")
        send_to_discord(f"Badoo Account Creation Failed: {e}")
        raise


def trigger_dolphin_profile_creation(model_name, num_profiles, record_id, country):
    """
    Triggers the creation of Dolphin Anty profiles.
    
    Args:
        model_name (str): Name of the model.
        num_profiles (int): Number of profiles to create.
        record_id (str): Airtable record ID.
        country (str): Country for the profile.
    """
    try:
        airtable.update(record_id, {'Dolphin Status': ['Making']})
        subprocess.run(
            ['python', CREATE_DOLPHIN_PROFILE_PATH, model_name, country, str(num_profiles)],
            check=True
        )
        print(f"Successfully created Dolphin Anty profile for {model_name}.")
        airtable.update(record_id, {'Dolphin Status': ['Made']})
    except Exception as e:
        airtable.update(record_id, {'Dolphin Status': ['Failed']})
        print(f"Error creating Dolphin Anty profile for {model_name}: {e}")
        send_to_discord(f"Dolphin Anty Profile Creation Failed: {e}")
        raise


def process_airtable_records():
    """
    Processes all Airtable records to manage Dolphin Anty and Badoo account creation.
    """
    all_records = airtable.get_all()
    for record in all_records:
        record_id = record['id']
        fields = record['fields']
        dolphin_status = fields.get('Dolphin Status', [''])[0] if fields.get('Dolphin Status') else ''
        badoo_status = fields.get('Badoo Status', [''])[0] if fields.get('Badoo Status') else ''
        tags = fields.get('Tags', [])
        model_name = tags[0] if tags else ''
        country = tags[-1] if tags else ''

        if 'Badoo' in tags:
            if dolphin_status == 'Scheduled':
                num_profiles = fields.get('Number Of Profiles To Make If Manual', 1)
                try:
                    num_profiles = int(num_profiles)
                except ValueError:
                    num_profiles = 1

                try:
                    trigger_dolphin_profile_creation(model_name, num_profiles, record_id, country)
                    process_create_badoo_account(record_id)
                    print(
                        f"Badoo Scheduler - Profile created successfully for model {model_name}.\n{'-' * 113}",
                        flush=True
                    )
                    send_to_discord(
                        f"Badoo Scheduler - Profile created successfully for model {model_name}.\n{'-' * 113}"
                    )
                except Exception as e:
                    print(f"Error during profile creation process: {e}")
            elif dolphin_status == 'Made' and badoo_status == 'Scheduled':
                try:
                    process_create_badoo_account(record_id)
                    print(
                        f"Badoo Scheduler - Account created successfully for model {model_name}.\n{'-' * 113}",
                        flush=True
                    )
                    send_to_discord(
                        f"Badoo Scheduler - Account created successfully for model {model_name}.\n{'-' * 113}"
                    )
                except Exception as e:
                    print(f"Error creating Badoo account for model {model_name}: {e}")


def main():
    """
    Main loop to process records every 60 seconds.
    """
    while True:
        process_airtable_records()
        time.sleep(60)


if __name__ == "__main__":
    main()
