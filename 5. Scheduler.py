import os
import random
import requests
from datetime import datetime, timedelta
from airtable import Airtable
from dotenv import load_dotenv

load_dotenv()


class AirtableHandler:
    """Class to handle interactions with Airtable."""

    def __init__(self, base_id, pat, profiles_table_name, scheduled_runs_table_name):
        self.profiles_table = Airtable(base_id, profiles_table_name, pat)
        self.scheduled_runs_table = Airtable(base_id, scheduled_runs_table_name, pat)

    def get_all_profiles(self):
        """Retrieves all profiles from the 'Profiles' table."""
        try:
            return self.profiles_table.get_all()
        except Exception as e:
            self.log_error(f"Error retrieving profiles from Airtable: {e}")
            return []

    def get_all_scheduled_runs(self):
        """Retrieves all records from the 'Scheduled Runs' table."""
        try:
            return self.scheduled_runs_table.get_all()
        except Exception as e:
            self.log_error(f"Error retrieving scheduled runs: {e}")
            return []

    def clear_scheduled_runs(self):
        """Removes all existing records from the 'Scheduled Runs' table."""
        try:
            records = self.get_all_scheduled_runs()
            record_ids = [record['id'] for record in records]
            self.scheduled_runs_table.batch_delete(record_ids)
        except Exception as e:
            self.log_error(f"Error clearing scheduled runs: {e}")

    def insert_scheduled_run(self, data):
        """Inserts a new record into the 'Scheduled Runs' table."""
        try:
            self.scheduled_runs_table.insert(data)
        except Exception as e:
            self.log_error(f"Error inserting scheduled run: {e}")

    @staticmethod
    def log_error(message):
        print(f"Airtable Error: {message}")
        send_to_discord(f"Airtable Error: {message}")


def create_scheduled_runs(day_choice, airtable_handler, profiles, run_config):
    """
    Creates scheduled runs for Airtable profiles based on configuration.

    Args:
        day_choice (str): Day choice ('1' for today, '2' for tomorrow).
        airtable_handler (AirtableHandler): Airtable handler instance.
        profiles (list): List of profiles retrieved from Airtable.
        run_config (dict): Configuration for runs and swipe amounts by status.
    """
    time_slots = {
        'all_day': (10, 2359, 20),
        'early_morning': (10, 300, 20),
        'morning': (900, 1159, 10),
        'hot_evening': (2000, 2359, 30),
        'afternoon': (1700, 1959, 20),
    }

    for profile in profiles:
        tags = profile['fields'].get('Tags', [])
        if 'Badoo' not in tags:
            continue

        model_name = profile['fields'].get('Model Name')
        dolphin_name = profile['fields'].get('Dolphin Name')
        dolphin_id = profile['fields'].get('Dolphin ID')
        status = profile['fields'].get('Status')
        country = profile['fields'].get('Country')

        status = status[0] if isinstance(status, list) else status
        runs_range = run_config.get(status)

        if not runs_range:
            continue

        runs_per_day = random.randint(*runs_range['runs'])
        swipe_amount_range = runs_range['swipe_amount']

        scheduled_times = []
        for _ in range(runs_per_day):
            while True:
                random_number = random.randint(1, 100)
                selected_time_slot = time_slots['all_day']
                for slot, (start_time, end_time, probability) in time_slots.items():
                    if random_number <= probability:
                        selected_time_slot = (start_time, end_time)
                        break

                random_hour = random.randint(selected_time_slot[0] // 100, selected_time_slot[1] // 100)
                random_minute = random.randint(0, 59)
                time_to_run = random_hour * 100 + random_minute

                if all(abs(time_to_run - scheduled_time) >= 100 for scheduled_time in scheduled_times):
                    scheduled_times.append(time_to_run)
                    break

        for time_to_run in scheduled_times:
            date_offset = 0 if day_choice == '1' else 1
            run_time = datetime.now() + timedelta(days=date_offset, hours=time_to_run // 100, minutes=time_to_run % 100)
            swipe_amount = random.randint(*swipe_amount_range)

            airtable_handler.insert_scheduled_run({
                'Model Name': model_name,
                'Dolphin Name': dolphin_name,
                'Dolphin ID': dolphin_id,
                'Status': status,
                'Tags': tags,
                'Country': country,
                'Date To Run': run_time.strftime('%Y-%m-%d'),
                'Time To Run': int(run_time.strftime('%H%M')),
                'Swipe Amount': swipe_amount,
                'Running Progress': ["Scheduled"],
            })


def send_to_discord(message):
    """
    Sends messages to Discord via webhook.

    Args:
        message (str): Message content.
    """
    discord_webhook_url = os.getenv("DISCORD_WEBHOOK_URL", "")
    if not discord_webhook_url:
        print("Discord webhook URL is not set.")
        return

    data = {'content': message, 'username': 'Notification Bot'}
    try:
        requests.post(discord_webhook_url, json=data)
    except requests.RequestException as e:
        print(f"Error sending message to Discord: {e}")


def main():
    """
    Main workflow for scheduling runs in Airtable.
    """
    pat = os.getenv("AIRTABLE_PAT", "")
    base_id = os.getenv("AIRTABLE_BASE_ID", "")
    profiles_table_name = os.getenv("PROFILES_TABLE_NAME", "Profiles Badoo")
    scheduled_runs_table_name = os.getenv("SCHEDULED_RUNS_TABLE_NAME", "Scheduled Runs Badoo")

    if not all([pat, base_id, profiles_table_name, scheduled_runs_table_name]):
        print("Error: Missing required environment variables.")
        return

    airtable_handler = AirtableHandler(base_id, pat, profiles_table_name, scheduled_runs_table_name)

    try:
        day_choice = '1'
        airtable_handler.clear_scheduled_runs()
        profiles = airtable_handler.get_all_profiles()

        run_config = {
            'Stage 1': {'runs': (1, 4), 'swipe_amount': (30, 120)},
            'Stage 2': {'runs': (3, 6), 'swipe_amount': (80, 220)},
            'Stage 3': {'runs': (2, 6), 'swipe_amount': (160, 350)},
        }

        create_scheduled_runs(day_choice, airtable_handler, profiles, run_config)

    except Exception as e:
        error_message = f"Badoo Scheduler - General error in scheduler: {e}"
        print(error_message)
        send_to_discord(error_message)


if __name__ == "__main__":
    main()
