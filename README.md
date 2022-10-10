# SocMediaScrapper Telegram Bot
------------------------

## Upload video from
* Youtube [.mp3; max duration: 10 min]
* Tik-Tok [without tt watermark]
* Instagram [stories, posts(photo,video,carousel), reels] (dont work for highlight)
--------------------
### Configs Example
#### .env
```.env
TG_API_KEY=''
downloads_pwd='{$pwd}/app/downloads/'
ad_pwd='{$pwd}/app/Ads'
inst_url = 'https://ru.savefrom.net/94/download-from-instagram'
tt_url = 'https://ru.savefrom.net/79/download-from-tiktok'
DRIVER = '{$pwd}/app/chromedriver'
admin_pass = '12345'
referal = 'https://t.me/inst_yt_tt_bot?start='
banner='Скачано из @inst_yt_tt_bot'
```

#### config.ini
```.ini
[Telegram]
api_id = 00000000
api_hash = 0000000000000000000000000000000
username = username
proxy_server = 123.456.78.90
proxy_port = 123
proxy_key = -----BEGIN RSA PUBLIC KEY-----{...}-----END RSA PUBLIC KEY-----"
```
----------------------

### Install 
#### 1. 
```.sh
cd/app
./dbmanager rebuild
```

#### 2.
```.sh
python bot.py
```
-------------------------
### Install chromedriver 
#### Helpful links
* https://omahaproxy.appspot.com/ | check Branch Base Position for google version
* https://chromedriver.storage.googleapis.com/index.html | download from archive 
* https://commondatastorage.googleapis.com/chromium-browser-snapshots/index.html?prefix=Linux_x64/Branch Base Position/ | download by Branch Base Position

-----------------------------------------
### Running on no-CLI server
##### On cli server use this options
```.py
from pyvirtualdisplay import Display

op.add_argument("--no-sandbox");
        op.add_argument("--disable-dev-shm-usage");
        display = Display(visible=0, size=(800, 800))
        display.start()

        .....

        finally:
            ...
            display.stop()
```

