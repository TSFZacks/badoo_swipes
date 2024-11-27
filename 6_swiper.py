import os
import json
import re
import time
import random
import logging
import requests
from datetime import datetime
from airtable import Airtable
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from concurrent.futures import ThreadPoolExecutor
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from termcolor import colored, COLORS
from dotenv import load_dotenv


load_dotenv()

PAT = ''
BASE_ID = ''
PROFILES_TABLE_NAME = 'Profiles Badoo'
BANNED_PROFILE_TABLE_NAME = 'Banned Profiles copy'
SCHEDULED_COMPLETE_TABLE_NAME = 'Completed Runs copy'
SCHEDULED_RUNS_TABLE_NAME = 'Scheduled Runs Badoo'

profiles_table = Airtable(BASE_ID, PROFILES_TABLE_NAME, PAT)
scheduled_runs_table = Airtable(BASE_ID, SCHEDULED_RUNS_TABLE_NAME, PAT)
bearer_token = ""
ERROR_COLOR = "red"
DENIED_COLOR = "yellow"
SUCCESSFULLY_COLOR = "green"

swipe_left_js = """
    const e = document.querySelector("#meetmevotebutton-no");
    if (e) {
        e.click();
    }
"""
swipe_right_js = """
    const e = document.querySelector("button[data-qa='profile-card-action-vote-yes']");
    if (e) {
        e.click();
    }
"""

def close_profile(dolphin_prof_id):

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {bearer_token}"
    }

    stop_url = f"http://localhost:3001/v1.0/browser_profiles/{dolphin_prof_id}/stop"
    response = requests.get(stop_url, headers=headers)
    data = response.json()

SIMULATE_DRAG = """
    function simulateMouseEvent(element, eventName, options) {
    var event = new MouseEvent(eventName, options);
    element.dispatchEvent(event);
    }

function autoDragElement(element, targetX, targetY, duration) {
    var rect = element.getBoundingClientRect();
    var startX = rect.left + window.scrollX;
    var startY = rect.top + window.scrollY;
    var startTime = performance.now();

    function step(currentTime) {
        var elapsed = currentTime - startTime;
        var progress = Math.min(elapsed / duration, 1);

        var currentX = startX + (targetX - startX) * progress;
        var currentY = startY + (targetY - startY) * progress;

        simulateMouseEvent(element, 'mousemove', {
            clientX: currentX,
            clientY: currentY,
            bubbles: true
        });

        element.style.left = currentX + 'px';
        element.style.top = currentY + 'px';

        if (progress < 1) {
            requestAnimationFrame(step);
        } else {
            simulateMouseEvent(element, 'mouseup', {
                clientX: currentX,
                clientY: currentY,
                bubbles: true
            });
        }
    }

    simulateMouseEvent(element, 'mousedown', {
        clientX: startX,
        clientY: startY,
        bubbles: true
    });

    requestAnimationFrame(step);
}
const card = document.querySelector("#page-container > div > div > div.csms-screen__block.csms-screen__block--align-stretch > div:nth-child(2)")
autoDragElement(card, 0, card.getBoundingClientRect().top, 500)
"""

def wait_for_element_visible(driver, by, value, timeout=3):
    return WebDriverWait(driver, timeout).until(
        EC.visibility_of_element_located((by, value))
    )

def wait_for_elements(driver, by, value, timeout=3):
    return WebDriverWait(driver, timeout).until(
        EC.presence_of_all_elements_located((by, value))
    )

class ProfileChecker:
    
    def __init__(self, move_to_completed_runs, record_id, dolphin_prof_id, PAT, BASE_ID):

        self.previous_profile_username = None
        self.same_profile_count = 0
        self.move_to_completed_runs = move_to_completed_runs   
        self.record_id = record_id
        self.dolphin_prof_id = dolphin_prof_id
        self.yes_count = 0
        self.no_count = 0
        self.PAT = PAT
        self.BASE_ID = BASE_ID
        
    def get_swipe(self, driver, action):
        return wait_for_elements(driver, By.XPATH,f"//button[@class='profile-action' and @data-qa='profile-card-action-vote-{action}']")[1]
    
    def increment_yes_count(self):
        self.yes_count += 1

    def increment_no_count(self):
        self.no_count += 1

    def attempt_click_no(self, driver):
        try:
            no_button = self.get_swipe(driver,"no")
            no_button.click()
            return True
        except Exception as e:
            return False
    
    def attempt_click_yes(self, driver):
        try:
            no_button = self.get_swipe(driver,"yes")
            no_button.click()
            modal_button_exit = wait_for_element_visible(By.XPATH, "//button[@class='csms-modal__navigation-item csms-modal__navigation-item--end' and @data-qa='modal-close']")
            if modal_button_exit:
                modal_button_exit.click()
            return True
        except Exception as e:
            return False

def have_you_used_dating_apps_before(driver):
    try:
        choice = random.randint(1, 3)
        button = wait_for_element_visible(driver, By.XPATH, f"//button[@class='promo-card__button js-action' and @data-answer-id='{choice}']")
        if button:
            button.click()

    except Exception:
        pass

def get_profile_name(dolphin_prof_id):
    try:
        record = scheduled_runs_table.match('Dolphin ID', dolphin_prof_id)
        if record:
            return record['fields'].get('Dolphin Name')
        else:
            print(f"Badoo Swiper - No profile found for Dolphin ID: {dolphin_prof_id}\n{'-' * 113}", flush=True)
            send_to_discord(f"Badoo Swiper - No profile found for Dolphin ID: {dolphin_prof_id}\n{'-' * 113}")

            return None
    except Exception as e:

        print(f"Badoo Swiper - An error occurred while fetching the profile name: {e}\n{'-' * 113}", flush=True)
        send_to_discord(f"Badoo Swiper - An error occurred while fetching the profile name: {e}\n{'-' * 113}")
        return None

def openstatistics(dolphin_prof_id):
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {bearer_token}"
    }

    close_profile(dolphin_prof_id)

    time.sleep(3)

    try:
        start_url = f"http://localhost:3001/v1.0/browser_profiles/{int(dolphin_prof_id)}/start?automation=1"
        response = requests.get(start_url, headers=headers)
        response.raise_for_status()  

        data = response.json()
        if not data.get('success'):
            error_details = f"Failed to start the Dolphin Anty profile. Response: {data}"
            raise Exception(error_details)

        port = data['automation']['port']
        options = webdriver.ChromeOptions()
        options.add_argument(f'--remote-debugging-port={port}')
        options.add_argument('--user-data-dir=./User_Data')
        debugger_address = f"localhost:{port}"
        options.debugger_address = debugger_address
        executable_path = rf"{os.getenv('EXECUTABLE')}"
        service = Service(executable_path=executable_path)
        driver = webdriver.Chrome(options=options, service=service)
        driver.maximize_window()

        return driver
    
    except requests.RequestException as e:

        print(f"Badoo Swiper - Request error: {e.response.text if e.response else str(e)}\n{'-' * 113}", flush=True)
        dolph_need_refreshing = f"@everyone dolphin needs refreshing: {e}"
        send_to_discord(dolph_need_refreshing)
        raise
    except Exception as e:
        print(f"Badoo Swiper - Error in function openstatistics: {e}\n{'-' * 113}", flush=True)
        send_to_discord(f"Badoo Swiper - Error in function openstatistics: {e}\n{'-' * 113}")
        raise
    
def send_to_discord(message):
    url = ''  
    data = {
        'content': message,
        'username': 'Message Sender'
    }
    requests.post(url, data=json.dumps(data), headers={"Content-Type": "application/json"})

def check_if_banned_or_other_issues(driver, dolphin_prof):
    try:

        try:

            wait_for_element_visible(driver, By.XPATH, '//button[@data-qa="phone-login"]')
            check_login = True

        except Exception:

            check_login = None

        if 'https://badoo.com/en-us/landing' in driver.current_url or check_login:
            return 'Banned'
        banned_text = "//h1[text()='Account blocked']"
        h1_verify_text = "//div[text()='Verify your profile']"
        h1_banned_text = wait_for_element_visible(driver, By.XPATH, banned_text)
        h1_verify_text_component = wait_for_element_visible(driver, By.XPATH, h1_verify_text)
        if h1_banned_text or h1_verify_text_component:
            print(f"Badoo Swiper - {dolphin_prof} ACCOUNT HAS BEEN BANNED\n{'-' * 113}", flush=True)
            send_to_discord(f"Badoo Swiper - {dolphin_prof} ACCOUNT HAS BEEN BANNED\n{'-' * 113}")
            return "banned"
        return False
    except Exception as e:
        return False

def set_all_runs_to_banned(dolphin_prof_id):
    all_records = scheduled_runs_table.get_all()
    filtered_records = [record for record in all_records if record['fields'].get('Dolphin ID') == dolphin_prof_id]
    for record in filtered_records:
        record_id = record['id']
        scheduled_runs_table.update(record_id, {'Running Progress': ['Banned Account']})
        
def start_profile(dolphin_prof_id, profile_name, bearer_token):
    
    driver = None
    status = "Unknown"  
    expected_url = "https://badoo.com/en-us/encounters"
    stop_url = f"http://localhost:3001/v1.0/browser_profiles/{int(dolphin_prof_id)}/stop"

    try:
        driver = openstatistics(dolphin_prof_id)
        driver.get(expected_url)
        time.sleep(5)

        return driver
        
    except Exception as e:

        print(f"Badoo Swiper - Error with profile {profile_name}: {str(e)}\n{'-' * 113}", flush=True)
        send_to_discord(f"Badoo Swiper - Error with profile {profile_name}: {str(e)}\n{'-' * 113}")
        if driver:
            response = requests.get(stop_url)  
            data = response.json() 
            
            if not data.get('success'):
                raise Exception("Failed to close the Dolphin Anty profile.") 
        return None
    
def update_airtable_and_finish(status, dolphin_prof_id, profile_name, driver):
    scheduled_runs_table = Airtable(BASE_ID, SCHEDULED_RUNS_TABLE_NAME, PAT, 2)
    if "banned" in status.lower():
        record = scheduled_runs_table.match('Dolphin ID', dolphin_prof_id)
        if record:
            status_update = {'Status': ['Banned']}
            scheduled_runs_table.update(record['id'], status_update)
            set_all_runs_to_banned(dolphin_prof_id)
        
    if "banned" in status.lower():
        if find_and_move_record_in_airtable(dolphin_prof_id, PAT, BASE_ID, driver):
            url = f"https://dolphin-anty-api.com/browser_profiles/{dolphin_prof_id}?forceDelete=1"
            headers = {'Authorization': f'Bearer {bearer_token}'}
            response = requests.delete(url, headers=headers)
            
            if response.status_code == 200:
                pass
            else:

                print(f"Badoo Swiper - Failed to delete profile in Dolphin Anty. Status code: {response.status_code}\n{'-' * 113}", flush=True)
                send_to_discord(f"Badoo Swiper - Failed to delete profile in Dolphin Anty. Status code: {response.status_code}\n{'-' * 113}")
        else:

            print(f"Badoo Swiper - No matching record found in Airtable. Profile not deleted in Dolphin Anty.\n{'-' * 113}", flush=True)
            send_to_discord(f"Badoo Swiper - No matching record found in Airtable. Profile not deleted in Dolphin Anty.\n{'-' * 113}")
            stop_url = f"http://localhost:3001/v1.0/browser_profiles/{dolphin_prof_id}/stop"
            response = requests.get(stop_url)  
        
def find_and_move_record_in_airtable(dolphin_prof_id, PAT, BASE_ID, driver=None):
    existing_table = Airtable(BASE_ID, PROFILES_TABLE_NAME, PAT)
    deleted_profiles_table = Airtable(BASE_ID, BANNED_PROFILE_TABLE_NAME, PAT)

    matching_records = existing_table.search('Dolphin ID', dolphin_prof_id)

    if matching_records:
        record = matching_records[0]
        record_data = record['fields']

        try:
            response = deleted_profiles_table.insert(record_data)
            existing_table.delete(record['id'])

            stop_url = f"http://localhost:3001/v1.0/browser_profiles/{dolphin_prof_id}/stop"
            response = requests.get(stop_url)
            data = response.json()

            if not data.get('success'):
                if driver:
                    close_profile(dolphin_prof_id)

            return True
        except Exception as e:

            print(f"Badoo Swiper - Error inserting record into Banned Profiles or closing Dolphin Anty profile: {str(e)}\n{'-' * 113}", flush=True)
            send_to_discord(f"Badoo Swiper - Error inserting record into Banned Profiles or closing Dolphin Anty profile: {str(e)}\n{'-' * 113}")
            return False

    return False

def pick_and_update_scheduled_run():
    filter_formula = "{Running Progress}='Scheduled'"
    try:
        scheduled_records = scheduled_runs_table.get_all(formula=filter_formula)
        if not scheduled_records:

            print(f"Badoo Swiper - Error inserting record into Banned Profiles or closing Dolphin Anty profile: {str(e)}\n{'-' * 113}", flush=True)
            send_to_discord(f"Badoo Swiper - Error inserting record into Banned Profiles or closing Dolphin Anty profile: {str(e)}\n{'-' * 113}")
            return None, None
        selected_record = random.choice(scheduled_records)
        record_id = selected_record['id']
        dolphin_prof_id = selected_record['fields'].get('Dolphin ID')
        swipe_amount = selected_record['fields'].get('Swipe Amount')
        current_time = int(datetime.now().strftime('%H%M'))
        scheduled_runs_table.update(record_id, {
            'Running Progress': ["Initiating"],  
            'Time Initiated': current_time  
        })
        return record_id, dolphin_prof_id, swipe_amount
    except Exception as e:

        print(f"Badoo Swiper - Error in function pick_and_update_scheduled_run: {e}\n{'-' * 113}", flush=True)
        send_to_discord(f"Badoo Swiper - Error in function pick_and_update_scheduled_run: {e}\n{'-' * 113}")
        return None, None

def check_promo(driver):
    try:
        
        premium_xpath = "//button[@class='csms-button csms-button--semantic-primary csms-button--styling-inverse csms-button--medium js-touchable qa-button' and @data-qa='promo-card-cta']//span[@class='csms-button__text csms-text-break-words' and contains(text(), 'Get Premium')]"
        premium_button = driver.find_element(By.XPATH, premium_xpath)
        if premium_button:
            driver.execute_script(SIMULATE_DRAG)
    except Exception as e:
        return None


def no_more_likes(driver):
    try:
        xpath = "//div[contains(@class, 'csms-header-1') and contains(@class, 'csms-text-break-words')]"
        no_more_likes_text = driver.find_element(By.XPATH, xpath)
        if no_more_likes_text:

            return True
        else:
            return False
    except Exception as e:
        return False
    
def its_match_skip(driver):
    try:
        xpath = '//span[text()="It’s a match!"]'
        its_match = driver.find_element(By.XPATH, xpath)
        if its_match:
            x_path_skip_button = "//button[@class='csms-navigation-bar__icon' and @data-qa='navbar-icon' and @data-qa-icon='navigation-bar-close']"
            driver.find_element(By.XPATH, x_path_skip_button).click()
    except Exception as e:
        return None

def perform_swipes(record_id, driver, total_swipes, left_swipe_percentage, dolphin_prof_id, dolphin_prof):
    
    wait_time_between_swipes = random.randint(3, 9)
    left_swipes_count = int((left_swipe_percentage / 100) * total_swipes)
    right_swipes_count = total_swipes - left_swipes_count
    swipe_actions = ['left'] * left_swipes_count + ['right'] * right_swipes_count
    random.shuffle(swipe_actions)
    checker = ProfileChecker(move_to_completed_runs, record_id, dolphin_prof_id, PAT, BASE_ID)
    soldoff = False
    status = ""
    
    for action in swipe_actions:

        time.sleep(3)

        try:

            wait_for_element_visible(driver, By.XPATH, '//button[@data-qa-icon="navigation-bar-close"]').click()

        except Exception:

            pass

        try:
            wait_for_element_visible(driver, By.XPATH, "//button[.//span[text()='Later']]").click()
        except Exception:
            pass
        try:
            wait_for_element_visible(driver, By.XPATH, "//button[.//span[contains(@class, 'csms-button__text') and text() = 'No, thanks']]").click()
        except Exception:
            pass
        try:
            wait_for_element_visible(driver, By.XPATH, '//button[@data-qa="modal-close"]').click()
        except Exception:
            pass

        try:

            driver.find_element(By.XPATH, '//button[@data-qa="action-sheet-item"]').click()
        except Exception:
            pass
        try:
            driver.find_element(By.XPATH, '//button[@class="csms-modal__navigation-item csms-modal__navigation-item--end"]').click()
        except Exception:
            pass
        time.sleep(3)
        have_you_used_dating_apps_before(driver)
        status = check_if_banned_or_other_issues(driver, dolphin_prof)
        if soldoff:
            break
        if status:
            update_airtable_and_finish(status, dolphin_prof_id, dolphin_prof, driver)
            return
        check_promo(driver)
        try:
            wait_for_element_visible(driver, By.XPATH, "//*[text()='Verify your profile']")
            return
        except Exception:
            pass
        if action == 'left':
            checker.attempt_click_no(driver)
            checker.increment_no_count()
        else:
            checker.attempt_click_yes(driver)
            #driver.execute_script(swipe_right_js)
            checker.increment_yes_count()    
        soldoff = no_more_likes(driver)
        time.sleep(wait_time_between_swipes)

    close_profile(dolphin_prof_id)
    return checker

def move_to_completed_runs(record_id, yes_count, no_count, dolphin_prof_id, PAT, BASE_ID):
    time.sleep(2)
    try:
        scheduled_runs_table = Airtable(BASE_ID, SCHEDULED_RUNS_TABLE_NAME, PAT)
        time.sleep(2)
        record = scheduled_runs_table.get(record_id)
        if record:
            completed_run_data = {
                'Model Name': record['fields'].get('Model Name'),
                'Dolphin Name': record['fields'].get('Dolphin Name'),
                'Dolphin ID': dolphin_prof_id,
                'Date Ran': datetime.now().strftime('%Y-%m-%d'),
                'Start': record['fields'].get('Time Initiated'),
                'End': int(datetime.now().strftime('%H%M')), 
                'Total Swipes': yes_count + no_count,
                'No': (no_count / (yes_count + no_count)) * 1000 if yes_count + no_count > 0 else 0,  
                'Running Progress': ['Completed'],
            }
            try:
                # Insert into completed runs table
                completed_runs_table = Airtable(BASE_ID, SCHEDULED_COMPLETE_TABLE_NAME, PAT)
                insert_response = completed_runs_table.insert(completed_run_data)

            except Exception as e:

                print(f"Badoo Swiper - Error in function pick_and_update_scheduled_run: {e}\n{'-' * 113}", flush=True)
                send_to_discord(f"Badoo Swiper - Error in function pick_and_update_scheduled_run: {e}\n{'-' * 113}")
            try:
                # Delete from scheduled runs table
                scheduled_runs_table.delete(record_id)

            except Exception as e:

                print(f"Badoo Swiper - Error deleting record from Scheduled Runs: {e}\n{'-' * 113}", flush=True)
                send_to_discord(f"Badoo Swiper - Error deleting record from Scheduled Runs: {e}\n{'-' * 113}")
        else:

            print(f"Badoo Swiper - Record not found in Scheduled Runs: {record_id}\n{'-' * 113}", flush=True)
            send_to_discord(f"Badoo Swiper - Record not found in Scheduled Runs: {record_id}\n{'-' * 113}")
    except Exception as e:

        print(f"Badoo Swiper - Error retrieving record from Scheduled Runs: {e}\n{'-' * 113}", flush=True)
        send_to_discord(f"Badoo Swiper - Error retrieving record from Scheduled Runs: {e}\n{'-' * 113}")

    send_to_discord(f"@everyone {record['fields'].get('Dolphin Name')}: COMPLETE✅ Swipes = {yes_count + no_count}.")

def add_insta_tag(dolphin_id, bearer_token):
    get_url = f"https://dolphin-anty-api.com/browser_profiles/{dolphin_id}"
    headers = {
        "Authorization": f"Bearer {bearer_token}"
    }

    try:
        get_response = requests.get(get_url, headers=headers)
        if get_response.status_code == 200:
            current_tags = get_response.json()['data'].get('tags', [])
            if 'Insta' not in current_tags:
                current_tags.append('Insta')  
            else:
                return
        else:
            print(f"POF Swipe App - Failed to fetch tags for Dolphin ID {dolphin_id}, Status Code: {get_response.status_code}\n{'-' * 113}", flush=True)
            return
    except Exception as e:
        print(f"POF Swipe App - Error fetching tags for Dolphin ID {dolphin_id}: {e}\n{'-' * 113}", flush=True)
        return

    patch_url = f"https://dolphin-anty-api.com/browser_profiles/{dolphin_id}"
    patch_headers = {
        "Authorization": f"Bearer {bearer_token}",
        "Content-Type": "application/x-www-form-urlencoded"
    }
    patch_data = {
        'tags[]': current_tags
    }

    try:
        patch_response = requests.patch(patch_url, headers=patch_headers, data=patch_data)
    except Exception as e:
        print(f"POF Swipe App - Error adding 'Insta' tag for Dolphin ID {dolphin_id}: {e}\n{'-' * 113}", flush=True)

def add_instagram(dolphin_prof_id, model_name, INSTAGRAM_TABLE_NAME, PAT, BASE_ID, bearer_token, driver):
    add_instagram_table = Airtable(BASE_ID, INSTAGRAM_TABLE_NAME, PAT)

    try:
        matches = add_instagram_table.search('Dolphin ID', dolphin_prof_id)

        if not matches:
            driver.get("https://am1.badoo.com/en-us/encounters")        
            return False

        record_id = matches[0]['id']

        random_wait_time = random.uniform(3, 7)

        try:
            wait = WebDriverWait(driver, 10)

            driver.get("https://am1.badoo.com/en-us/profile-quality/15")  
            time.sleep(random_wait_time)

            file_name = f"{model_name.lower()}_insta_box.txt"
            insta_box_file_path = os.path.join(r'', file_name)
            
            with open(insta_box_file_path, 'r', encoding='utf-8') as file:
                insta_boxs = file.readlines()

            chosen_insta_box = random.choice(insta_boxs).strip()

            insta_box = wait.until(EC.presence_of_element_located((By.XPATH, "//textarea")))

            time.sleep(random_wait_time)  
            insta_box.click()  
            insta_box.send_keys(Keys.END)  
            time.sleep(0.5) 
            insta_box.send_keys(Keys.ENTER, Keys.ENTER)
            insta_box.send_keys(f'Check my instagram: {chosen_insta_box}')

            try:

                driver.find_element(By.XPATH, '//button[@data-qa="profile-quality-done"]').click()
            except Exception:
                pass
            time.sleep(3)

            skip_list = wait_for_elements(driver, By.XPATH, '//button[@class="csms-pagination-bar__action"]')

            if len(skip_list) == 1:

                skip_list[0].click()

            else:

                skip_list[1].click()

            driver.get("https://www.pof.com/meetme")
            
            time.sleep(2)
                        
            add_insta_tag(dolphin_prof_id, bearer_token)

            add_instagram_table.delete(record_id)
            return True  

        except Exception as e:
            print(f"POF Swipe App - An error occurred during adding Instagram to profile {dolphin_prof_id}: {e}\n{'-' * 113}", flush=True)
            driver.get("https://www.pof.com/meetme")        
            return False

    except Exception as e:
        print(f"POF Swipe App - An error occurred while accessing Airtable: {e}\n{'-' * 113}", flush=True)
        return False

def Main_func_g(record_id, dolphin_prof_id, swipe_amount, driver, profile_name):
    try:
        if driver:

            time.sleep(2)
            status = check_if_banned_or_other_issues(driver, profile_name)
            if status:
                update_airtable_and_finish(status, dolphin_prof_id, profile_name, driver)
                return
            check_not_shadow_ban = is_shadow_banned(driver, dolphin_prof_id, profile_name)

            if check_not_shadow_ban:
                model_name = profile_name.split(' ')[0]
                add_instagram(dolphin_prof_id, model_name, 'Badoo Instagram Scheduler', PAT, BASE_ID, bearer_token, driver)
                total_swipes = swipe_amount
                left_swipe_percentage = random.randint(40, 60)

                checker = perform_swipes(record_id, driver, total_swipes, left_swipe_percentage, dolphin_prof_id, profile_name)
                if not checker:
                    print(f"Badoo Swiper - Verification needed to keep swiping, finishing...\n{'-' * 113}", flush=True)
                    send_to_discord(f"Badoo Swiper - Verification needed to keep swiping, finishing...\n{'-' * 113}")

                    close_profile(dolphin_prof_id)
                    return
                yes_count = checker.yes_count
                no_count = checker.no_count
                move_to_completed_runs(record_id, yes_count, no_count, dolphin_prof_id, PAT, BASE_ID)

        else:

            print(f"Badoo Swiper - Driver failed to initialize.\n{'-' * 113}", flush=True)
            send_to_discord(f"Badoo Swiper - Driver failed to initialize.\n{'-' * 113}")
    except Exception as e:
        print(f"Badoo Swiper - Error in function Main_func_g: {e}\n{'-' * 113}", flush=True)
        send_to_discord(f"Badoo Swiper - Error in function Main_func_g: {e}\n{'-' * 113}")

def find_matching_runs():
    matches = []
    try:
        scheduled_records = scheduled_runs_table.get_all()
        current_time = datetime.now().strftime('%H%M')
        current_date = datetime.now().strftime('%Y-%m-%d')
        for record in scheduled_records:
            time_to_run = record['fields'].get('Time To Run')
            date_to_run = record['fields'].get('Date To Run')
            running_progress = record['fields'].get('Running Progress', [])
            
            # Check if the record is scheduled to run at the current time and date, and if 'Scheduled' is in the Running Progress list
            if time_to_run and date_to_run and int(time_to_run) == int(current_time) and date_to_run == current_date and "Scheduled" in running_progress:
                record_id = record['id']
                # Update the Running Progress to 'Initiating'
                scheduled_runs_table.update(record_id, {'Running Progress': ['Initiating']})
                matches.append(record)

    except Exception as e:

        print(f"Badoo Swiper - Error in function find_matching_runs: {e}\n{'-' * 113}", flush=True)
        send_to_discord(f"Badoo Swiper - Error in function find_matching_runs: {e}\n{'-' * 113}")
    return matches

def is_shadow_banned(driver, dolphin_prof_id, profile_name):
    try:
        completed_runs = Airtable(BASE_ID, SCHEDULED_COMPLETE_TABLE_NAME, PAT)
        driver.get("https://badoo.com/en-us/connections")
        time.sleep(4)
        try:
            all_completed_runs = completed_runs.get_all()
            filtered_records = [record for record in all_completed_runs if record['fields'].get('Dolphin ID') == dolphin_prof_id]
        except Exception:
            filtered_records = []
        sum = 0
        
        for record in filtered_records:
            if record.get("Total Swipes"):
                sum += int(record.get("Total Swipes"))
        if sum >= 100:
            element = wait_for_element_visible(driver, By.XPATH, "//span[contains(@class, 'csms-header-4') and contains(@class, 'csms-text-color-black') and @style='display: block;']")
            span_text = element.text
            match = re.search(r'\d+', span_text)
            if match:

                return True
                
            else:
                print(f"Badoo Swiper - Account with name {profile_name} is shadow banned.\n{'-' * 113}", flush=True)
                send_to_discord(f"Badoo Swiper - Account with name {profile_name} is shadow banned.\n{'-' * 113}")
                set_all_runs_to_banned(dolphin_prof_id)
                close_profile(dolphin_prof_id)
                return False
            
        else:

            return True
            
    except Exception as e:
        return True

def initiate_profile_run(record):
    try:
        record_id = record['id']
        dolphin_prof_id = record['fields'].get('Dolphin ID')
        swipe_amount = record['fields'].get('Swipe Amount')
        
        if dolphin_prof_id and swipe_amount:
            profile_name = get_profile_name(dolphin_prof_id)
            driver = start_profile(dolphin_prof_id, profile_name, bearer_token)
            if driver:
                Main_func_g(record_id, dolphin_prof_id, swipe_amount, driver, profile_name)
            else:

                close_profile(dolphin_prof_id)

        else:

            print(f"Badoo Swiper - Dolphin Profile ID or Swipe Amount not available for record {record_id}.\n{'-' * 113}", flush=True)
            send_to_discord(f"Badoo Swiper - Dolphin Profile ID or Swipe Amount not available for record {record_id}.\n{'-' * 113}")
    except Exception as e:

        print(f"Badoo Swiper - Error in initiating profile run: {e}.\n{'-' * 113}", flush=True)
        send_to_discord(f"Badoo Swiper - Error in initiating profile run: {e}.\n{'-' * 113}")

def continuous_check_and_run():
    with ThreadPoolExecutor(max_workers=30) as executor:
        while True:
            matches = find_matching_runs()
            for record in matches:
                executor.submit(initiate_profile_run, record)
            time.sleep(15)  

if __name__ == "__main__":
    continuous_check_and_run()