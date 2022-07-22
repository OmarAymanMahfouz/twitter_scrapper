from config import *

from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By

import os
from time import sleep
from math import ceil
from datetime import datetime
from pathlib import Path
import json
import pickle

try:
    current_path = os.path.dirname(os.path.abspath(__file__))
except:
    current_path = '.'
    
    
def init_driver(gecko_driver='', user_agent='', load_images=True, is_headless=False):
    firefox_profile = webdriver.FirefoxProfile()
    
    firefox_profile.set_preference('dom.ipc.plugins.enabled.libflashplayer.so', False)
    firefox_profile.set_preference("media.volume_scale", "0.0")
    firefox_profile.set_preference("dom.webnotifications.enabled", False)
    if user_agent != '':
        firefox_profile.set_preference("general.useragent.override", user_agent)
    if not load_images:
        firefox_profile.set_preference('permissions.default.image', 2)

    options = Options()
    options.headless = is_headless
    
    driver = webdriver.Firefox(options=options,
                               executable_path=f'{current_path}/{gecko_driver}',
                               firefox_profile=firefox_profile)
    
    return driver
    
def get_url(page_url, driver):
    driver.get(page_url)
    
    sleep(page_load_timeout)
    
    close_popup = driver.find_elements(By.CSS_SELECTOR,'.-close_popup')
    if len(close_popup) > 0:
        close_popup[0].click()
        
    return True


def load_cookies(driver):
    
    driver.get(twitter_url)
    
    try:
        cookie_file = open("twitter_cookies.pkl", "rb")
    except Exception as e:
        print(str(e))
        return False

    try:
        with cookie_file as f:
            unpickler = pickle.Unpickler(f)
            cookies = unpickler.load()
            # if not isinstance(cookies, dict):
            #     cookies = {}
    except Exception as e:
        print(str(e))
        return False


    if len(cookies) == 0:
        return False
        
    for cookie in cookies:
        driver.add_cookie(cookie)
        
    sleep(2)
    
    driver.get(f"{twitter_url}/settings/account")
    if len(driver.find_elements(By.CLASS_NAME,'r-30o5oe.r-1niwhzg.r-17gur6a.r-1yadl64.r-deolkf.r-homxoj.r-poiln3.r-7cikom.r-1ny4l3l.r-t60dpp.r-1dz5y72.r-fdjqy7.r-13qz1uu')) > 0:
        _ = open(cookie_file, 'w').truncate()
        return False
    else:
        return True

def twitter_login(driver):
    driver.get(twitter_login_page)
    
    if len(driver.find_elements(By.CSS_SELECTOR,'input.js-username-field')) > 0 and len(driver.find_elements(By.CSS_SELECTOR,'input.js-password-field')) > 0:
        email = driver.find_elements(By.CSS_SELECTOR, 'input.js-username-field')[0]
        password = driver.find_elements(By.CSS_SELECTOR, 'input.js-password-field')[0]

        email.clear()
        password.clear()

        email.send_keys( twitter_email )
        password.send_keys( twitter_password )

        sleep(3)
        login_btn = driver.find_elements(By.CSS_SELECTOR,'button[type="submit"]')[0].click()

        sleep(5)
        cookies_list = driver.get_cookies()

        ck_file = open(f"{current_path}/{twitter_cookies_path}",'w', encoding='utf8')
        ck_file.write( json.dumps( cookies_list ) )
        ck_file.close()
    
    return True