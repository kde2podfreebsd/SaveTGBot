from tiktok_downloader import snaptik
import requests
from dotenv import load_dotenv
import os

config = load_dotenv()

downloads_pwd = os.getenv("downloads_pwd")

def upload_video_tt(chat_id:str, url:str):
    try:
        d = snaptik(url)
        d.get_media()[0].download(f"{downloads_pwd}{chat_id}.mp4")
        stat =  os.stat(f'{downloads_pwd}{chat_id}.mp4')
        print(stat.st_size / (1024 * 1024))
        return f'{downloads_pwd}{chat_id}.mp4'
    except Exception as e:
        return "not found"
