# SocMediaScrapper Telegram Bot 
## Test the bot now - [@UzSavebot](https://t.me/UzSavebot)
------------------------

## Upload video from
* Youtube [.mp3; max duration: 10 min]
* Youtube Shorts [.mp4]
* Tik-Tok [without watermark]
* Instagram [stories, posts(photo,video,carousel), reels] (dont work for highlight)
-----------
### [Miro design - Miro desk of application architecture](https://miro.com/app/board/uXjVPU7fviQ=/)
-----------
### Configs Example
#### .env (.env-example) 
##### pwd - full os path to dir of project
```.env
Local
TG_API_KEY=''
downloads_pwd='{pwd}/app/downloads/'
ad_pwd='{pwd}/app/Ads'
inst_url = 'https://ru.savefrom.net/94/download-from-instagram'
tt_url = 'https://ru.savefrom.net/79/download-from-tiktok'
DRIVER = '{pwd}/app/chromedriver'


admin_pass = '12345'
referal = 'https://t.me/UzSavebot?start='
banner='Скачано из @UzSavebot'

channel_link = 'https://t.me/Tezkor_tg'
channel_username = '@CryptoVedma' #Tezkor_tg
```


### Install 

#### 1. Install requirements
```.sh
cd/app
pip install -r requirements.txt
```

#### 2. Rebuild database:db.sqlite
```.sh
./dbmanager rebuild
```

#### 3. Start the app 
```.sh
python bot.py
# or (infinity restart app if it crash)
./restarter.sh
```

### Install chromedriver 
#### Helpful links
* https://omahaproxy.appspot.com/ - check Branch Base Position for google version
* https://chromedriver.storage.googleapis.com/index.html - download from archive 
* https://commondatastorage.googleapis.com/chromium-browser-snapshots/index.html?prefix=Linux_x64/Branch Base Position/ - download by Branch Base Position

### No CLI Server
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
-------------------------------

### Admin panel 
#### For auth in bot like admin write to the bot:
``` .txt 
/admin 12345
```
#### U can chage pass in .env file for auth like admin role
!
