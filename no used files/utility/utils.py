# utils.py
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import StaleElementReferenceException, TimeoutException, NoSuchElementException



class Utils:
    @staticmethod
    def wait_for_elements_visible(driver, by, value, timeout=20):
        try:
            return WebDriverWait(driver, timeout).until(
            EC.visibility_of_all_elements_located((by, value))
            )

        except NoSuchElementException as e:
            print(f"Error: Element {value} not found")
            return None
        except Exception as e:
            print("something wrong")
            return None
    
    
    @staticmethod
    def find_element_without_delay(driver, by, value):
        element = driver.find_element(by, value)
        if element:
            return element
        else:
            return None
        
    @staticmethod
    def perform_action_raise_an_execption(driver, by, value, action, *args, timeout=10):
            try:
                element = WebDriverWait(driver, timeout).until(EC.visibility_of_element_located((by, value)))
                if action == 'execute_script':
                    driver.execute_script(*args)
                else:
                    if action == 'click':
                        element.click()
                    elif action == 'send_keys':
                        element.send_keys(*args)
                    else:
                        print(f"Error: Unsupported action {action}")
            except Exception as e:
                raise
    @staticmethod
    def perform_action(driver, by, value, action, *args, timeout=10):
        try:
            if action == 'execute_script':
                driver.execute_script(*args)
            else:
                element = Utils.wait_for_element(driver, by, value, timeout)
                if action == 'click':
                    element.click()
                elif action == 'send_keys':
                    element.send_keys(*args)
                
                else:
                    print(f"Error: Unsupported action {action}")
        except NoSuchElementException:
            print(f"Error: Element {value} not found")
        except StaleElementReferenceException:
            print(f"Error: Stale element reference {value}")
        except Exception as e:
            print(f"Error: Exception occurred for element {value} - {e}")

    @staticmethod
    def wait_for_element(driver, by, value, timeout=10):
        try:
            return WebDriverWait(driver, timeout).until(EC.visibility_of_element_located((by, value)))
        except TimeoutException:
            print(f"Error: Timeout while waiting for element {value}")
            return None

    @staticmethod
    def wait_for_element_visible(driver, by, value, timeout=20):
        return WebDriverWait(driver, timeout).until(
            EC.visibility_of_element_located((by, value))
        )

    
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