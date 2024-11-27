import random
import os
from utility.utils import Utils
from selenium.webdriver.common.by import By
import time
from pynput.keyboard import Key, Controller
from selenium.common.exceptions import TimeoutException, ElementClickInterceptedException, NoSuchElementException, StaleElementReferenceException
from selenium.webdriver.common.keys import Keys
from termcolor import colored
from services.Photo_services import PhotoServices
from dotenv import load_dotenv
import uuid


load_dotenv()
class BadooServices:

    random_wait_time = 1
    take_a_photo_xpath = "//button[@class='csms-action-row' and @type='button' and @data-qa='action-sheet-item' and @data-qa-type='generic' and @data-qa-provider='gallery']"
    add_photo_xpath = "//button[@class='multimedia multimedia--background-primary-lighten' and @data-qa='registration-add-photos__cta']"
    PATH_UNIVERSITY = r"C:\Users\info\OneDrive\Desktop\Python Code\Isaack Codes\melow_like_bot\badoo_system\Dating App General .txt Files-20240715T153420Z-001\Dating App General .txt Files\university.txt"
    INTERESTS_PATH = r"C:\Users\info\OneDrive\Desktop\Python Code\Isaack Codes\melow_like_bot\badoo_system\Dating App General .txt Files-20240715T153420Z-001\Dating App General .txt Files\hobbies.TXT"
    TALK_ABOUT_PATH = r"C:\Users\info\OneDrive\Desktop\Python Code\Isaack Codes\melow_like_bot\badoo_system\Dating App General .txt Files-20240715T153420Z-001\Dating App General .txt Files\talking_about.TXT"
    _data = {}
    _current_path = -1
    PHOTO_PATH = os.getenv('PHOTO_PATH')
    
    @staticmethod
    def start_badoo(driver):
        driver.get('https://badoo.com/signup')
        BadooServices.sleep_code(10, 15)
        try:
            iframe = driver.find_element(By.ID, "sp_message_iframe_1172550")
            if iframe:
                driver.switch_to.frame(iframe)
                Utils.perform_action(driver, By.XPATH, "//button[@title='Accept cookies' and contains(@class, 'message-button') and text()='Accept cookies']", 'click')
                driver.switch_to.default_content()
        except Exception:
            pass
    
    @staticmethod
    def Create_An_Account(driver, sleep_code, password, profile_name, model_name, day, randomInt, COUNTRY_PATH, get_swipe, DONE_COLOR, lock, final_event):
        BadooServices.SetGenderAndBirthday(profile_name, driver, model_name)
        sleep_code()
        BadooServices.ChoosePhotos(model_name, driver, model_name,lock, final_event)
        sleep_code()
        BadooServices.newPassword(password, driver)
        sleep_code()    
        BadooServices._your_are_here(driver)
        sleep_code()
        Utils.perform_action(driver, By.XPATH, "//button[span/span[text()='Start The Quiz']]", 'click')
        sleep_code()
        while True:
            sleep_code(2,4)
            if BadooServices._current_path != 16:
                try:
                    BadooServices._quiz(url=driver.current_url, driver=driver, profile=model_name,day=day, month=randomInt)
                except Exception as e:
                    print(colored("Something Wrong, occurred an error on the code, you can see the log there -> ", "light_red"))
                    print(e)
                    BadooServices._quiz(day=day, driver=driver, month=randomInt, profile=model_name, url=driver.current_url)    
            else:
                break   
        sleep_code(4, 7)
        Utils.perform_action(driver, By.XPATH, "//button[@data-qa='continue-button']", 'click')
        sleep_code(4, 6)
        with open(COUNTRY_PATH,'r') as file:
            unis = file.readlines()
        choose = random.choice(unis).strip()
        Utils.perform_action(driver, By.XPATH, "//input[@name='location']", 'send_keys', choose)
        list = Utils.wait_for_elements_visible(driver, By.XPATH, "//li[@data-qa='suggested-location']")     
        element = random.choice(list)
        element.click()
        next = Utils.wait_for_element(driver, By.XPATH, '//button[@data-qa="continue-button"]')
        next.click()
        sleep_code()
        Utils.perform_action(driver, By.XPATH, '//button[.//span[contains(text(),"No Thanks")]]', "click")
        input()
        # script = """
        # var element = document.querySelector('.onboarding-tips__tooltip.js-highlighted-element');
        # if (element) {
        #     element.click();
        # } else {
        #     console.log('Elemento não encontrado.');
        # }
        # """
        # accept_notification = "//button[@class='csms-action-row' and .//span[text()='Yes']]"
        # yes_button = "//button[@class='profile-action' and @data-qa='profile-card-action-vote-yes']"
        # for i in range(1, 5):
        #     sleep_code(1,4)  
        #     Utils.perform_action(driver, By.XPATH, accept_notification, 'click', 1)     
        #     Utils.perform_action(driver, By.XPATH, yes_button, 'click', 1)     
        #     BadooServices.sleep_code(2,5)
        # print(colored("DONE ---- YOUR ACCOUNT HAS BEEN CREATED", DONE_COLOR))
    
    
    @staticmethod
    def Login(email, driver):
        try:
            Utils.perform_action(driver, By.XPATH, "//button[contains(., 'Continue with Google')]", 'click')
            time.sleep(20)
            principle_page = driver.current_window_handle

            for window_handle in driver.window_handles:
                if window_handle != principle_page:
                    driver.switch_to.window(window_handle)
                    break
            Utils.perform_action(driver, By.XPATH, f"//li[.//div[@class='yAlK0b' and @data-email='{email}@gmail.com", 'click')
            Utils.perform_action(driver, By.XPATH, "//button[contains(span[@class='VfPpkd-vQzf8d'], 'Continue')]", 'click')
            driver.switch_to.window(principle_page)

        except Exception as e:
            print(e)
        time.sleep(20)
    
    @staticmethod
    def sleep_code(init = 10, end = 20):
        time.sleep(random.randint(init, end))
    
    @staticmethod
    def _job(driver):
        random_job_indices = random.randint(0, 50)
        job_container = Utils.wait_for_element(driver, By.XPATH, "//input[@class='csms-text-field__input csms-text-field__input--text' and @data-qa='text-field-input']", 20)
        job_container.click()
        job_title = f'*//li[@class="csms-listbox__item"][{random_job_indices}]/div[@class="csms-listbox__item-text"]/span'
        job_chosen = Utils.wait_for_element(driver, By.XPATH, job_title)
        job_name = job_chosen.get_attribute('innerHTML')
        job_container.send_keys(job_name)
        job_chosen = Utils.wait_for_element(driver, By.XPATH, '*//div[@class="csms-listbox"][1]')
        job_chosen.click()
        enterprise_name = Utils.wait_for_element(driver, By.XPATH, "//div[@data-qa='pqw-company-name']//input[@type='text']")
        final_name = job_name + " Company"
        enterprise_name.send_keys(final_name)
        BadooServices._data["Occupation"] = job_name
        BadooServices._nextQuiz(driver)
    
    @staticmethod
    def SetGenderAndBirthday(profile, driver, name):
        signup_name = "//input[@id='signup-name']"
        BadooServices.sleep_code()
        Utils.perform_action(driver, By.XPATH, "//label[@data-qa-gender='female']", 'click')
        Utils.perform_action(driver, By.XPATH, signup_name, 'send_keys', name)
        
        _day = random.randint(1, 28)
        _month = random.randint(1, 12)
        month = f"{_month:02d}"
        day = f"{_day:02d}"
        year = random.randint(1996, 2002)
        BadooServices.sleep_code(2,3)
        try:
            Utils.perform_action(driver, By.XPATH, '//*[@id="signup-dob"]', 'click')
            Utils.perform_action(driver, By.XPATH, '//*[@id="signup-dob"]', 'send_keys', day)
            BadooServices.sleep_code(1,2)
            Utils.perform_action(driver, By.XPATH, '//*[@id="signup-dob"]', 'send_keys', month)
            BadooServices.sleep_code(1,2)
            Utils.perform_action(driver, By.XPATH, '//*[@id="signup-dob"]', 'send_keys', year)
            BadooServices.sleep_code(1,2)
        except TimeoutException:
            print(f"{profile} failed clicking birthday box")
            print("------------------------------------------------------------------")
            return 
        time.sleep(2)
        next_button_female = driver.find_element(By.XPATH, "//button[.//span[text()='Continue']]")
        next_button_female.click()
    
    @staticmethod
    def newPassword(password, driver):
        while True:
            password_xpath = "//input[@id='new-password']"
            continue_button = "//button[@type='button' and contains(@class, 'csms-button') and @data-qa='continue-button']"
            Utils.perform_action(driver, By.XPATH, password_xpath, 'send_keys', password)
            BadooServices.sleep_code(1, 2)
            Utils.perform_action(driver, By.XPATH, continue_button, 'click')
            
            BadooServices.sleep_code(3, 4)
            write_button = Utils.wait_for_element(driver, By.XPATH, password_xpath)
            if(write_button is not None):
                password = password = str(uuid.uuid4())[0: 10]
            else:
                break
        print(colored("CREATE A NEW PASSWORD IS DONE", "green"))
    

    
    @staticmethod
    def ChoosePhotos(profile, driver, model_name, lock, final_event):
        photo_path = BadooServices.PHOTO_PATH
        photo = PhotoServices(photo_path)
        with lock:
            photo.process_images_for_editing(model_name)
            driver.maximize_window()
            Utils.perform_action(driver, By.XPATH, '//', 'execute_script', 'window.focus()')
            time.sleep(5)
            photo_directory = rf'C:\Users\anthc\Documents\job\Anthony-Repo\photoss\{profile}\Finished Photos'
            Utils.perform_action(driver, By.XPATH, BadooServices.add_photo_xpath, 'click')
            photo_files = [f for f in os.listdir(photo_directory) if os.path.isfile(os.path.join(photo_directory, f))]
            if len(photo_files) == 0:
                raise Exception("NO PHOTOS")
            for i in range(1, 4):
                time.sleep(4)
                if len(photo_files) < 0:
                    break
                if i == 1:
                    take_photo = Utils.wait_for_element(driver, By.XPATH, BadooServices.take_a_photo_xpath)
                    take_photo.click()
                if i < 4 and photo_files:
                    selected_photo = random.choice(photo_files)
                    selected_photo_path = os.path.join(photo_directory, selected_photo)
                    keyboard = Controller()
                    BadooServices.sleep_code(4, 7)
                    keyboard.type(selected_photo_path)
                    keyboard.press(Key.enter)
                    keyboard.release(Key.enter)
                    photo_files.remove(selected_photo)
                if i < 3:
                    take_another_photo = Utils.wait_for_element(driver, By.CLASS_NAME, 'photo-editing-add-button')
                    BadooServices.sleep_code(1, 3)
                    take_another_photo.click()
            for i in range(2, 5):
                try:
                    BadooServices.sleep_code(2, 5)              
                    photo = Utils.wait_for_element(driver, By.XPATH, f'//*[@id="page-container"]/div/div/div[3]/ul/li[{i}]/div/button')
                    photo.click()
                except:
                    print(colored(f"DONT FIND ANY PHOTO TO INDEX {i}", "light_red"))
            BadooServices.sleep_code(5, 10)
            upload_images = Utils.wait_for_element(driver, By.XPATH, '//*[@id="page-container"]/div/div/div[1]/nav/div/div[2]/button')
            upload_images.click()
            time.sleep(30)
            Utils.perform_action(driver, By.XPATH, "//button[@data-qa='continue-button']",'click')
            driver.minimize_window()
            photo_files = [f for f in os.listdir(photo_directory) if os.path.isfile(os.path.join(photo_directory, f))]
            photo = PhotoServices(photo_path)
            for i in range(len(photo_files)):
                photo.move_photo_to_editing(os.path.join(photo_directory, photo_files[i]), model_name)
            print(colored("CHOOSE PHOTO HAS BEEN COMPLETED", "green"))
        final_event.set()
    @staticmethod
    def _your_are_here(driver):
        BadooServices.sleep_code(1,2)
        sexual_orientation = [
            "//button[@data-qa-tiw-option-type='date']", 
            "//button[@data-qa-tiw-option-type='serious']"  
        ]
        random_so_index = random.randint(0, len(sexual_orientation) - 1)
        so_chosen = Utils.wait_for_element(driver, By.XPATH, sexual_orientation[random_so_index])
        so_chosen.click()
        BadooServices.sleep_code(1,3)
        next = Utils.wait_for_element(driver, By.XPATH, '//button[@data-qa="continue-button"]')
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
            print(current_quiz)
            current_quiz_int = int(current_quiz)
        except Exception as e:
            print("QUIZ -> Not a number (URL) " + str(e))
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
        print(current_quiz_int)
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
        else: BadooServices._nextQuiz(driver)
    
    @staticmethod
    def _nextQuiz(driver):
        time.sleep(1)
        Utils.perform_action(driver, By.XPATH,'//button[@data-qa="profile-quality-done"]', 'click')
        list_continue_button = Utils.wait_for_elements_visible(driver, By.XPATH, "//button[@class='csms-pagination-bar__action' and not(@aria-hidden='true')]")
        if len(list_continue_button) > 1:
            continue_button = list_continue_button[1]
        else:
            continue_button = list_continue_button[0]
        continue_button.click()
        
    @staticmethod
    def _questionary(driver):
            list = Utils.wait_for_elements_visible(driver, By.XPATH, '//button[@class="profile-questions-tile"]')
            try:
                if list:
                    while True:
                        if len(list) > 0:
                            BadooServices.sleep_code(4, 5)
                            list[0].click()
                            choices = Utils.wait_for_elements_visible(driver, By.XPATH,'//input[@type="radio"]')
                            choices.pop()
                            BadooServices.sleep_code(4, 5)
                            clickable = random.choice(choices)
                            clickable.click()
                            Utils.perform_action(driver, By.XPATH, "//button[@data-qa='submit-answer']", 'click')
                            BadooServices.sleep_code(4, 5)
                            list = Utils.wait_for_elements_visible(driver, By.XPATH, '//button[@class="profile-questions-tile"]')
                        else:
                            break
                    BadooServices.sleep_code(2, 3)
            finally:
                BadooServices._nextQuiz(driver)
                print("Something wrong")
                    
    @staticmethod
    def _interests(driver):
        try:
            list = Utils.wait_for_elements_visible(driver, By.XPATH, "//button[@data-qa='badge']")
            choosen_list = random.sample(population=list, k=4)
            for elements in choosen_list:
                elements.click()
        finally:
            BadooServices._nextQuiz(driver)

            
    @staticmethod
    def _sexuality(driver):
        try:
            sexual_orientation = [
            "//label[.//span[text()='Straight']]", 
            "//label[.//span[text()='Lesbian']]"  
            ]
            random_so_index = random.randint(0, len(sexual_orientation) - 1)
            so_chosen = Utils.wait_for_element(driver, By.XPATH, sexual_orientation[random_so_index])
            so_chosen.click()
        except Exception as e:
            print(e)
        finally:
            BadooServices._nextQuiz(driver)
    
    @staticmethod
    def _relationship(driver):
        Utils.perform_action(driver, By.XPATH, '//input[@name="relationship" and @value="Single"]', "click")
        BadooServices._nextQuiz(driver)
    
    @staticmethod
    def _height(driver):
        
        tall = '//input[@data-qa="pqw-input-range"]'
        
        script = """
        const tall = document.querySelector('.profile-quality-range[data-qa="pqw-input-range"]');
        if (tall) {
            tall.value = %d;
        }
        """ % random.randint(30, 40)
        Utils.perform_action(driver, By.XPATH, tall, "click")
        Utils.perform_action(driver, By.XPATH, "//input[@class='profile-quality-range' and @data-qa='pqw-input-range']", "execute_script", script)
        BadooServices._nextQuiz(driver)
        
    @staticmethod
    def _university(driver):
        with open(BadooServices.PATH_UNIVERSITY, 'r') as file:
            unis = file.readlines()
        choose = random.choice(unis).strip()
        box = Utils.wait_for_element(driver, By.XPATH, "//input[@class='csms-text-field__input csms-text-field__input--text' and @data-qa='text-field-input']")
        print(box)
        box.click()
        box.send_keys(choose)
        BadooServices._nextQuiz(driver)
       
    @staticmethod
    def _do_you_have_pets(driver):
        options = [
            "//label[.//span[contains(text(), 'Cat')]]",
            "//label[.//span[contains(text(), 'Dog')]]",
            "//label[.//span[contains(text(), 'Both')]]",
        ]
        number = random.randint(0, len(options) - 1)
        label = options[number]
        Utils.perform_action(driver, By.XPATH, label, 'click')
        BadooServices._nextQuiz(driver)  
       
    @staticmethod
    def _what_your_religion(driver):
        options = [
            "//label[.//span[contains(text(), 'Atheist')]]",
            "//label[.//span[contains(text(), 'Catholic')]]",
            "//label[.//span[contains(text(), 'Christian')]]",
        ]
        number = random.randint(0, len(options) - 1)
        label = options[number]
        Utils.perform_action(driver, By.XPATH, label, 'click')
        BadooServices._nextQuiz(driver)
       
    @staticmethod 
    def _do_you_drink(driver):
        options = [
            "//label[.//span[contains(text(), 'Socially')]]",
            "//label[.//span[contains(text(), 'Never')]]",
            "//label[.//span[contains(text(), 'Often')]]",
        ]
        number = random.randint(0, len(options) - 1)
        label = options[number]
        Utils.perform_action(driver, By.XPATH, label, 'click')
        BadooServices._nextQuiz(driver)
    
    def _do_you_smoke(driver):
        label = "//input[@name='smoking' and @value='No']"
        print("HERE")
        tap = Utils.wait_for_element_visible(driver, By.XPATH, label)
        if tap:
            tap.click()
        BadooServices._nextQuiz(driver)
    
    @staticmethod 
    def _how_you_feel_about_kids(driver):
        label = "//label[.//span[contains(text(), 'like them someday')]]"
        Utils.perform_action(driver, By.XPATH, label, 'click')
        BadooServices._nextQuiz(driver)
    
    @staticmethod 
    def _education_level(driver):
        BadooServices.sleep_code(3,6)
        label = "//label[.//span[contains(text(), 'Graduate degree or higher')]]"
        Utils.perform_action(driver, By.XPATH, label, 'click')
        BadooServices._nextQuiz(driver)
    
    @staticmethod 
    def _extrovert_or_introvert(driver):
        
        options = [
            "//label[.//span[contains(text(), 'Introvert')]]",
            "//label[.//span[contains(text(), 'Extrovert')]]",
        ]
        number = random.randint(0, len(options) - 1)
        label = options[number]
        Utils.perform_action(driver, By.XPATH, label, 'click')
        BadooServices._nextQuiz(driver)
    
    @staticmethod 
    def _signus(driver, day, month):
        Utils.perform_action(driver, By.XPATH, "//", 'execute_script', 'window.scrollTo(0,200)')
        signus = Utils.get_star_sign(day=int(day), month=int(month))
        label = f"//label[.//span[contains(text(), '{signus}')]]"
        Utils.perform_action(driver, By.XPATH, label, 'click')
        BadooServices._nextQuiz(driver)

    @staticmethod
    def _bio(driver):
        with open(BadooServices.TALK_ABOUT_PATH, 'r') as file:
            unis = file.readlines()
        choose = random.choice(unis).strip()
        Utils.perform_action(driver, By.ID, 'about-textarea', "send_keys", choose)
        BadooServices._nextQuiz(driver)
    
    @staticmethod
    def _return_data():
        return BadooServices._data

