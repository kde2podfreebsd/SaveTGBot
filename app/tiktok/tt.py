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
        return f'{downloads_pwd}{chat_id}.mp4'
    except Exception as e:
        return 'not found'
        
# def upload_video_tt(chat_id: str, url: str):
#     try:
#         src = get_src(url = url)
#         if src == 'not found':
#             return 'not found'
#         else:
#             print(f'request to {src}')
#             r = requests.get(src, allow_redirects=True)
#             print(f'write content on disk: {downloads_pwd}{chat_id}.mp4')
#             open(f'{downloads_pwd}{chat_id}.mp4', 'wb').write(r.content)
#             return f'{chat_id}.mp4'

#     except Exception as e:
#         return 'not found'
