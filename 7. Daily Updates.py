import os
from datetime import datetime
from airtable import Airtable
import requests
from dotenv import load_dotenv

load_dotenv()


class AirtableHandler:
    """Handles interactions with Airtable."""

    def __init__(self, base_id, pat, swipes_table, profiles_table):
        self.swipes_table = Airtable(base_id, swipes_table, pat)
        self.profiles_table = Airtable(base_id, profiles_table, pat)

    def get_all_records(self, table):
        """
        Retrieves all records from the specified table.
        Args:
            table (Airtable): Airtable table instance.
        Returns:
            list: List of records from the Airtable table.
        """
        try:
            return table.get_all()
        except Exception as e:
            self.log_error(f"Error retrieving records from Airtable: {e}")
            return []

    @staticmethod
    def log_error(message):
        print(f"Airtable Error: {message}")
        send_to_discord(f"Airtable Error: {message}")


def process_swipe_records(records, input_date):
    """
    Processes swipe records and calculates aggregated data for a given date.
    Args:
        records (list): List of swipe records.
        input_date (str): Date to filter the records.
    Returns:
        tuple: Processed swipe data, total runs, total swipes, average "no" percentage.
    """
    data = {}
    total_swipes = 0
    total_no_percentage = 0
    count = 0

    for record in records:
        record_date = record['fields'].get('Date Ran', '')
        if record_date == input_date:
            model = record['fields'].get('Model Name', 'Unknown')
            swipes = record['fields'].get('Total Swipes', 0)
            no_percentage = record['fields'].get('No', 0) * 100

            if model not in data:
                data[model] = {'runs': 0, 'swipes': 0}
            data[model]['runs'] += 1
            data[model]['swipes'] += swipes
            total_swipes += swipes
            total_no_percentage += no_percentage
            count += 1

    average_no_percentage = total_no_percentage / count if count else 0
    return data, count, total_swipes, average_no_percentage


def calculate_success_rate(started, finished):
    """
    Calculates the success rate as a percentage.
    Args:
        started (int): Number of profiles that started.
        finished (int): Number of profiles that finished.
    Returns:
        float: Success rate percentage.
    """
    if started > 0:
        return (finished / started) * 100
    return 0


def send_to_discord(message):
    """
    Sends a message to Discord via webhook.
    Args:
        message (str): Message content to be sent.
    """
    discord_webhook_url = os.getenv("DISCORD_WEBHOOK_URL", "")
    if not discord_webhook_url:
        print("Discord webhook URL is not set.")
        return

    try:
        requests.post(discord_webhook_url, json={"content": message})
    except requests.RequestException as e:
        print(f"Error sending message to Discord: {e}")


def main():
    """
    Main workflow to process swipe and profile data, and send results to Discord.
    """
    pat = os.getenv("AIRTABLE_PAT", "")
    base_id = os.getenv("AIRTABLE_BASE_ID", "")
    swipes_table_name = os.getenv("SWIPES_TABLE_NAME", "Completed Runs copy")
    profiles_table_name = os.getenv("PROFILES_TABLE_NAME", "Badoo Profile Daily Tracker")

    if not all([pat, base_id, swipes_table_name, profiles_table_name]):
        print("Error: Missing required environment variables.")
        return

    airtable_handler = AirtableHandler(base_id, pat, swipes_table_name, profiles_table_name)

    today = datetime.now().strftime('%Y-%m-%d')

    # Retrieve swipe records and process data
    swipe_records = airtable_handler.get_all_records(airtable_handler.swipes_table)
    processed_swipe_data, total_runs, total_swipes, average_no_percentage = process_swipe_records(swipe_records, today)

    # Retrieve profile data and calculate metrics
    profile_stage_records = airtable_handler.get_all_records(airtable_handler.profiles_table)
    started = sum(record['fields'].get('Profiles Started', 0) for record in profile_stage_records if record['fields'].get('Date') == today)
    halfway = sum(record['fields'].get('Profiles That Made It Halfway', 0) for record in profile_stage_records if record['fields'].get('Date') == today)
    finished = sum(record['fields'].get('Profiles That Finished', 0) for record in profile_stage_records if record['fields'].get('Date') == today)
    added = sum(record['fields'].get('Profiles Added To Airtable', 0) for record in profile_stage_records if record['fields'].get('Date') == today)
    success_rate = calculate_success_rate(started, finished)

    # Prepare message to send to Discord
    message = f"DATING APP SWIPE AND PROFILE DATA\n\nDate: {today}\n"
    for model, info in processed_swipe_data.items():
        message += f"{model}: {info['runs']} run(s), {info['swipes']} swipe(s)\n"
    message += f"\nOverall number of runs today: {total_runs}\n"
    message += f"Overall number of swipes today: {total_swipes}\n"
    message += f"Average no %: {average_no_percentage:.2f}%\n\n"
    message += "DATING APP PROFILE DATA\n\n"
    message += f"Profiles Started Today: {started}\n"
    message += f"Profiles Made It Halfway Today: {halfway}\n"
    message += f"Profiles Finished Today: {finished}\n"
    message += f"Profiles Added To Airtable Today: {added}\n"
    message += f"Success rate: {success_rate:.2f}%"

    send_to_discord(message)


if __name__ == "__main__":
    main()
