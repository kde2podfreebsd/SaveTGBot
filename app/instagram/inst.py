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
from pyvirtualdisplay import Display

config = load_dotenv()

downloads_pwd = os.getenv("downloads_pwd")
inst_url = os.getenv("inst_url")
DRIVER = os.getenv("DRIVER")

ser = Service(DRIVER)
op = webdriver.ChromeOptions()

def get_src(url:str):
    try:
        op.add_argument("--no-sandbox");
        op.add_argument("--disable-dev-shm-usage");
        display = Display(visible=0, size=(800, 800))
        display.start()
        src = list()
        data_type_list = list()
        driver = webdriver.Chrome(service=ser, options=op)
        driver.get(inst_url)
        time.sleep(2)
        input = driver.find_element(by=By.ID, value="sf_url")
        input.send_keys(url)
        time.sleep(1)
        driver.find_element(by=By.ID, value="sf_submit").click()
        try:
            source = EC.presence_of_all_elements_located((By.XPATH, '//div[@class="def-btn-box"]'))
            def_btn_box = WebDriverWait(driver, 30).until(source)
            download_source = []
            for data in def_btn_box:
                link = data.find_element(by=By.TAG_NAME, value='a')
                download_source.append(link)
            for i in range(len(download_source)):
                src.append(download_source[i].get_attribute('href'))
                data_type_list.append(download_source[i].get_attribute('data-type'))
            return src, data_type_list
        except TimeoutException:
            print(TimeoutException)
            return 'not found', 'not found'
    except Exception as e:
        print(e)
        return 'not found', 'not found'

    finally:
        driver.close()
        driver.quit()
        display.stop()

def upload_video_inst(chat_id: str, url: str):
    try:
        files_paths = list()
        src, data_type_list = get_src(url = url)
        print(src, data_type_list)
        if src == 'not found':
            return 'not found'
        else:
            for i in range(len(src)):
                print(f'request to {src[i]}')
                r = requests.get(src[i], allow_redirects=True)
                if data_type_list[i] == 'webp':
                    print(f'write content on disk: {downloads_pwd}{i}.jpg')
                    open(f'{downloads_pwd}{chat_id}{i}.jpg', 'wb').write(r.content)
                    files_paths.append(f'{chat_id}{i}.jpg')
                else:
                    print(f'write content on disk: {downloads_pwd}{chat_id}{i}.{data_type_list[i]}')
                    open(f'{downloads_pwd}{chat_id}{i}.{data_type_list[i]}', 'wb').write(r.content)
                    files_paths.append(f'{chat_id}{i}.{data_type_list[i]}')
            return files_paths
    except Exception as e:
        print(e)
        return 'not found'

# print(get_src(url = 'https://instagram.com/stories/dayakouz/2948152636196930861?utm_source=ig_story_item_share&igshid=MDJmNzVkMjY='))
