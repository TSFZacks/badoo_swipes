from threading import Thread, Event, Lock
import time
import json
import re
import random
import uuid
import requests
import ast
from termcolor import colored
from selenium import webdriver
from pynput.keyboard import Key, Controller
from selenium.webdriver.common.by import By
from concurrent.futures import ThreadPoolExecutor
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, ElementClickInterceptedException, NoSuchElementException, StaleElementReferenceException
from PIL import ImageEnhance, Image
import shutil
import os
from dotenv import load_dotenv
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys

load_dotenv()



temp_tag = 'UK'

ERROR_COLOR = "red"
COUNTRY = "England"
DONE_COLOR = "green"
country_p = rf"{os.getenv('COUNTRY_PATH')}"
COUNTRY_PATH = rf"{country_p}\{COUNTRY}\england_cities.TXT"
PHOTO_PATH = rf"{os.getenv('PHOTO_PATH')}"
PATH_NAMES= rf"{os.getenv('PATH_NAMES')}"

json_path = r"created_profiles.txt"
model_database = {
    'Chloe': {
    },  
    'Carla': {
    },
    'Emma': {
    },
    'Maddie':{''
    },
    'Laurie': {
    },
}

class PhotoServices:
    
    
    def __init__(self, PATH : str):
        self.PATH = PATH
    
    def adjust_brightness(self, image_path, brightness, save_directory):
        img = Image.open(image_path)
        enhancer = ImageEnhance.Brightness(img)
        adjusted_img = enhancer.enhance(1 + brightness)

        if not os.path.exists(save_directory):
            os.makedirs(save_directory)

        file_name = os.path.basename(image_path)
        save_path = os.path.join(save_directory, file_name)

        adjusted_img.save(save_path)

        os.remove(image_path)
        
    def adjust_brightness_directory(self, directory, brightness, save_directory):
        for filename in os.listdir(directory):
            if filename.lower().endswith((".jpg", ".png", ".jpeg")):
                image_path = os.path.join(directory, filename)
                self.adjust_brightness(image_path, brightness, save_directory)
                
    def process_images_for_editing(self, model_name):
        directory = rf"{self.PATH}"
        brightness = -0.075

        save_directory = os.path.join(directory, model_name, "Finished Photos")
        model_directory = os.path.join(directory, model_name, "Photos For Editing")
        self.adjust_brightness_directory(model_directory, brightness, save_directory)
        
    def move_photo_to_editing(self, selected_photo_path, model_name, attempt=1, max_attempts=2):

        editing_path = os.path.join(rf"{self.PATH}\{model_name.capitalize()}\Photos For Editing", os.path.basename(selected_photo_path))
        try:
            shutil.move(selected_photo_path, editing_path)

        except Exception as e:

            if attempt < max_attempts:

                time.sleep(5)  
                self.move_photo_to_editing(selected_photo_path, model_name, attempt + 1, max_attempts)    

class SMS_SENDER:
    
    _API_KEY = ""
    _SERVICE_NAME = 'Badoo'
    _COUNTRY_CODE = 2
    _PRICING_OPTION = 0
    _ORDER_SMS_URL = "https://api.smspool.net/purchase/sms"
    _CHECK_SMS_URL = "https://api.smspool.net/sms/check"
    _CHECK_SMS_URL_CANCEL = "https://api.smspool.net/sms/cancel"

    @staticmethod
    def order_sms():
        params = {
            "key": SMS_SENDER._API_KEY,
            "country": SMS_SENDER._COUNTRY_CODE,
            "service": SMS_SENDER._SERVICE_NAME,
            "pricing_option": SMS_SENDER._PRICING_OPTION
        }
        try:
            response = requests.post(SMS_SENDER._ORDER_SMS_URL, params=params)
        
            return response.json()
        except Exception as e:

            print(f"Badoo Acc Maker - Insufficient funds or another error with the SMS pool: {e}\n{'-' * 113}", flush=True)
            send_to_discord(f"Badoo Acc Maker - Insufficient funds or another error with the SMS pool: {e}\n{'-' * 113}")

            return None
        
    @staticmethod
    def cancel_sms(order_id):
        params = {
            "key": SMS_SENDER._API_KEY,
            "orderid": order_id
        }
        try:
            response = requests.post(SMS_SENDER._CHECK_SMS_URL_CANCEL, params=params)

            return response.json()
        except Exception as e:
            return None
        
    @staticmethod
    def check_sms(order_id):
        params = {
            "key": SMS_SENDER._API_KEY,
            "orderid": order_id
        }
        try:
            response = requests.post(SMS_SENDER._CHECK_SMS_URL, params=params)
            return response.json()
        except Exception as e:
            print(f"Badoo Acc Maker - Error decoding JSON response: {e}\n{'-' * 113}", flush=True)
            send_to_discord(f"Badoo Acc Maker - Error decoding JSON response: {e}\n{'-' * 113}")

            return None
        
class BadooServices:

    random_wait_time = 1
    take_a_photo_xpath = "//button[@class='csms-action-row' and @type='button' and @data-qa='action-sheet-item' and @data-qa-type='generic' and @data-qa-provider='gallery']"
    add_photo_xpath = "//button[@class='multimedia multimedia--background-primary-lighten' and @data-qa='registration-add-photos__cta']"
    PATH_UNIVERSITY = r""
    INTERESTS_PATH = r""
    TALK_ABOUT_PATH = r""
    _data = {}
    _current_path = -1
    PHOTO_PATH = os.getenv('PHOTO_PATH')
    
    @staticmethod
    def Create_An_Account(driver, password, profile_name, model_name, day, randomInt, COUNTRY_PATH, get_swipe, DONE_COLOR, lock, final_event, profile_id):
        BadooServices.SetGenderAndBirthday(profile_name, driver, model_name)
        number_sleep = random.randint(10, 15)
        time.sleep(number_sleep)
        BadooServices.ChoosePhotos(model_name, driver, model_name,lock, final_event)
        number_sleep = random.randint(10, 15)
        time.sleep(number_sleep)
        time.sleep(number_sleep)   
        BadooServices._your_are_here(driver)
        number_sleep = random.randint(10, 15)
        time.sleep(number_sleep)

        element_list=wait_for_elements(driver, By.XPATH, '//div[@data-qa="csms-stack-item"]')
        element_list[0].click()

        number_sleep = random.randint(10, 15)
        time.sleep(number_sleep)
        try:
            element_check = wait_for_element_visible(driver, By.XPATH, "//*[text()=' It might have been removed or be under repairs, try checking back later ']")
            raise
        except Exception:
            element_check = None

        if not element_check:

            count_raise = 0

            while True:
                number_sleep = random.randint(5, 7)
                time.sleep(number_sleep)
                if BadooServices._current_path != 16:
                    try:
                        BadooServices._quiz(url=driver.current_url, driver=driver, profile=model_name,day=day, month=randomInt)
                    except Exception as e:
                        try:

                            BadooServices._quiz(day=day, driver=driver, month=randomInt, profile=model_name, url=driver.current_url)
                        except Exception:
                            count_raise+=1 
                else:
                    break
                time.sleep(3)
                try:

                    driver.find_element(By.XPATH, '//button[@data-qa="profile-quality-done"]').click()
                except Exception:
                    pass
                time.sleep(3)
                try:

                    skip_list = wait_for_elements(driver, By.XPATH, '//button[@class="csms-pagination-bar__action"]')

                    if len(skip_list) == 1:

                        skip_list[0].click()

                    else:

                        skip_list[1].click()

                except Exception as e:
                    count_raise+=1

            time.sleep(10)

            try:

                wait_for_element_visible(driver, By.XPATH, '//button[@data-qa-icon="navigation-bar-close"]').click()

            except Exception as e:
                count_raise+=1

            if count_raise == 3:

                print(f"Badoo Acc Maker - Error making the quiz after 3 attempts\n{'-' * 113}", flush=True)
                send_to_discord(f"Badoo Acc Maker - Error making the quiz after 3 attempts\n{'-' * 113}")
                raise

        else:

            print(f"Badoo Account Maker - Quiz button failed.\n{'-' * 113}", flush=True)
            return None

        time.sleep(3)
        driver.refresh()
        time.sleep(10)
        number_sleep = random.randint(4, 7)
        time.sleep(number_sleep)
        number_sleep = random.randint(4, 6)
        time.sleep(number_sleep)
        unis = ['Cardiff', 'London']
        choose = random.choice(unis).strip()
        i = 0

        while True:
            time.sleep(3)
            local_input = wait_for_element_visible(driver, By.XPATH, "//input[@name='location']")
            actions = ActionChains(driver)

            actions.move_to_element(local_input).click().perform()
            actions.move_to_element(local_input).click().perform()
            actions.move_to_element(local_input).click().perform()
            time.sleep(1)
            actions.click(local_input).send_keys(Keys.BACKSPACE).perform()
            local_input.send_keys(f'{choose}')
            time.sleep(3)
            try:
                list_elements = wait_for_elements(driver, By.XPATH, "//li[@data-qa='suggested-location']")     
                random.shuffle(list_elements)
                list_elements[0].click()
                break
            except Exception:
                choose = random.choice(unis).strip()
                continue
        time.sleep(2)
        next = wait_for_element_visible(driver, By.XPATH, '//button[@data-qa="continue-button"]')
        next.click()
        time.sleep(5)
        try:

            check_inapropriated = wait_for_element_visible(driver, By.XPATH, "//div[text()='Inappropriate photo']")
            driver.back()
        except Exception:
            check_inapropriated = None
        number_sleep = random.randint(10, 15)
        time.sleep(number_sleep)

        count_then_swipes = 0

        count_except = 0

        while True:

            try:

                element = wait_for_elements(driver, By.XPATH, '//button[@data-qa="profile-card-action-vote-yes"]')

                element[1].click()
                count_then_swipes+=1

                if count_then_swipes == 10:
                    close_profile(profile_id)

                    return True

                time.sleep(3)
                try:

                    wait_for_element_visible(driver, By.XPATH, '//button[@data-qa="action-sheet-item"]').click()
                except Exception as e:

                    pass
            except Exception as e:
                count_except+=1

                try:

                    wait_for_element_visible(driver, By.XPATH, '//button[@class="csms-modal__navigation-item csms-modal__navigation-item--end"]').click()

                except Exception as e:

                    pass

                if count_except == 5:

                    return True
    
    @staticmethod
    def Login(email, driver):
        try:
            wait_for_element_visible(driver, By.XPATH, "//button[contains(., 'Continue with Google')]").click()
            time.sleep(20)
            principle_page = driver.current_window_handle

            for window_handle in driver.window_handles:
                if window_handle != principle_page:
                    driver.switch_to.window(window_handle)
                    break
            wait_for_element_visible(driver, By.XPATH, f"//li[.//div[@class='yAlK0b' and @data-email='{email}@gmail.com").click()
            wait_for_element_visible(driver, By.XPATH, "//button[contains(span[@class='VfPpkd-vQzf8d'], 'Continue')]").click()
            driver.switch_to.window(principle_page)

        except Exception as e:
            pass
        time.sleep(20)
    
    @staticmethod
    def _job(driver):
        random_job_indices = random.randint(0, 50)
        job_container = wait_for_element_visible(driver, By.XPATH, "//input[@class='csms-text-field__input csms-text-field__input--text' and @data-qa='text-field-input']")
        time.sleep(20)
        job_container.click()
        job_title = f'*//li[@class="csms-listbox__item"][{random_job_indices}]/div[@class="csms-listbox__item-text"]/span'
        job_chosen = wait_for_element_visible(driver, By.XPATH, job_title)
        job_name = job_chosen.get_attribute('innerHTML')
        job_container.send_keys(job_name)
        job_chosen = wait_for_element_visible(driver, By.XPATH, '*//div[@class="csms-listbox"][1]')
        job_chosen.click()
        enterprise_name = wait_for_element_visible(driver, By.XPATH, "//div[@data-qa='pqw-company-name']//input[@type='text']")
        final_name = job_name + " Company"
        enterprise_name.send_keys(final_name)
        BadooServices._data["Occupation"] = job_name
    
    @staticmethod
    def SetGenderAndBirthday(profile, driver, name):
        signup_name = "//input[@id='signup-name']"
        number_sleep = random.randint(10, 15)
        time.sleep(number_sleep)
        wait_for_element_visible(driver, By.XPATH, "//label[@data-qa-gender='female']").click()
        wait_for_element_visible(driver, By.XPATH, signup_name).send_keys(f'Laurie')
        
        _day = random.randint(1, 28)
        _month = random.randint(1, 12)
        month = f"{_month:02d}"
        day = f"{_day:02d}"
        year = random.randint(1996, 2002)
        number_sleep = random.randint(2, 3)
        time.sleep(number_sleep)

        wait_for_element_visible(driver, By.XPATH, '//*[@id="signup-dob"]').click()
        wait_for_element_visible(driver, By.XPATH, '//*[@id="signup-dob"]').send_keys(f'{day}')
        number_sleep = random.randint(1, 2)
        time.sleep(number_sleep)
        wait_for_element_visible(driver, By.XPATH, '//*[@id="signup-dob"]').send_keys(f'{month}')
        number_sleep = random.randint(1, 2)
        time.sleep(number_sleep)
        wait_for_element_visible(driver, By.XPATH, '//*[@id="signup-dob"]').send_keys(f'{year}')
        number_sleep = random.randint(1, 2)
        time.sleep(number_sleep)

        time.sleep(2)
        next_button_female = driver.find_element(By.XPATH, "//button[.//span[text()='Continue']]")
        next_button_female.click()
    
    @staticmethod
    def newPassword(password, driver):
        while True:
            password_xpath = "//input[@id='new-password']"
            continue_button = "//button[@type='button' and contains(@class, 'csms-button') and @data-qa='continue-button']"
            wait_for_element_visible(driver, By.XPATH, password_xpath).send_keys(f'{password}')
            number_sleep = random.randint(1, 2)
            time.sleep(number_sleep)
            wait_for_element_visible(driver, By.XPATH, continue_button).click()
            
            number_sleep = random.randint(3, 4)
            time.sleep(number_sleep)
            write_button = wait_for_element_visible(driver, By.XPATH, password_xpath)
            if(write_button is not None):
                password = password = str(uuid.uuid4())[0: 10]
            else:
                break
    
    @staticmethod
    def ChoosePhotos(profile, driver, model_name, lock, final_event):
        photo_path = BadooServices.PHOTO_PATH
        photo = PhotoServices(photo_path)
        with lock:
            photo.process_images_for_editing(model_name)
            driver.maximize_window()
            try:
                element = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, '//'))
                )
            except Exception:
                pass
            driver.execute_script("window.focus()")
            time.sleep(5)
            photo_directory = rf''
            wait_for_element_visible(driver, By.XPATH, BadooServices.add_photo_xpath).click()
            photo_files = [f for f in os.listdir(photo_directory) if os.path.isfile(os.path.join(photo_directory, f))]
            if len(photo_files) == 0:
                raise Exception("NO PHOTOS")
            for i in range(1, 4):
                time.sleep(4)
                if len(photo_files) < 0:
                    break
                if i == 1:
                    take_photo = wait_for_element_visible(driver, By.XPATH, BadooServices.take_a_photo_xpath)
                    take_photo.click()
                if i < 4 and photo_files:
                    selected_photo = random.choice(photo_files)
                    selected_photo_path = os.path.join(photo_directory, selected_photo)
                    keyboard = Controller()
                    number_sleep = random.randint(4, 7)
                    time.sleep(number_sleep)
                    keyboard.type(selected_photo_path)
                    keyboard.press(Key.enter)
                    keyboard.release(Key.enter)
                    photo_files.remove(selected_photo)
                if i < 3:
                    take_another_photo = wait_for_element_visible(driver, By.CLASS_NAME, 'photo-editing-add-button')
                    number_sleep = random.randint(1, 3)
                    time.sleep(number_sleep)
                    take_another_photo.click()
            for i in range(2, 5):
                try:
                    number_sleep = random.randint(2, 5)
                    time.sleep(number_sleep)              
                    photo = wait_for_element_visible(driver, By.XPATH, f'//*[@id="page-container"]/div/div/div[3]/ul/li[{i}]/div/button')
                    photo.click()
                except:
                    pass
            number_sleep = random.randint(5, 10)
            time.sleep(number_sleep)
            upload_images = wait_for_element_visible(driver, By.XPATH, '//*[@id="page-container"]/div/div/div[1]/nav/div/div[2]/button')
            upload_images.click()
            time.sleep(30)
            wait_for_element_visible(driver, By.XPATH, "//button[@data-qa='continue-button']").click()
            driver.minimize_window()
            photo_files = [f for f in os.listdir(photo_directory) if os.path.isfile(os.path.join(photo_directory, f))]
            photo = PhotoServices(photo_path)
            for i in range(len(photo_files)):
                photo.move_photo_to_editing(os.path.join(photo_directory, photo_files[i]), model_name)

        final_event.set()
    @staticmethod
    def _your_are_here(driver):
        number_sleep = random.randint(1, 2)
        time.sleep(number_sleep)
        sexual_orientation = [
            "//button[@data-qa-tiw-option-type='date']", 
            "//button[@data-qa-tiw-option-type='serious']"  
        ]
        random_so_index = random.randint(0, len(sexual_orientation) - 1)

        so_chosen = wait_for_element_visible(driver, By.XPATH, sexual_orientation[random_so_index])
        so_chosen.click()

        number_sleep = random.randint(1, 3)
        time.sleep(number_sleep)
        next = wait_for_element_visible(driver, By.XPATH, '//button[@data-qa="continue-button"]')
        next.click()
    
    @staticmethod
    def _quiz(url, driver, profile="Laurie", day=20, month=3):
        BadooServices._data["Model Name"] = profile 
        size = len(url)
        current_quiz_inverted = ""
        while True:
            if url[size - 1] == "/":
                break
            else:
                current_quiz_inverted += url[size - 1]
            size = size - 1
        
        current_quiz = ""
        
        for i in range(len(current_quiz_inverted) - 1, -1, -1):
            current_quiz += current_quiz_inverted[i] 
        try:

            current_quiz_int = int(current_quiz)
        except Exception as e:
            current_quiz_int = 0

        time.sleep(3)
        BadooServices._current_path = current_quiz_int
        dictionary = {
            12: BadooServices._do_you_drink,
            11: BadooServices._do_you_smoke,
            10: BadooServices._how_you_feel_about_kids,
            30: BadooServices._education_level,
            29: BadooServices._extrovert_or_introvert,
            15: BadooServices._bio,
            20: BadooServices._questionary,
            2: BadooServices._relationship,
            26: BadooServices._signus,
            4: BadooServices._height,
            24: BadooServices._university,
            23: BadooServices._job,
            3: BadooServices._sexuality,
            14: BadooServices._interests,
            27: BadooServices._do_you_have_pets,
            28: BadooServices._what_your_religion   
        }

        time.sleep(4)
        if(current_quiz_int == 12) : dictionary[12](driver)
        elif(current_quiz_int == 11) : dictionary[11](driver)
        elif(current_quiz_int == 10) : dictionary[10](driver)
        elif(current_quiz_int == 30) : dictionary[30](driver)
        elif(current_quiz_int == 29) : dictionary[29](driver)
        if(current_quiz_int == 20) : dictionary[20](driver)
        elif(current_quiz_int == 2) : dictionary[2](driver)
        elif(current_quiz_int == 26) : dictionary[26](driver, day, month)
        elif(current_quiz_int == 4) : dictionary[4](driver)
        elif(current_quiz_int == 24) : dictionary[24](driver)
        elif(current_quiz_int == 23) : dictionary[23](driver)
        elif(current_quiz_int == 3) : dictionary[3](driver)
        elif(current_quiz_int == 14) : dictionary[14](driver)
        elif(current_quiz_int == 15) : dictionary[15](driver)
        elif(current_quiz_int == 27) : dictionary[27](driver)
        elif(current_quiz_int == 28) : dictionary[28](driver)
        else: raise
        
    @staticmethod
    def _questionary(driver):
            list = wait_for_elements(driver, By.XPATH, '//button[@class="profile-questions-tile"]')
            try:
                if list:
                    while True:
                        if len(list) > 0:
                            number_sleep = random.randint(4, 5)
                            time.sleep(number_sleep)
                            list[0].click()
                            choices = wait_for_elements(driver, By.XPATH,'//input[@type="radio"]')
                            choices.pop()
                            number_sleep = random.randint(4, 5)
                            time.sleep(number_sleep)
                            clickable = random.choice(choices)
                            clickable.click()
                            wait_for_element_visible(driver, By.XPATH, "//button[@data-qa='submit-answer']").click()
                            number_sleep = random.randint(4, 5)
                            time.sleep(number_sleep)
                            list = wait_for_elements(driver, By.XPATH, '//button[@class="profile-questions-tile"]')
                        else:
                            break
                    number_sleep = random.randint(2, 3)
                    time.sleep(number_sleep)
            except Exception:
                pass
                    
    @staticmethod
    def _interests(driver):
        try:
            list = wait_for_elements(driver, By.XPATH, "//button[@data-qa='badge']")
            choosen_list = random.sample(population=list, k=4)
            for elements in choosen_list:
                elements.click()
        except Exception:
            pass
            
    @staticmethod
    def _sexuality(driver):

        sexual_orientation = [
        "//label[.//span[text()='Straight']]", 
        "//label[.//span[text()='Lesbian']]"  
        ]
        random_so_index = random.randint(0, len(sexual_orientation) - 1)
        so_chosen = wait_for_element_visible(driver, By.XPATH, sexual_orientation[random_so_index])
        so_chosen.click()

    @staticmethod
    def _relationship(driver):
        wait_for_element_visible(driver, By.XPATH, '//input[@name="relationship" and @value="Single"]').click()
    
    @staticmethod
    def _height(driver):
        
        tall = '//input[@data-qa="pqw-input-range"]'
        
        script = """
        const tall = document.querySelector('.profile-quality-range[data-qa="pqw-input-range"]');
        if (tall) {
            tall.value = %d;
        }
        """ % random.randint(30, 40)
        wait_for_element_visible(driver, By.XPATH, tall).click()
        element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//input[@class='profile-quality-range' and @data-qa='pqw-input-range']"))
        )

        driver.execute_script(script, element)
        
    @staticmethod
    def _university(driver):
        with open(BadooServices.PATH_UNIVERSITY, 'r') as file:
            unis = file.readlines()
        choose = random.choice(unis).strip()
        box = wait_for_element_visible(driver, By.XPATH, "//input[@class='csms-text-field__input csms-text-field__input--text' and @data-qa='text-field-input']")
        box.click()
        box.send_keys(choose)
       
    @staticmethod
    def _do_you_have_pets(driver):
        options = [
            "//label[.//span[contains(text(), 'Cat')]]",
            "//label[.//span[contains(text(), 'Dog')]]",
            "//label[.//span[contains(text(), 'Both')]]",
        ]
        number = random.randint(0, len(options) - 1)
        label = options[number]
        wait_for_element_visible(driver, By.XPATH, label).click() 
       
    @staticmethod
    def _what_your_religion(driver):
        options = [
            "//label[.//span[contains(text(), 'Atheist')]]",
            "//label[.//span[contains(text(), 'Catholic')]]",
            "//label[.//span[contains(text(), 'Christian')]]",
        ]
        number = random.randint(0, len(options) - 1)
        label = options[number]
        wait_for_element_visible(driver, By.XPATH, label).click()

    @staticmethod 
    def _do_you_drink(driver):
        options = [
            "//label[.//span[contains(text(), 'Socially')]]",
            "//label[.//span[contains(text(), 'Never')]]",
            "//label[.//span[contains(text(), 'Often')]]",
        ]
        number = random.randint(0, len(options) - 1)
        label = options[number]
        wait_for_element_visible(driver, By.XPATH, label).click()
    
    def _do_you_smoke(driver):
        label = "//input[@name='smoking' and @value='No']"

        tap = wait_for_element_visible(driver, By.XPATH, label)
        if tap:
            tap.click()
    
    @staticmethod 
    def _how_you_feel_about_kids(driver):
        label = "//label[.//span[contains(text(), 'like them someday')]]"
        wait_for_element_visible(driver, By.XPATH, label).click()
    
    @staticmethod 
    def _education_level(driver):
        number_sleep = random.randint(3, 6)
        time.sleep(number_sleep)
        label = "//label[.//span[contains(text(), 'Postgraduate degree')]]"
        wait_for_element_visible(driver, By.XPATH, label).click()
    
    @staticmethod 
    def _extrovert_or_introvert(driver):
        
        options = [
            "//label[.//span[contains(text(), 'Introvert')]]",
            "//label[.//span[contains(text(), 'Extrovert')]]",
        ]
        number = random.randint(0, len(options) - 1)
        label = options[number]
        wait_for_element_visible(driver, By.XPATH, label).click()
    
    @staticmethod 
    def _signus(driver, day, month):
        try:
            element = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "//"))
            )
        except Exception:
            pass

        driver.execute_script("window.scrollTo(0, 200)")
        signus = get_star_sign(day=int(day), month=int(month))
        label = f"//label[.//span[contains(text(), '{signus}')]]"
        wait_for_element_visible(driver, By.XPATH, label).click()

    @staticmethod
    def _bio(driver):
        with open(BadooServices.TALK_ABOUT_PATH, 'r') as file:
            unis = file.readlines()
        choose = random.choice(unis).strip()
        wait_for_element_visible(driver, By.ID, 'about-textarea').send_keys(f'{choose}')
        time.sleep(3)
        try:

            driver.find_element(By.XPATH, '//button[@data-qa="profile-quality-done"]').click()
        except Exception:
            pass
    
    @staticmethod
    def _return_data():
        return BadooServices._data
    
file_path = r''

with open(file_path, 'r') as file:
    file_contents = file.read()

profile_data = ast.literal_eval(file_contents.split('=')[1].strip())

profile_ids = list(profile_data.keys())
profile_names = list(profile_data.values())
def cancel_SMS(ORDER_ID, PROFILE_ID):
    while True:
        time_sleep = random.randint(10, 20)
        time.sleep(time_sleep)
        response_cancel = SMS_SENDER.cancel_sms(ORDER_ID)
        if response_cancel['success'] == 1:
            stop(API_BASE_URL, PROFILE_ID)
            break
    raise

access_token = "eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.eyJhdWQiOiIxIiwianRpIjoiMDRmMzY1YThhNjU5OTc2NmJjM2I2NzJkN2ZiNWYxOGVlNjUyN2E5Y2Y1NjBjNWNmMDgwNjc5OTlmMTUzYmU4M2NhYWI0NzM3Yjg5ZDc3OTAiLCJpYXQiOjE3MjA0MzQ2MjEuMzk0ODk2LCJuYmYiOjE3MjA0MzQ2MjEuMzk0ODk5LCJleHAiOjE3NTE5NzA2MjEuMzgwMTAyLCJzdWIiOiIyNTg1Nzc1Iiwic2NvcGVzIjpbXX0.dDW27glTVusC-qMzXRQyvv8rL9miyjGoLnIYWxv1dRUswh3v4X1IpWmktFdE7nRI0zu4RuTnFKWatemPLDr_bssoTXId2yLGHgtTrI2e5UsEb0HWdofsaEdFv7xHodpfI3uKM7cUgvckV_vG9MtfRwQEWNe-7NooFjFyKWfXQEPGBgaGs8HLjhPo31s9SYBDtAroq7G_EMRgAqufnM8M2hjQ3XswT393Uf01ufWZbLhFVgorI9foXbvaQsqNOiPnid5Kc_lSJPYSX9xDW3mVpHvL6DVVSdi-XqhVQUITaBes3ULckj35D-Gjm1VXRMLDjMSNdaGJ3tG8MZ3wYCVPqsBOE38mcgG9_4AoFO1rI5t_MhySsNrI1Ix392OqwL56VdPOmis14C6nf3J2uVUm9HBFIQCrY30u6ZuDUrMKBEKFQ9oZ1yxX58plOpNGtEFIw4o4_CqNdLB0gYvgmElyBkkdePj4Wus2huQ_2tomYsSrjT5v72tob-6KSyNe_fX_wpCEFB5a14fS1_19NBSYIKMjfNgDfT4ImMY8EyCZBOpFwAKZ0PxukQAVKMb1N3I48DSepRTIGIiYkom720YXT9Gd-VGczIq-m_jv5WyKNcW0_WnTA_rv7YS47dXIjarrq39XEldhk-fa0KBQs9bKP7i0yIGO7TIH9ip_CCJ9yk4"
list_profiles_url = "https://dolphin-anty-api.com/browser_profiles"

headers = {
    "Authorization": f"Bearer {access_token}"
}

API_BASE_URL = "http://localhost:3001/v1.0"

def get_swipe(driver, action):
        return wait_for_elements(driver, By.XPATH,f"//button[@class='profile-action' and @data-qa='profile-card-action-vote-{action}']")[1]

def start_badoo(driver):
    driver.get('https://badoo.com/onboarding-phone')
    time.sleep(30)
    try:
        iframe = driver.find_element(By.ID, "sp_message_iframe_1172550")
        if iframe:
            driver.switch_to.frame(iframe)
            wait_for_element_visible(driver, By.XPATH, "//button[@title='Accept cookies' and contains(@class, 'message-button') and text()='Accept cookies']").click()
            driver.switch_to.default_content()
    except Exception:
        pass

        
def stop(API_BASE_URL, PROFILE_ID):
    stop_url = f"{API_BASE_URL}/browser_profiles/{PROFILE_ID}/stop"
    response = requests.get(stop_url)
    data = response.json()
    if not data.get('success'):
        raise Exception("Failed to stop the Dolphin Anty profile.")
    
def get_star_sign(day, month):
    if (month == 3 and day >= 21) or (month == 4 and day <= 19):
        return "Aries"
    elif (month == 4 and day >= 20) or (month == 5 and day <= 20):
        return "Taurus"
    elif (month == 5 and day >= 21) or (month == 6 and day <= 20):
        return "Gemini"
    elif (month == 6 and day >= 21) or (month == 7 and day <= 22):
        return "Cancer"
    elif (month == 7 and day >= 23) or (month == 8 and day <= 22):
        return "Leo"
    elif (month == 8 and day >= 23) or (month == 9 and day <= 22):
        return "Virgo"
    elif (month == 9 and day >= 23) or (month == 10 and day <= 22):
        return "Libra"
    elif (month == 10 and day >= 23) or (month == 11 and day <= 21):
        return "Scorpio"
    elif (month == 11 and day >= 22) or (month == 12 and day <= 21):
        return "Sagittarius"
    elif (month == 12 and day >= 22) or (month == 1 and day <= 19):
        return "Capricorn"
    elif (month == 1 and day >= 20) or (month == 2 and day <= 18):
        return "Aquarius"
    elif (month == 2 and day >= 19) or (month == 3 and day <= 20):
        return "Pisces"
    else:
        return "Unknown"

def wait_for_element_visible(driver, by, value, timeout=3):
    return WebDriverWait(driver, timeout).until(
        EC.visibility_of_element_located((by, value))
    )

def wait_for_elements(driver, by, value, timeout=3):
    return WebDriverWait(driver, timeout).until(
        EC.presence_of_all_elements_located((by, value))
    )

def create_new_profile(model_name, headers):

    user_country = 'UK'

    headers = {
            "Authorization": f"Bearer {api_key}"
        }

    def read_proxies_from_file(file_path):
        with open(file_path, 'r') as file:
            proxies = [line.strip() for line in file.readlines()]
        return proxies

    if user_country == 'UK':
        proxy_file_path = r""
    elif user_country == 'USA':
        proxy_file_path = r""
    proxy_list = read_proxies_from_file(proxy_file_path)

    def fetch_profiles_with_tag(api_key, tag):
        url = "https://dolphin-anty-api.com/browser_profiles"
        params = {
            "query": tag,
            "limit": 50,
            "page": 1
        }
        headers = {
            "Authorization": f"Bearer {api_key}"
        }
        response = requests.get(url, headers=headers, params=params)
        if response.status_code == 200:
            return response.json().get('data', [])
        else:

            return None

    def get_highest_profile_number(profiles, model_name):
        highest_number = 0
        for profile in profiles:
            name = profile.get('name', '')
            if name.startswith(model_name):
                try:
                    number = int(name.split()[-1])
                    highest_number = max(highest_number, number)
                except ValueError:
                    continue
        return highest_number

    def fetch_user_agent(headers):
        user_agent_url = "https://dolphin-anty-api.com/fingerprints/useragent"
        params = {
            "browser_type": "anty",
            "browser_version": "latest",
            "platform": platform
        }
        response = requests.get(user_agent_url, headers=headers, params=params)
        if response.status_code == 200:
            return response.json().get('data')
        else:
            return "Default User Agent String"

    def fetch_webgl_info():
        webgl_url = "https://dolphin-anty-api.com/fingerprints/fingerprint"
        params = {
            "platform": platform,
            "browser_type": "anty",
            "browser_version": "112",
            "type": "fingerprint",
            "screen": "2560x1440"
        }
        response = requests.get(webgl_url, headers=headers, params=params)
        if response.status_code == 200:
            response_data = response.json()

            unmasked_vendor = response_data.get('webgl', {}).get('unmaskedVendor', 'Default WebGL Vendor')
            unmasked_renderer = response_data.get('webgl', {}).get('unmaskedRenderer', 'Default WebGL Renderer')
            webgl2_maximum = json.loads(response_data.get('webgl2Maximum', '{}'))

            return unmasked_vendor, unmasked_renderer, webgl2_maximum
        else:
            return "Default WebGL Vendor", "Default WebGL Renderer", {}
        

    def rewrite_proxy_file(file_path, proxies):
        with open(file_path, 'w') as file:
            for proxy in proxies:
                file.write(proxy + '\n')
    created_profiles = []
    
    while True:
        platform = random.choice(['macos', 'windows'])
        profiles = fetch_profiles_with_tag(api_key, model_name)
        if not profiles:
            return None, None
        highest_number = get_highest_profile_number(profiles, model_name)
        new_profile_name = f"{model_name} {highest_number + 1}"

        new_user_agent = fetch_user_agent(headers)
        new_webgl_vendor, new_webgl_renderer, new_webgl2_maximum = fetch_webgl_info()

        random_proxy = random.choice(proxy_list)
        proxy_list.remove(random_proxy)
        rewrite_proxy_file(proxy_file_path, proxy_list)

        proxy_parts = random_proxy.split(':')
        proxy_host, proxy_port, proxy_login, proxy_password = proxy_parts

        proxy_config = {
            "type": "http",
            "host": proxy_host,
            "port": proxy_port,
            "login": proxy_login,
            "password": proxy_password,
            "name": "Sticky"
        }

        profile_data = {
            "name": new_profile_name,
            "tags": [model_name, "Badoo", ' UK'],
            "tabs": [],
            "platform": platform,
            "mainWebsite": "", 
            "useragent": {
                "mode": "manual",
                "value": new_user_agent
            },
            "proxy": proxy_config,
        "webrtc": {
            "mode": "altered"
        },
        "canvas": {
            "mode": "noise"
        },
        "webgl": {
            "mode": "noise"
        },
            "webglInfo": {
                "mode": "manual",
                "vendor": new_webgl_vendor if new_webgl_vendor else "Default WebGL Vendor",
                "renderer": new_webgl_renderer if new_webgl_renderer else "Default WebGL Renderer",
                "webgl2Maximum": new_webgl2_maximum if new_webgl2_maximum else "Default WebGL Renderer",
            },
        "timezone": {
            "mode": "auto"
        },
        "locale": {
            "mode": "auto"
        },
        "geolocation": {
            "mode": "auto"
        },
        "cpu": {
            "mode": "manual",
            "value": random.choice([2, 4, 8, 16])
        },
        "memory": {
            "mode": "manual",
            "value": random.choice([4, 8, 16, 32])
        },
        "doNotTrack": 0,
        "browserType": "anty"
        }

        create_profile_url = "https://dolphin-anty-api.com/browser_profiles"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}"
        }


        try:
            create_response = requests.post(create_profile_url, headers=headers, data=json.dumps(profile_data))
            create_response.raise_for_status()
            create_response_data = create_response.json()
            if create_response_data.get("success") == 1:
                browser_profile_id = create_response_data.get("browserProfileId", "Unknown ID")

                created_profiles.append((new_profile_name, browser_profile_id))

                
                with open(r'', 'w') as file:
                    file.write("profile_names = {\n")
                    for name, id in created_profiles:
                        file.write(f"    '{id}': '{name}',\n")
                    file.write("}\n")
                    
                return browser_profile_id, new_profile_name

            else:

                return None, None

        except Exception as e:

            if '404 Client Error: Not Found for url: https://dolphin-anty-api.com/browser_profiles' in str(e):
                continue
            else:
                send_to_discord(f"Reddit Auto - An error occurred while creating the profile, in reddit_auto_reddit, '{new_profile_name}': {e}\n{'-' * 113}")

                return None, None
                
def send_to_discord(var_):
    pass
            
def close_profile(PROFILE_ID):
    stop_url = f"{API_BASE_URL}/browser_profiles/{PROFILE_ID}/stop"
    requests.get(stop_url, headers=headers)

def delete_profile(PROFILE_ID):

    delete_url = f"https://dolphin-anty-api.com/browser_profiles/{PROFILE_ID}?forceDelete=1"
    response = requests.delete(delete_url, headers=headers)

    if response.status_code == 200:
        pass
    else:

        print(f"Badoo Account Maker - Failed to delete profile {PROFILE_ID} in Dolphin Anty. Message: {response.text}.\n{'-' * 113}", flush=True)
        send_to_discord(f"Badoo Account Maker - Failed to delete profile {PROFILE_ID} in Dolphin Anty, continuing anyway. Message: {response.text}.\n{'-' * 113}")

attempt = 1
api_key = ''

def start_profile(profile_name, profile_id):

    global attempt

    try:
        model_name = re.sub(r'\d+$', '', profile_name).strip()

        start_url = f"{API_BASE_URL}/browser_profiles/{profile_id}/start?automation=1"
        response = requests.get(start_url)
        data = response.json()

        if not data.get('success'):
            raise Exception("Failed to start the Dolphin Anty profile.")
        port = data['automation']['port']
        options = webdriver.ChromeOptions()
        options.add_argument(f'--remote-debugging-port={port}')
        options.add_argument('--user-data-dir=./User_Data')
        options.add_argument('--headless')
        debugger_address = f"localhost:{port}"
        options.debugger_address = debugger_address
        options.add_argument("--lang=en")
        chrome_driver_path = r"chromedriver.exe"
        service = Service(executable_path=chrome_driver_path)
        driver = webdriver.Chrome(service=service, options=options)

        with open(PATH_NAMES, 'r') as file:
            unis = file.readlines()
        name_choosen = random.choice(unis).strip()
        
        time.sleep(5)

        password = str(uuid.uuid4())[0: 10]
        randomInt = random.randint(1, 12)
        day = random.randint(1, 28)
        signup_tel = "//input[@id='phone-input']"
        signup_but = '//button[@aria-live="polite"]'
        confirm_tel = "//input[@id='confirmation-code-input']"
        confirm_tel_button = "//button[@type='submit' and contains(@class, 'csms-button') and @data-qa='continue-button']"
        start_badoo(driver)

        response = SMS_SENDER.order_sms()
        if response:

            if response["success"] == 1:
                wait_for_element_visible(driver, By.XPATH, '//button[@data-qa="phone-login"]').click()
                time.sleep(3)
                wait_for_element_visible(driver, By.XPATH, signup_tel).send_keys(f"{response['number']}")
                time.sleep(2)

                button_List_continue = wait_for_elements(driver, By.XPATH, signup_but)
                button_List_continue[1].click()
                time.sleep(10)

                wait_for_element_visible(driver, By.XPATH, "//span[text()='OK']").click()

                time_sleep = random.randint(20, 26)
                time.sleep(time_sleep)
                order_id = response["order_id"]
                time_sleep = random.randint(40, 60)
                time.sleep(time_sleep)
                try:
                    call_me_button = wait_for_element_visible(driver, By.XPATH, "//button[contains(@class, 'csms-button') and @type='button']//span[text()='Call Me']")
                    if call_me_button:
                        cancel_SMS(order_id, profile_id)
                        stop(API_BASE_URL, profile_id)
                except Exception:
                    pass
                sms = SMS_SENDER.check_sms(order_id)
                if sms:
                    if sms["status"] != 1 and wait_for_element_visible(driver, By.XPATH, confirm_tel):

                        wait_for_element_visible(driver, By.XPATH, confirm_tel).send_keys(sms["sms"])

                        wait_for_element_visible(driver, By.XPATH, confirm_tel_button).click()
                        time.sleep(20)
                        if sms["sms"]:

                            check_create_account = BadooServices.Create_An_Account(driver, password, profile_name, model_name, day, randomInt, COUNTRY_PATH, get_swipe, DONE_COLOR, lock_sequencial, final_event, profile_id) 
                            stop(API_BASE_URL, profile_id)
                            if not check_create_account:
                                raise
                            else:
                                print(f"Badoo Account Maker - Account created successfully for dolphin name {profile_name} and id {profile_id}.\n{'-' * 113}", flush=True)
                                send_to_discord(f"Badoo Account Maker - Account created successfully for dolphin name {profile_name} and id {profile_id}.\n{'-' * 113}")

                                return
                            
                        else:
                            cancel_SMS(order_id, profile_id)
                            raise
                    else:
                        cancel_SMS(order_id, profile_id)
                        raise    
                else:
                    cancel_SMS(order_id, profile_id)
                    raise    

        else:
            raise

    except Exception as e:

        attempt+=1

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}"
        }

        print(f"Badoo Account Maker - Exception encountered for profile {profile_id}: {e}. Attempting to retry...\n{'-' * 113}", flush=True)
        if attempt <= 4:  
            print(f"Badoo Account Maker - Attempt {attempt}: Closing and deleting profile {profile_id}, then retrying...\n{'-' * 113}", flush=True)
            close_profile(profile_id)
            delete_profile(profile_id)
            new_profile_id, new_profile_name = create_new_profile(model_name, headers)  
            if new_profile_id:
                start_profile(new_profile_name, new_profile_id)
            else:
                print(f"Badoo Account Maker - Failed to create a new profile on attempt {attempt}.\n{'-' * 113}", flush=True)
        else:
            print(f"Badoo Account Maker - Failed to create profile after {attempt} attempts.\n{'-' * 113}", flush=True)
            send_to_discord(f"Badoo Account Maker - Failed to create profile after {attempt} attempts.\n{'-' * 113}")
            close_profile(profile_id)
            delete_profile(profile_id)
            return 
        
lock_sequencial = Lock()
final_event = Event()
   
with ThreadPoolExecutor(max_workers=10) as executor:
    list(executor.map(start_profile, profile_names, profile_ids))
    