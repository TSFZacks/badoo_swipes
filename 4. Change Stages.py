import os
import time
import subprocess
import requests
from airtable import Airtable
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

class AirtableHandler:
    """Handles interactions with Airtable."""
    def __init__(self, pat, base_id, table_name):
        self.airtable = Airtable(base_id, table_name, pat)

    def add_record(self, dolphin_id, model_name, dolphin_account_name):
        """
        Adds a record to the Airtable table if it doesn't already exist.
        Args:
            dolphin_id (int): Dolphin profile ID.
            model_name (str): Name of the model.
            dolphin_account_name (str): Account name in Dolphin.
        """
        try:
            existing_records = self.airtable.search('Dolphin ID', dolphin_id)
            if existing_records:
                return

            data = {
                'Dolphin ID': dolphin_id,
                'Model Name': model_name,
                'Dolphin Name': dolphin_account_name
            }
            self.airtable.insert(data)
        except Exception as e:
            self.log_error(f"Error while inserting data in Airtable: {e}")

    def update_record_status(self, dolphin_id, stage):
        """
        Updates the status field of a record in Airtable.
        Args:
            dolphin_id (int): Dolphin profile ID.
            stage (str): Stage to update.
        """
        try:
            records = self.airtable.search('Dolphin ID', str(dolphin_id))
            if records:
                record = records[0]
                record_id = record['id']
                current_status = record['fields'].get('Status', [])

                if stage not in current_status:
                    update_fields = {'Status': [stage]}
                    self.airtable.update(record_id, update_fields)
            else:
                self.log_error(f"No matching record found in Airtable for Dolphin ID {dolphin_id}")
        except Exception as e:
            self.log_error(f"Error updating Airtable for Dolphin ID {dolphin_id}: {e}")

    @staticmethod
    def log_error(message):
        print(f"Airtable Error: {message}")
        send_to_discord(f"Airtable Error: {message}")


class DolphinAntyHandler:
    """Handles interactions with the Dolphin Anty API."""
    def __init__(self, api_key):
        self.api_base_url = os.getenv("DOLPHIN_API_URL", "https://dolphin-anty-api.com/browser_profiles")
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }

    def get_profile_tags(self, dolphin_id):
        """
        Retrieves tags for a specific Dolphin profile.
        Args:
            dolphin_id (int): Dolphin profile ID.
        Returns:
            list: Tags associated with the profile.
        """
        url = f"{self.api_base_url}/{dolphin_id}"
        try:
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            return response.json().get('data', {}).get('tags', [])
        except requests.RequestException as e:
            self.log_error(f"Error fetching profile tags for Dolphin ID {dolphin_id}: {e}")
            return []

    def update_profile_status(self, dolphin_id, status_id):
        """
        Updates the status of a Dolphin profile.
        Args:
            dolphin_id (int): Dolphin profile ID.
            status_id (int): Status ID to update.
        """
        url = f"{self.api_base_url}/{dolphin_id}"
        data = {'statusId': status_id}
        try:
            response = requests.patch(url, headers=self.headers, json=data)
            response.raise_for_status()
        except requests.RequestException as e:
            self.log_error(f"Error updating status for Dolphin ID {dolphin_id}: {e}")

    def fetch_profiles(self, page=1, limit=50):
        """
        Fetches profiles from the Dolphin API.
        Args:
            page (int): Page number for pagination.
            limit (int): Number of profiles per page.
        Returns:
            dict: Profiles data and total pages.
        """
        try:
            response = requests.get(self.api_base_url, headers=self.headers, params={"limit": limit, "page": page})
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            self.log_error(f"Error fetching profiles: {e}")
            return {}

    @staticmethod
    def log_error(message):
        print(f"Dolphin Anty API Error: {message}")
        send_to_discord(f"Dolphin Anty API Error: {message}")


def categorize_by_age(created_at):
    """
    Categorizes profiles into stages based on their creation date.
    Args:
        created_at (str): Profile creation date in string format.
    Returns:
        str: Stage category.
    """
    creation_date = datetime.strptime(created_at, "%Y-%m-%d %H:%M:%S")
    age = (datetime.now() - creation_date).days

    if age <= 5:
        return "Stage 1"
    elif 6 <= age <= 12:
        return "Stage 2"
    elif age >= 13:
        return "Stage 3"
    else:
        return "Unknown"


def send_to_discord(message):
    """
    Sends a message to Discord via a webhook.
    Args:
        message (str): Message content.
    """
    discord_webhook_url = os.getenv("DISCORD_WEBHOOK_URL", "")
    if not discord_webhook_url:
        print("Discord webhook URL not set.")
        return

    data = {'content': message, 'username': 'Notification Bot'}
    try:
        requests.post(discord_webhook_url, json=data)
    except requests.RequestException as e:
        print(f"Failed to send message to Discord: {e}")


def main():
    """
    Main workflow for managing Dolphin profiles and updating Airtable.
    """
    api_key = os.getenv("DOLPHIN_API_KEY", "")
    airtable_pat = os.getenv("AIRTABLE_PAT", "")
    base_id = os.getenv("AIRTABLE_BASE_ID", "")
    table_name = os.getenv("AIRTABLE_TABLE_NAME", "Profiles Badoo")

    if not all([api_key, airtable_pat, base_id, table_name]):
        print("Error: Missing required environment variables.")
        return

    airtable_handler = AirtableHandler(airtable_pat, base_id, table_name)
    dolphin_handler = DolphinAntyHandler(api_key)

    # Fetch profiles from Airtable
    records = airtable_handler.airtable.get_all()
    dolphin_ids = [
        int(record['fields']['Dolphin ID'])
        for record in records
        if 'Dolphin ID' in record['fields'] and
        not any(s in record['fields'].get('Status', []) for s in ['Banned', 'Failed', 'Other'])
    ]

    # Fetch profiles from Dolphin Anty and update stages
    matched_profiles = []
    current_page = 1
    while True:
        response_data = dolphin_handler.fetch_profiles(page=current_page)
        if not response_data:
            break

        profiles = response_data.get('data', [])
        total_pages = response_data.get('last_page', 1)

        for profile in profiles:
            profile_dolphin_id = int(profile['id'])
            if 'Badoo' in profile['tags'] and profile_dolphin_id in dolphin_ids:
                matched_profiles.append({
                    'Dolphin ID': profile_dolphin_id,
                    'Created At': profile.get('created_at')
                })

        if current_page >= total_pages:
            break
        current_page += 1

    for profile in matched_profiles:
        stage = categorize_by_age(profile['Created At'])
        dolphin_id = profile['Dolphin ID']

        # Update Dolphin Anty and Airtable
        status_info = {
            "Stage 1": 7437802,
            "Stage 2": 7437809,
            "Stage 3": 7437811,
            "Unknown": 7910125
        }.get(stage, 7910125)

        dolphin_handler.update_profile_status(dolphin_id, status_info)
        airtable_handler.update_record_status(dolphin_id, stage)

    # Run additional script
    script_path = os.getenv("SCHEDULER_PATH", "")
    if script_path:
        subprocess.call(["python", script_path])


if __name__ == "__main__":
    main()
