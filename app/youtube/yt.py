import os
from pytube import YouTube

dir = os.path.abspath(os.curdir)

def download_YT(url: str, chatid: str, ismp3: bool) -> object:
    try:
        duration = YouTube(url).length
        if duration > 600:
            return 'Video too long'
        else:
            if ismp3:
                audio = YouTube(url).streams.filter(only_audio=True).first().download(output_path=f'{dir}/downloads/', filename=f'{chatid}.mp3')
                return audio
            else:
                video = YouTube(url).streams.filter(subtype='mp4', resolution='720p').first().download(output_path=f'{dir}/downloads/', filename=f'{chatid}.mp4')
                return video

    except Exception as e:
        print(e)




