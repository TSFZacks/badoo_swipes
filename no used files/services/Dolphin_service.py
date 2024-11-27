import requests


class Dolphin_Controller:
    
    @staticmethod
    def stop(API_BASE_URL, PROFILE_ID):
        stop_url = f"{API_BASE_URL}/browser_profiles/{PROFILE_ID}/stop"
        response = requests.get(stop_url)
        data = response.json()
        if not data.get('success'):
            raise Exception("Failed to stop the Dolphin Anty profile.")