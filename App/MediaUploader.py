import os
import urlextract
from typing import List, Union, Tuple
from tiktok_downloader import snaptik
from pytube import YouTube
from selenium import webdriver
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.common.by import By
from webdriver_manager.firefox import GeckoDriverManager
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import requests


class MediaUploader(object):

    saveFormNetInstURL = 'https://ru.savefrom.net/132/download-from-instagram'
    extractor = urlextract.URLExtract()

    @classmethod
    def find_urls(cls, text: str) -> List[Union[str, Tuple[str, Tuple[int, int]]]]:
        return cls.extractor.find_urls(text)

    @classmethod
    def select_service_type(cls, url: str) -> str:
        serviceTypes = ['youtube_shorts', 'instagram', 'youtube', 'tiktok']

        if url.find('tiktok') == -1:
            serviceTypes.remove('tiktok')

        if url.find('instagram') == -1:
            serviceTypes.remove('instagram')

        if url.find('youtube.com/shorts') == -1 and url.find('youtu.be.com/shorts') == -1:
            serviceTypes.remove('youtube_shorts')

        if url.find('youtube') == -1 and url.find('youtu.be') == -1:
            serviceTypes.remove('youtube')

        if url.find('playlist') != -1:
            serviceTypes.remove('youtube')

        if len(serviceTypes) == 0:
            return False
        else:
            return serviceTypes[0]

    @classmethod
    def TikTok(url: str, chat_id: int) -> str:
        path = f'{os.getenv("PWD")}/files/{chat_id}.mp4'
        d = snaptik(url)
        d[0].download(path)
        return path

    @classmethod
    def YouTube(url: str, chat_id: int, isMP3: bool):
        duration = YouTube(url).length
        if duration > 600:
            return 'Video too long'
        else:
            if isMP3:
                path = f'{os.getenv("PWD")}/files/'
                audio = YouTube(url).streams.filter(only_audio=True).first().download(
                    output_path=path, filename=f'{chat_id}.mp3')
                print(audio)
                return audio
            else:
                path = f'{os.getenv("PWD")}/files/'
                video = YouTube(url).streams.filter(subtype='mp4', resolution='720p').first().download(
                    output_path=path, filename=f'{chat_id}.mp4')
                print(video)
                return video

    @classmethod
    def InstagramSource(cls, url: str):
        try:
            driver = webdriver.Firefox(service=FirefoxService(GeckoDriverManager().install()))
            src, data_type_list = list(), list()
            driver.get(cls.saveFormNetInstURL)
            url_input = driver.find_element(by=By.ID, value="sf_url")
            url_input.send_keys(url)
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
                driver.close()
                return src, data_type_list
            except TimeoutException:
                print(TimeoutException)
                driver.close()
                return 'not found', 'not found'
        except Exception as e:
                print(e)
                return 'not found', 'not found'

    @classmethod
    def Instagram(cls, url: str, chat_id: int):
        path = f'{os.getenv("PWD")}/files/{chat_id}'
        files_paths = list()
        src, data_type = cls.InstagramSource(url=url)
        # src, data_type = ['https://scontent.cdninstagram.com/v/t51.2885-15/62533717_147294506408041_1780171739254908309_n.jpg?stp=dst-jpg_e35&_nc_ht=scontent.cdninstagram.com&_nc_cat=101&_nc_ohc=XdT2TkL6ZL0AX-Pbwbm&edm=APs17CUBAAAA&ccb=7-5&oh=00_AfCfbhATZzhJ7wNoB1hsrc9ScB447BvF__6p81pc7AxO5w&oe=6435A113&_nc_sid=978cb9&dl=1', 'https://scontent.cdninstagram.com/v/t51.2885-15/61178271_681668052277527_2197630245913747744_n.jpg?stp=dst-jpg_e35&_nc_ht=scontent.cdninstagram.com&_nc_cat=103&_nc_ohc=GyTrKtQzNqkAX-TxRso&edm=APs17CUBAAAA&ccb=7-5&oh=00_AfAUt1mKZEeSUbOt4hRuPPAhJ5KSMbxyFTHfag27Ewuaug&oe=64358492&_nc_sid=978cb9&dl=1'], ['jpg', 'jpg']
        if src == 'not found':
            return 'not found'
        else:
            for i in range(len(src)):
                print(f'request to {src[i]}')
                r = requests.get(src[i], allow_redirects=True)
                if data_type[i] == 'webp':
                    open(f'{path}{i}.jpg', 'wb').write(r.content)
                    files_paths.append(f'{path}{i}.jpg')
                else:
                    open(f'{path}{i}.{data_type[i]}', 'wb').write(r.content)
                    files_paths.append(f'{path}{i}.{data_type[i]}')
            return files_paths

# print(MediaUploader.select_service_type(url="https://vt.tiktok.com/ZS8tFm6ac/"))
# print(MediaUploader.find_urls(text='https://www.youtube.com/ 123https://cloud.reg.ru/panel/87711675/servers'))
# print(MediaUploader.TikTok(url="https://vt.tiktok.com/ZS8tFm6ac/", chat_id=123))
# print(MediaUploader.YouTube(url="https://www.youtube.com/watch?v=smqhSl0u_sI", chat_id=123, isMP3=True))
# print(MediaUploader.InstagramSource(url='https://www.instagram.com/p/Byaz4wqiR4R/?igshid=YmMyMTA2M2Y='))

