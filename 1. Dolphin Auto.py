import requests
import json
import random
import time
import sys

def main():
    """
    Main function to handle the creation of browser profiles based on user inputs.

    Command-line arguments:
    1. model_name (str): Base name for the profile.
    2. user_country (str): User's country.
    3. num_profiles (int): Number of profiles to create.
    """
    try:
        # Parse command-line arguments
        model_name = sys.argv[1]
        user_country = sys.argv[2]
        num_profiles = int(sys.argv[3])

        # Configuration
        api_key = ""  # Replace with your API key
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}"
        }

        # Proxy file selection
        proxy_file_path = select_proxy_file(user_country)
        proxy_list = read_proxies_from_file(proxy_file_path)

        created_profiles = []  # Store created profile names and IDs

        for _ in range(num_profiles):
            attempt_profile_creation(
                model_name, headers, proxy_list, proxy_file_path, created_profiles
            )
            time.sleep(5)  # Avoid hitting API rate limits

        # Save created profiles to a file
        save_created_profiles_to_file(created_profiles)

    except Exception as e:
        print(f"An error occurred: {e}", flush=True)
        send_to_discord(f"Unexpected error: {str(e)}")
        sys.exit(1)

def send_to_discord(message: str):
    """
    Sends a notification to Discord with the given message.
    """
    discord_webhook_url = ""  # Replace with your Discord webhook URL
    payload = {"content": message, "username": "Message Sender"}
    requests.post(discord_webhook_url, json=payload)

def fetch_profiles_with_tag(api_key: str, tag: str):
    """
    Fetches profiles matching a specific tag using the Dolphin Anty API.
    """
    url = "https://dolphin-anty-api.com/browser_profiles"
    params = {"query": tag, "limit": 50, "page": 1}
    headers = {"Authorization": f"Bearer {api_key}"}

    response = requests.get(url, headers=headers, params=params)
    if response.status_code == 200:
        return response.json().get("data", [])
    else:
        error_message = f"Failed to fetch profiles with tag {tag}: {response.text}"
        print(error_message, flush=True)
        send_to_discord(error_message)
        sys.exit(1)

def get_highest_profile_number(profiles: list, model_name: str) -> int:
    """
    Retrieves the highest numeric suffix from profiles with the given model name.
    """
    highest_number = 0
    for profile in profiles:
        name = profile.get("name", "")
        if name.startswith(model_name):
            try:
                number = int(name.split()[-1])
                highest_number = max(highest_number, number)
            except ValueError:
                continue
    return highest_number

def fetch_user_agent(headers: dict, platform: str) -> str:
    """
    Fetches a user agent string for the specified platform.
    """
    user_agent_url = "https://dolphin-anty-api.com/fingerprints/useragent"
    params = {"browser_type": "anty", "browser_version": "latest", "platform": platform}

    response = requests.get(user_agent_url, headers=headers, params=params)
    return response.json().get("data", "Default User Agent String") if response.status_code == 200 else "Default User Agent String"

def fetch_webgl_info(platform: str) -> tuple:
    """
    Fetches WebGL information for the specified platform.
    """
    webgl_url = "https://dolphin-anty-api.com/fingerprints/fingerprint"
    params = {
        "platform": platform,
        "browser_type": "anty",
        "browser_version": "112",
        "type": "fingerprint",
        "screen": "2560x1440"
    }

    response = requests.get(webgl_url, params=params)
    if response.status_code == 200:
        data = response.json()
        webgl_info = data.get("webgl", {})
        return (
            webgl_info.get("unmaskedVendor", "Default Vendor"),
            webgl_info.get("unmaskedRenderer", "Default Renderer"),
            json.loads(data.get("webgl2Maximum", "{}")),
        )
    return "Default Vendor", "Default Renderer", {}

def select_proxy_file(country: str) -> str:
    """
    Returns the appropriate proxy file path based on the user's country.
    """
    if country == "UK":
        return r"path/to/uk_proxies.txt"
    elif country == "USA":
        return r"path/to/usa_proxies.txt"
    else:
        raise ValueError(f"Unsupported country: {country}")

def read_proxies_from_file(file_path: str) -> list:
    """
    Reads proxies from a specified file and returns them as a list.
    """
    with open(file_path, "r") as file:
        return [line.strip() for line in file]

def rewrite_proxy_file(file_path: str, proxies: list):
    """
    Rewrites the proxy file with the remaining proxies.
    """
    with open(file_path, "w") as file:
        file.writelines(f"{proxy}\n" for proxy in proxies)

def attempt_profile_creation(model_name: str, headers: dict, proxy_list: list, proxy_file_path: str, created_profiles: list):
    """
    Attempts to create a new browser profile, retrying up to three times if an error occurs.
    """
    for attempt in range(3):
        try:
            platform = random.choice(["macos", "windows"])
            profiles = fetch_profiles_with_tag(headers["Authorization"], model_name)
            highest_number = get_highest_profile_number(profiles, model_name)
            new_profile_name = f"{model_name} {highest_number + 1}"

            user_agent = fetch_user_agent(headers, platform)
            webgl_vendor, webgl_renderer, webgl2_maximum = fetch_webgl_info(platform)

            proxy = random.choice(proxy_list)
            proxy_list.remove(proxy)
            rewrite_proxy_file(proxy_file_path, proxy_list)

            proxy_config = parse_proxy_configuration(proxy)

            profile_data = generate_profile_data(new_profile_name, platform, user_agent, webgl_vendor, webgl_renderer, webgl2_maximum, proxy_config)
            create_profile(headers, profile_data, created_profiles)
            break

        except Exception as e:
            if attempt == 2:
                error_message = f"Failed to create profile after 3 attempts: {e}"
                print(error_message, flush=True)
                send_to_discord(error_message)

def parse_proxy_configuration(proxy: str) -> dict:
    """
    Parses a proxy string into a dictionary format for profile configuration.
    """
    host, port, login, password = proxy.split(":")
    return {"type": "http", "host": host, "port": port, "login": login, "password": password, "name": "Sticky"}

def generate_profile_data(name: str, platform: str, user_agent: str, webgl_vendor: str, webgl_renderer: str, webgl2_maximum: dict, proxy: dict) -> dict:
    """
    Generates the profile data payload for the API request.
    """
    return {
        "name": name,
        "tags": ["Badoo", platform],
        "platform": platform,
        "useragent": {"mode": "manual", "value": user_agent},
        "proxy": proxy,
        "webgl": {"mode": "manual", "vendor": webgl_vendor, "renderer": webgl_renderer, "webgl2Maximum": webgl2_maximum},
        "browserType": "anty"
    }

def create_profile(headers: dict, profile_data: dict, created_profiles: list):
    """
    Sends a request to create a new browser profile.
    """
    url = "https://dolphin-anty-api.com/browser_profiles"
    response = requests.post(url, headers=headers, json=profile_data)
    response.raise_for_status()

    data = response.json()
    if data.get("success") == 1:
        created_profiles.append((profile_data["name"], data.get("browserProfileId", "Unknown ID")))

def save_created_profiles_to_file(profiles: list):
    """
    Saves created profiles to a file in a structured format.
    """
    with open("created_profiles.txt", "w") as file:
        file.write("profile_names = {\n")
        for name, profile_id in profiles:
            file.write(f"    '{profile_id}': '{name}',\n")
        file.write("}\n")

if __name__ == "__main__":
    main()
