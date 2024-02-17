from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, ElementClickInterceptedException, ElementNotVisibleException
from selenium.common.exceptions import ElementNotInteractableException, TimeoutException, StaleElementReferenceException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options

from webdriver_manager.chrome import ChromeDriverManager
from image_processing import removeIsland

import numpy as np 
import base64
from io import BytesIO
from PIL import Image
import pytesseract
import cv2

import config
import logging
import requests

import os

class TelegramLoggingHandler(logging.Handler):
    def __init__(self, token, chat_id):
        super().__init__()
        self.token = token
        self.chat_id = chat_id
        self.telegram_api_url = f"https://api.telegram.org/bot{token}/sendMessage"

    def emit(self, record):
        log_entry = self.format(record)
        payload = {
            'chat_id': self.chat_id,
            'text': log_entry,
            'parse_mode': 'HTML'
        }
        try:
            requests.post(self.telegram_api_url, data=payload)
        except requests.exceptions.RequestException as e:
            print(f"Error sending log entry to Telegram: {e}")

pytesseract.pytesseract.tesseract_cmd = config.TESSERACT_PATH


class QueueChecker:
    def __init__(self, kdmid_subdomain, order_code_pairs):
        self.kdmid_subdomain = kdmid_subdomain
        self.order_code_pairs = order_code_pairs  # List of tuples (order_id, code)
        self.image_name = 'captcha_processed.png'
        self.screen_name = "screenshot0.png"
        self.button_dalee = "//input[@id='ctl00_MainContent_ButtonA']"
        self.button_b = "//input[@id='ctl00_MainContent_ButtonB']"
        self.main_button_id = "//input[@id='ctl00_MainContent_Button1']"
        self.text_form = "//input[@id='ctl00_MainContent_txtCode']"
        self.checkbox = "//input[@id='ctl00_MainContent_RadioButtonList1_0']"
        self.token = '<Telegram Bot Token>'
        self.chat_id = '<Telegram Chat ID>'
        self.telegram_handler = TelegramLoggingHandler(self.token, self.chat_id)
        # self.formatter = logging.Formatter('%(asctime)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
        # self.telegram_handler.setFormatter(self.formatter)

        self.logger = logging.getLogger('telegram_logger')
        self.logger.setLevel(logging.INFO)
        self.logger.addHandler(self.telegram_handler)


    def write_success_file(self, text): 
        with open(self.order_id+"_"+self.code+"_success.txt", mode = "w", encoding="utf-8") as f:
            f.write(text)       
        
    def check_exists_by_xpath(self, xpath, driver):
        mark = False
        try:
            driver.find_element(By.XPATH, xpath)
            mark = True
            return mark
        except NoSuchElementException:
            return mark
       
    def get_driver(self): 
        chrome_options = Options()
        chrome_options.add_argument("--headless")  # Ensure GUI is off
        chrome_options.add_argument("--no-sandbox")  # Bypass OS security model
        chrome_options.add_argument("--disable-dev-shm-usage")  # Overcome limited resource problems
        driver = webdriver.Chrome(executable_path='/usr/local/bin/chromedriver', options=chrome_options)
        return driver
    
    def screenshot_captcha(self, driver, error_screen=False): 
        # Detect the image of the captcha and get it's position
        element = driver.find_element(By.XPATH, '//img[@id="ctl00_MainContent_imgSecNum"]')
        loc  = element.location
        size = element.size
        left = loc['x']
        top = loc['y']
        right = (loc['x'] + size['width'])
        bottom = (loc['y'] + size['height'])
	
        driver.save_screenshot("screenshot.png")	
        screenshot = driver.get_screenshot_as_base64()
        img = Image.open(BytesIO(base64.b64decode(screenshot)))
        #Get size of the part of the screen visible in the screenshot
        screensize = (driver.execute_script("return document.body.clientWidth"), 
		              driver.execute_script("return window.innerHeight"))
        img = img.resize(screensize)
        
        box = (int(left), int(top), int(right), int(bottom))
        area = img.crop(box)
        area.save(self.screen_name, 'PNG')
	
        #process saved image to make it more contrast
        img  = cv2.imread(self.screen_name)
        # Convert to grayscale
        c_gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
        # Median filter
        out = cv2.medianBlur(c_gray,1)
        # Image thresholding 
        a = np.where(out>228, 1, out)
        out = np.where(a!=1, 0, a)
        # Islands removing with threshold = 30
        out = removeIsland(out, 30)
        # Median filter
        out = cv2.medianBlur(out,3)
        cv2.imwrite(self.image_name, out*255)
    
    def recognize_image(self): 
        digits = pytesseract.image_to_string(self.image_name, config='--psm 10 --oem 3 -c tessedit_char_whitelist=0123456789')
        return digits

    def check_queue(self):
        for order_id, code in self.order_code_pairs:
            if os.path.isfile(f"{order_id}_{code}_success.txt"):
                self.logger.info(f"Order {order_id}: Appointment found, skipping")
                continue
            self.order_id = order_id
            self.code = code
            self.url = 'http://'+self.kdmid_subdomain+'.kdmid.ru/queue/OrderInfo.aspx?id='+self.order_id+'&cd='+self.code
            driver = self.get_driver()
            driver.maximize_window()
            try: 
                driver.get(self.url) 
            except:
                self.logger.info(f"{self.order_id}: Failed to load order page")
            # self.logger.info(f"——————— Order {self.order_id} ––––––––")
            # self.logger.info(f"{self.order_id}: Page loaded")
            
            error = True
            error_screen = False
            # iterate until captcha is recognized 
            while error: 
                self.screenshot_captcha(driver, error_screen)
                digits = self.recognize_image()
                WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.XPATH, self.text_form))).send_keys(str(digits))
            
                if self.check_exists_by_xpath(self.button_dalee, driver): 
                    driver.find_element(By.XPATH, self.button_dalee).click()
                
                if self.check_exists_by_xpath(self.button_b, driver): 
                    driver.find_element(By.XPATH, self.button_b).click()
                
                window_after = driver.window_handles[0]
                driver.switch_to.window(window_after)
                error = False
                # self.logger.info(f"{self.order_id}: Try entering captcha")
                
                try: 
                   driver.find_element(By.XPATH, self.main_button_id)    
                except: 
                    # self.logger.info(f"{self.order_id}: Captcha not accepted. Trying again")
                    error = True
                    error_screen = True
                    driver.find_element(By.XPATH, self.text_form).clear()
                    
            # self.logger.info(f"{self.order_id}: Captcha accepted. Checking timeslots")
            if self.check_exists_by_xpath(self.checkbox, driver): 
            # if success, take the first available timeslot
                driver.find_element(By.XPATH,self.checkbox).click()
                check_box = driver.find_element(By.XPATH, self.checkbox)
                val = check_box.get_attribute("value")
                self.logger.info(f"Order {self.order_id}: Appointment booked for: {val}")
                WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.XPATH, self.main_button_id))).click()  
            # write success file to stop iterating
                self.write_success_file(str(val))			
            else: 
                self.logger.info(f"Order {self.order_id}: Checked. No free timeslots for now")
                
            driver.quit()
