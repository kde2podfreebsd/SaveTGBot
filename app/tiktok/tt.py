from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import requests
from dotenv import load_dotenv
import os
# from pyvirtualdisplay import Display

config = load_dotenv()

downloads_pwd = os.getenv("downloads_pwd")
tt_url = os.getenv("tt_url")
DRIVER = os.getenv("DRIVER")

ser = Service(DRIVER)
op = webdriver.ChromeOptions()

def get_src(url:str):
    try:
        # op.add_argument("--no-sandbox");
        # op.add_argument("--disable-dev-shm-usage");
        # display = Display(visible=0, size=(800, 800))
        # display.start()
        driver = webdriver.Chrome(service=ser, options=op)
        driver.get(tt_url)
        time.sleep(2)
        input = driver.find_element(by=By.ID, value="sf_url")
        input.send_keys(url)
        time.sleep(1)
        driver.find_element(by=By.ID, value="sf_submit").click()
        try:
            source = EC.presence_of_element_located((By.CLASS_NAME, 'link-download'))
            download_source = WebDriverWait(driver, 30).until(source)
            print(download_source.get_attribute('href'))
            return download_source.get_attribute('href')
        except TimeoutException:
            print(TimeoutException)

    except Exception as e:
        print(e)
        return 'not found'

    finally:
        driver.close()
        driver.quit()
        # display.stop()
        
def upload_video_tt(chat_id: str, url: str):
    try:
        src = get_src(url = url)
        if src == 'not found':
            return 'not found'
        else:
            print(f'request to {src}')
            r = requests.get(src, allow_redirects=True)
            print(f'write content on disk: {downloads_pwd}{chat_id}.mp4')
            open(f'{downloads_pwd}{chat_id}.mp4', 'wb').write(r.content)
            return f'{chat_id}.mp4'

    except Exception as e:
        return 'not found'
