import os
import time
import requests
from airtable import Airtable
import subprocess
from dotenv import load_dotenv

load_dotenv()


class BrowserProfilesHandler:
    """Handles browser profiles operations including fetching, clearing, and updating Airtable records."""

    def __init__(self, airtable_pat, base_id, profiles_table_name, api_key):
        self.profiles_table = Airtable(base_id, profiles_table_name, airtable_pat)
        self.api_base_url = os.getenv("DOLPHIN_API_URL", "https://dolphin-anty-api.com/browser_profiles")
        self.api_key = api_key

    def get_browser_profiles(self, page=1, limit=50, query=None, tags=None, statuses=None, mainWebsites=None, users=None):
        """
        Fetches browser profiles from the Dolphin API.
        Args:
            page (int): Page number for pagination.
            limit (int): Number of profiles per page.
            query (str): Search query.
            tags (list): List of tags to filter.
            statuses (list): List of statuses to filter.
            mainWebsites (list): List of websites to filter.
            users (list): List of users to filter.
        Returns:
            dict: Response from the Dolphin API.
        """
        params = {
            'limit': limit,
            'page': page,
            'query': query,
            'tags[]': tags,
            'statuses[]': statuses,
            'mainWebsites[]': mainWebsites,
            'users[]': users,
        }
        headers = {
            'Authorization': f'Bearer {self.api_key}'
        }
        try:
            response = requests.get(self.api_base_url, params=params, headers=headers)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            raise Exception(f"Failed to fetch browser profiles: {e}")

    def fetch_all_browser_profiles(self):
        """
        Fetches all browser profiles, handling pagination and filtering by tags.
        Returns:
            list: List of all browser profiles with specific tags.
        """
        all_profiles_info = []
        page = 1
        while True:
            try:
                data = self.get_browser_profiles(page=page)
                profiles = data.get('data', [])
                if not profiles:
                    break
                for profile in profiles:
                    if 'Badoo' in profile['tags']:
                        profile_info = {
                            'id': profile.get('id', 'N/A'),
                            'name': profile.get('name', 'N/A'),
                            'status': profile.get('status', {}).get('name', 'N/A'),
                            'proxy': profile.get('proxy', {}).get('name', 'N/A'),
                            'tags': profile.get('tags', [])
                        }
                        all_profiles_info.append(profile_info)
                page += 1
            except Exception as e:
                raise Exception(f"Error while fetching profiles: {e}")
        return all_profiles_info

    def send_profiles_to_airtable(self, profiles_info):
        """
        Sends browser profiles information to Airtable.
        Args:
            profiles_info (list): List of profiles to send to Airtable.
        """
        for info in profiles_info:
            if 'Badoo' in info['tags']:
                name_parts = info['name'].split()
                name = " ".join(name_parts[:-1]) if len(name_parts) > 1 else info['name']
                number = name_parts[-1] if len(name_parts) > 1 else ''

                airtable_data = {
                    'Dolphin ID': int(info['id']),
                    'Dolphin Name': str(info['name']),
                    'Model Name': str(name),
                    'Status': [str(info['status'])],
                    'Tags': [str(tag) for tag in info['tags']],
                    'Proxy Name': str(info['proxy'])
                }
                try:
                    self.profiles_table.insert(airtable_data)
                except Exception as e:
                    raise Exception(f"Failed to send profile to Airtable: {e}")

    def clear_airtable(self):
        """
        Clears all records from the Airtable table.
        """
        try:
            records = self.profiles_table.get_all()
            record_ids = [record['id'] for record in records]
            self.profiles_table.batch_delete(record_ids)
        except Exception as e:
            raise Exception(f"Failed to clear Airtable records: {e}")

    @staticmethod
    def run_change_stage_code(script_path):
        """
        Runs an external script to change stages.
        Args:
            script_path (str): Path to the script.
        """
        try:
            subprocess.call(["python", script_path])
        except Exception as e:
            raise Exception(f"Failed to execute script: {e}")


def send_to_discord(message):
    """
    Sends a message to Discord webhook.
    Args:
        message (str): Message to send.
    """
    discord_webhook_url = os.getenv("DISCORD_WEBHOOK_URL", "")
    if not discord_webhook_url:
        print("Discord webhook URL not set.")
        return
    data = {'content': message, 'username': 'Message Sender'}
    try:
        requests.post(discord_webhook_url, json=data)
    except requests.RequestException as e:
        print(f"Failed to send message to Discord: {e}")


def main():
    """
    Main workflow to handle browser profiles and Airtable operations.
    """
    airtable_pat = os.getenv("AIRTABLE_PAT", "")
    base_id = os.getenv("AIRTABLE_BASE_ID", "")
    profiles_table_name = os.getenv("AIRTABLE_TABLE_NAME", "Profiles Badoo")
    api_key = os.getenv("DOLPHIN_API_KEY", "")

    if not all([airtable_pat, base_id, profiles_table_name, api_key]):
        print("Error: Missing required environment variables.")
        return

    handler = BrowserProfilesHandler(airtable_pat, base_id, profiles_table_name, api_key)

    try:
        # Clear Airtable records
        handler.clear_airtable()

        # Fetch browser profiles and send to Airtable
        profiles_info = handler.fetch_all_browser_profiles()
        handler.send_profiles_to_airtable(profiles_info)

        # Run external stage change script
        script_path = os.getenv("STAGE_CHANGE_SCRIPT_PATH", "path/to/change_stages.py")
        handler.run_change_stage_code(script_path)

    except Exception as e:
        error_message = f"Error during processing: {e}"
        print(error_message)
        send_to_discord(error_message)


if __name__ == "__main__":
    main()
