import os
import telebot
from telebot import types
from bot import markups as mp
from dotenv import load_dotenv
import urlextract
import subprocess
from youtube import download_YT
from tiktok import upload_video_tt
from instagram import upload_video_inst
from subChecker import check
from database import dbworker as db
from datetime import date
from pathlib import Path
from random import randrange

extractor = urlextract.URLExtract()

config = load_dotenv()
bot = telebot.TeleBot(os.getenv("TG_API_KEY"))

users = dict()
ads = {'shortname': '', 'text':'', 'file_path':'', 'media_type':'', 'btn_text': '', 'btn_url':''}
language_list = dict()
sub_status = False
ad_status = False
channel_link = ' https://t.me/inst_yt_tt_bot'
# https://t.me/inst_yt_tt_bot?start=token
@bot.message_handler(commands=['start'])
def start(message) -> None:
    try:
        unique_code = extract_unique_code(message.text)
        if unique_code == None:
            db.init_user(chat_id=message.chat.id, username=message.chat.username, date_of_join=date_today(), referal_code='N/A')
        else:
            db.init_user(chat_id=message.chat.id, username=message.chat.username, date_of_join=date_today(),referal_code=unique_code)
        bot.send_message(message.chat.id, mp.menu_message, reply_markup=mp.off_markup, parse_mode='MARKDOWN')

    except Exception as e:
        bot.reply_to(message, f'{e}')

@bot.message_handler(commands=['language'])
def language(message) -> None:
    try:
        msg = bot.send_message(message.chat.id, "Выберите язык", reply_markup=mp.language, parse_mode='MARKDOWN')
        bot.register_next_step_handler(msg, set_language)

    except Exception as e:
        bot.reply_to(message, f'{e}')

def set_language(message):
    language_list[message.chat.id] = message.text
    bot.send_message(message.chat.id, f"Language:{language_list[message.chat.id]}", reply_markup=mp.off_markup, parse_mode='MARKDOWN')
    bot.send_message(message.chat.id, mp.menu_message, reply_markup=mp.off_markup, parse_mode='MARKDOWN')

@bot.message_handler(commands=['admin', 'admin_menu'])
def admin(message) -> None:
    try:
        unique_code = extract_unique_code(message.text)
        if db.is_admin(chat_id=message.chat.id):
            bot.send_message(message.chat.id, f'Admin: {message.chat.username}', reply_markup=mp.menu_admin, parse_mode='MARKDOWN')
        elif db.is_admin(chat_id=message.chat.id) == False and unique_code == os.getenv("admin_pass"):
            db.init_admin(chat_id=message.chat.id)
            bot.send_message(message.chat.id, f'Admin: {message.chat.username}', reply_markup=mp.menu_admin,parse_mode='MARKDOWN')
        else:
            bot.send_message(message.chat.id, mp.not_admin, reply_markup=mp.off_markup, parse_mode='MARKDOWN')
    except Exception as e:
        bot.reply_to(message, f'{e}')

@bot.message_handler(commands=['stat'])
def stat(message) -> None:
    try:
        if db.is_admin(chat_id=message.chat.id):
            stat = db.get_stat()
            # print(stat)
            msg = mp.get_stat_msg(
                number_of_users = stat['number_of_users'],
                users_today=stat['users_today'],
                all_downloads=stat['all_downloads'],
                today_downloads=stat['today_downloads'],
                youtube=stat['youtube'],
                tiktok=stat['tiktok'],
                instagram=stat['instagram']
            )
            bot.send_message(message.chat.id, msg, reply_markup=mp.menu_admin, parse_mode='MARKDOWN')
        else:
            bot.send_message(message.chat.id, mp.not_admin, reply_markup=mp.off_markup, parse_mode='MARKDOWN')
    except Exception as e:
        bot.reply_to(message, f'{e}')

@bot.message_handler(commands=['create_referal'])
def create_referal(message) -> None:
    try:
        if db.is_admin(chat_id=message.chat.id):
            msg = bot.send_message(message.chat.id, 'Введите название для реферальной ссылки', reply_markup=mp.off_markup, parse_mode='MARKDOWN')
            bot.register_next_step_handler(msg, init_referal)
        else:
            bot.send_message(message.chat.id, mp.not_admin, reply_markup=mp.off_markup, parse_mode='MARKDOWN')
    except Exception as e:
        bot.reply_to(message, f'{e}')

def init_referal(message):
    try:
        uid = db.init_referal(name = message.text)
        bot.send_message(message.chat.id, f'{message.text}: {os.getenv("referal")}{uid}', reply_markup=mp.menu_admin, parse_mode='html')
    except Exception as e:
        bot.reply_to(message, f'{e}')

@bot.message_handler(commands=['referal_stat'])
def referal_stat(message) -> None:
    try:
        if db.is_admin(chat_id=message.chat.id):
            data = db.get_referal_stat()
            msg = referal_stat_msg(data)
            bot.send_message(message.chat.id, msg, reply_markup=mp.menu_admin, parse_mode='MARKDOWN')
        else:
            bot.send_message(message.chat.id, mp.not_admin, reply_markup=mp.off_markup, parse_mode='MARKDOWN')
    except Exception as e:
        bot.reply_to(message, f'{e}')

@bot.message_handler(commands=['subscription'])
def subscription(message) -> None:
    try:
        if db.is_admin(chat_id=message.chat.id):
            global channel_link
            global sub_status
            bot.send_message(message.chat.id, f'Выберите действие\n\nchannel: {channel_link}\nstatus: {sub_status}', reply_markup=mp.subscription, parse_mode='html')
        else:
            bot.send_message(message.chat.id, mp.not_admin, reply_markup=mp.off_markup, parse_mode='MARKDOWN')
    except Exception as e:
        bot.reply_to(message, f'{e}')

@bot.message_handler(commands=['turn_on_subscription'])
def turn_on_subscription(message) -> None:
    try:
        if db.is_admin(chat_id=message.chat.id):
            global sub_status
            sub_status = True
            bot.send_message(message.chat.id, 'Обязательная подписка включена!', reply_markup=mp.subscription, parse_mode='MARKDOWN')
        else:
            bot.send_message(message.chat.id, mp.not_admin, reply_markup=mp.off_markup, parse_mode='MARKDOWN')
    except Exception as e:
        bot.reply_to(message, f'{e}')

@bot.message_handler(commands=['turn_off_subscription'])
def turn_off_subscription(message) -> None:
    try:
        if db.is_admin(chat_id=message.chat.id):
            global sub_status
            sub_status = False
            bot.send_message(message.chat.id, 'Обязательная подписка выключена!', reply_markup=mp.subscription, parse_mode='MARKDOWN')
        else:
            bot.send_message(message.chat.id, mp.not_admin, reply_markup=mp.off_markup, parse_mode='MARKDOWN')
    except Exception as e:
        bot.reply_to(message, f'{e}')

@bot.message_handler(commands=['change_channel'])
def change_channel(message) -> None:
    try:
        if db.is_admin(chat_id=message.chat.id):
            msg = bot.send_message(message.chat.id, mp.change_group, reply_markup=mp.off_markup, parse_mode='MARKDOWN')
            bot.register_next_step_handler(msg, set_new_channel)
        else:
            bot.send_message(message.chat.id, mp.not_admin, reply_markup=mp.off_markup, parse_mode='MARKDOWN')
    except Exception as e:
        bot.reply_to(message, f'{e}')

def set_new_channel(message):
    try:
        if db.is_admin(chat_id=message.chat.id):
            global channel_link
            channel_link = message.text
            bot.send_message(message.chat.id, f'Changed to {channel_link}', reply_markup=mp.subscription, parse_mode='html')
        else:
            bot.send_message(message.chat.id, mp.not_admin, reply_markup=mp.off_markup, parse_mode='MARKDOWN')
    except Exception as e:
        bot.reply_to(message, f'{e}')

@bot.message_handler(commands=['mail_users'])
def mail_users(message) -> None:
    try:
        if db.is_admin(chat_id=message.chat.id):
            msg = bot.send_message(message.chat.id, mp.mail_users_msg, reply_markup=mp.off_markup, parse_mode='MARKDOWN')
            bot.register_next_step_handler(msg, mail_users_send)
        else:
            bot.send_message(message.chat.id, mp.not_admin, reply_markup=mp.off_markup, parse_mode='MARKDOWN')
    except Exception as e:
        bot.reply_to(message, f'{e}')

def mail_users_send(message):
    try:
        users = db.get_users()
        for i in range(len(users)):
            bot.send_message(users[i].chat_id, message.text, reply_markup=mp.off_markup, parse_mode='MARKDOWN')
    except Exception as e:
        pass

@bot.message_handler(commands=['ads'])
def ads_menu(message) -> None:
    try:
        if db.is_admin(chat_id=message.chat.id):
            global ad_status
            bot.send_message(message.chat.id, f'Выберите действие\n\nstatus: {ad_status}', reply_markup=mp.ads_menu, parse_mode='MARKDOWN')
        else:
            bot.send_message(message.chat.id, mp.not_admin, reply_markup=mp.off_markup, parse_mode='MARKDOWN')
    except Exception as e:
        bot.reply_to(message, f'{e}')

@bot.message_handler(commands=['turn_on_ads'])
def turn_on_ads(message) -> None:
    try:
        if db.is_admin(chat_id=message.chat.id):
            global ad_status
            ad_status = True
            bot.send_message(message.chat.id, 'Реклама включена!', reply_markup=mp.ads_menu, parse_mode='MARKDOWN')
        else:
            bot.send_message(message.chat.id, mp.not_admin, reply_markup=mp.off_markup, parse_mode='MARKDOWN')
    except Exception as e:
        bot.reply_to(message, f'{e}')

@bot.message_handler(commands=['turn_off_ads'])
def turn_off_ads(message) -> None:
    try:
        if db.is_admin(chat_id=message.chat.id):
            global ad_status
            ad_status = False
            bot.send_message(message.chat.id, 'Реклама выключена!', reply_markup=mp.ads_menu, parse_mode='MARKDOWN')
        else:
            bot.send_message(message.chat.id, mp.not_admin, reply_markup=mp.off_markup, parse_mode='MARKDOWN')
    except Exception as e:
        bot.reply_to(message, f'{e}')

@bot.message_handler(commands=['new_ad'])
def new_ad(message) -> None:
    try:
        if db.is_admin(chat_id=message.chat.id):
            msg = bot.send_message(message.chat.id, "Укажите короткое имя для нового рекламного поста", reply_markup=mp.off_markup, parse_mode='MARKDOWN')
            bot.register_next_step_handler(msg, shortname_ad)
        else:
            bot.send_message(message.chat.id, mp.not_admin, reply_markup=mp.off_markup, parse_mode='MARKDOWN')
    except Exception as e:
        bot.reply_to(message, f'{e}')

def shortname_ad(message):
    try:
        if db.is_admin(chat_id=message.chat.id):
            ads['shortname'] = message.text
            msg = bot.send_message(message.chat.id, "Укажите текст рекламного поста в разметке MARKDOWN", reply_markup=mp.off_markup, parse_mode='MARKDOWN')
            bot.register_next_step_handler(msg, text_ad)
        else:
            bot.send_message(message.chat.id, mp.not_admin, reply_markup=mp.off_markup, parse_mode='MARKDOWN')
    except Exception as e:
        bot.reply_to(message, f'{e}')

def text_ad(message):
    try:
        if db.is_admin(chat_id=message.chat.id):
            ads['text'] = message.text
            msg = bot.send_message(message.chat.id, "Укажите текст inline кнопки, если кнопка не нужна - отправьте 0", reply_markup=mp.off_markup, parse_mode='MARKDOWN')
            bot.register_next_step_handler(msg, btn_text)
        else:
            bot.send_message(message.chat.id, mp.not_admin, reply_markup=mp.off_markup, parse_mode='MARKDOWN')
    except Exception as e:
        bot.reply_to(message, f'{e}')

def btn_text(message):
    try:
        if db.is_admin(chat_id=message.chat.id):
            if message.text == '0':
                ads['btn_text'] = ''
                msg = bot.send_message(message.chat.id,"Прикрепите медиа в формате jpg/jpeg или mp4",reply_markup=mp.off_markup, parse_mode='MARKDOWN')
                bot.register_next_step_handler(msg, handler_file)
            else:
                ads['btn_text'] = message.text
                msg = bot.send_message(message.chat.id, "Укажите ссылку к inline кнопке", reply_markup=mp.off_markup, parse_mode='MARKDOWN')
                bot.register_next_step_handler(msg, btn_url)
        else:
            bot.send_message(message.chat.id, mp.not_admin, reply_markup=mp.off_markup, parse_mode='MARKDOWN')
    except Exception as e:
        bot.reply_to(message, f'{e}')

def btn_url(message):
    try:
        if db.is_admin(chat_id=message.chat.id):
            ads['btn_url'] = message.text
            msg = bot.send_message(message.chat.id, "Прикрепите медиа в формате jpg/jpeg или mp4", reply_markup=mp.off_markup, parse_mode='MARKDOWN')
            bot.register_next_step_handler(msg, handler_file)
        else:
            bot.send_message(message.chat.id, mp.not_admin, reply_markup=mp.off_markup, parse_mode='MARKDOWN')
    except Exception as e:
        bot.reply_to(message, f'{e}')

@bot.message_handler(content_types=['photo', 'document'])
def handler_file(message):
    try:
        if db.is_admin(chat_id=message.chat.id):
            Path(f'files/{message.chat.id}/').mkdir(parents=True, exist_ok=True)
            if message.content_type == 'photo':
                file_info = bot.get_file(message.photo[len(message.photo) - 1].file_id)
                downloaded_file = bot.download_file(file_info.file_path)
                src = f"{os.getenv('ad_pwd')}/{ads['shortname']}.jpg"
                with open(src, 'wb') as new_file:
                    new_file.write(downloaded_file)
                ads['file_path'] = src
                ads['media_type'] = 'jpg'
                bot.send_message(message.chat.id, f"Изображение загружено",reply_markup=mp.off_markup, parse_mode='html')
            if message.content_type == 'video':
                file_info = bot.get_file(message.photo[len(message.photo) - 1].file_id)
                downloaded_file = bot.download_file(file_info.file_path)
                src = f"{os.getenv('ad_pwd')}/{ads}.mp4"
                with open(src, 'wb') as new_file:
                    new_file.write(downloaded_file)
                ads['file_path'] = src
                ads['media_type'] = 'mp4'
                bot.send_message(message.chat.id, f"Видео загружено", reply_markup=mp.off_markup, parse_mode='html')

            media = open(f"{ads['file_path']}", 'rb')
            if ads['btn_text'] == '':
                bot.send_document(message.chat.id, media, caption=ads['text'], reply_markup=mp.off_markup,parse_mode='MARKDOWN')
            else:
                markup = mp.get_inline_url_btn(text=ads['btn_text'], url=ads['btn_url'])
                bot.send_document(message.chat.id, media, caption=ads['text'], reply_markup=markup, parse_mode='MARKDOWN')

            bot.send_message(message.chat.id, f"short name: {ads['shortname']} - Confirm?", reply_markup=mp.confirm_ad, parse_mode='html')
        else:
            bot.send_message(message.chat.id, mp.not_admin, reply_markup=mp.off_markup, parse_mode='MARKDOWN')
    except Exception as e:
        bot.reply_to(message, f'{e}')

@bot.message_handler(commands=['conirm_ad'])
def conirm_ad(message) -> None:
    try:
        if db.is_admin(chat_id=message.chat.id):
            output = db.new_ad(shortname=ads['shortname'], text=ads['text'],file_path=ads['file_path'],media_type=ads['media_type'],btn_text=ads['btn_text'],btn_url=ads['btn_url'])
            bot.send_message(message.chat.id, 'Рекламный пост добавлен', reply_markup=mp.ads_menu, parse_mode='MARKDOWN')
            ads['shortname'], ads['text'], ads['file_path'], ads['media_type'], ads['btn_text'], ads['btn_url'] = '','','','','',''
        else:
            bot.send_message(message.chat.id, mp.not_admin, reply_markup=mp.off_markup, parse_mode='MARKDOWN')
    except Exception as e:
        bot.reply_to(message, f'{e}')

@bot.message_handler(commands=['decline_ad'])
def decline_ad(message) -> None:
    try:
        if db.is_admin(chat_id=message.chat.id):
            msg = bot.send_message(message.chat.id, "Укажите короткое имя для нового рекламного поста", reply_markup=mp.off_markup, parse_mode='MARKDOWN')
            bot.register_next_step_handler(msg, shortname_ad)
        else:
            bot.send_message(message.chat.id, mp.not_admin, reply_markup=mp.off_markup, parse_mode='MARKDOWN')
    except Exception as e:
        bot.reply_to(message, f'{e}')

@bot.message_handler(commands=['delete_ad'])
def delete_ad(message) -> None:
    try:
        if db.is_admin(chat_id=message.chat.id):
            unique_code = extract_unique_code(message.text)
            if unique_code == None:
                bot.send_message(message.chat.id, f"Поста с таким названием нет", reply_markup=mp.ads_menu,parse_mode='MARKDOWN')
            else:
                ad = db.get_ad(shortname=unique_code)
                if ad == None:
                    bot.send_message(message.chat.id, 'Поста с таким названием нет', reply_markup=mp.ads_menu,parse_mode='MARKDOWN')
                else:
                    output = db.delete_ad(shortname=ad.shortname)
                    subprocess.run(f'rm {ad.file_path}', shell=True, capture_output=True)
                    bot.send_message(message.chat.id, f"Пост удален: {output['message']}", reply_markup=mp.ads_menu, parse_mode='MARKDOWN')
        else:
            bot.send_message(message.chat.id, mp.not_admin, reply_markup=mp.off_markup, parse_mode='MARKDOWN')
    except Exception as e:
        bot.reply_to(message, f'{e}')

@bot.message_handler(commands=['list_ad'])
def list_ad(message) -> None:
    try:
        if db.is_admin(chat_id=message.chat.id):
            ads = db.get_ads()
            msg = ''
            for i in range(len(ads)):
                msg += "``` "+ads[i].shortname+" ```\n"
            bot.send_message(message.chat.id, msg, reply_markup=mp.ads_menu,parse_mode='MARKDOWN')
        else:
            bot.send_message(message.chat.id, mp.not_admin, reply_markup=mp.off_markup, parse_mode='MARKDOWN')
    except Exception as e:
        bot.reply_to(message, f'{e}')

@bot.message_handler(commands=['get_ad'])
def get_add(message) -> None:
    try:
        if db.is_admin(chat_id=message.chat.id):
            unique_code = extract_unique_code(message.text)
            if unique_code == None:
                bot.send_message(message.chat.id, f"Поста с таким названием нет", reply_markup=mp.ads_menu,parse_mode='MARKDOWN')
            else:
                ad = db.get_ad(shortname=unique_code)
                if ad == None:
                    bot.send_message(message.chat.id, 'Поста с таким названием нет', reply_markup=mp.ads_menu,parse_mode='MARKDOWN')
                else:
                    get_ad(chat_id=message.chat.id,ad=ad)
        else:
            bot.send_message(message.chat.id, mp.not_admin, reply_markup=mp.off_markup, parse_mode='MARKDOWN')
    except Exception as e:
        bot.reply_to(message, f'{e}')

def send_random_post(chat_id:int):
    try:
        ads = db.get_ads()
        if len(ads) == 0:
            pass
        else:
            random_int = get_random_int(length=len(ads))
            media = open(ads[random_int].file_path, 'rb')
            if ads[random_int].btn_text == '':
                if ads[random_int].media_type == 'jpg':
                    bot.send_photo(chat_id, media, caption=ads[random_int].text, parse_mode='MARKDOWN')
                elif ads[random_int].media_type == 'mp4':
                    bot.send_video(chat_id, media, caption=ads[random_int].text, parse_mode='MARKDOWN')
            else:
                markup = mp.get_inline_url_btn(text = ads[random_int].btn_text, url = ads[random_int].btn_url)
                if ads[random_int].media_type == 'jpg':
                    bot.send_document(chat_id, media, caption=ads[random_int].text, parse_mode='MARKDOWN', reply_markup=markup)
                else:
                    bot.send_video(chat_id, media, caption=ads[random_int].text, parse_mode='MARKDOWN',reply_markup=markup)
    except Exception as e:
        print(f'{e}')

def get_ad(chat_id:int,ad):
    try:
        media = open(ad.file_path, 'rb')
        if ad.btn_text == '':
            bot.send_document(chat_id, media, caption=ad.text, parse_mode='MARKDOWN')
        else:
            markup = mp.get_inline_url_btn(text=ad.btn_text, url=ad.btn_url)
            bot.send_document(chat_id, media, caption=ad.text, parse_mode='MARKDOWN',reply_markup=markup)
    except Exception as e:
        print(f'{e}')

@bot.callback_query_handler(func = lambda call:True)
def callback_handler(call):
    try:
        if call.data == 'check':
            global channel_link
            ans = check(channel=channel_link, username=str(call.message.chat.username).lower())
            if ans == 'False':
                bot.send_message(chat_id=call.message.chat.id, text='Проверьте, вы точно подписались на канал?', reply_markup=mp.off_markup, parse_mode='MARKDOWN')
            else:
                bot.send_message(chat_id=call.message.chat.id, text='Отправьте ссылку заново', reply_markup=mp.off_markup, parse_mode='MARKDOWN')
    except Exception as e:
        print(e)


@bot.message_handler(content_types=["text"])
def text_handler(message):
    try:
        urls = extractor.find_urls(message.text)
        if len(urls) == 0:
            bot.send_message(chat_id=message.chat.id, text=mp.invalid_url, reply_markup=mp.off_markup, parse_mode='MARKDOWN')
            file_path = False
        elif len(urls) > 1:
            bot.send_message(chat_id=message.chat.id, text=mp.toomuch_urls)
            file_path = False
        else:
            users[message.chat.id] = urls[0]
            global channel_link
            ans = check(channel=channel_link, username=str(message.chat.username).lower())
            global sub_status
            if ans == 'False' and sub_status == True:
                bot.send_message(chat_id=message.chat.id, text=mp.channel_post, reply_markup=mp.inline_sub_mp(channel_url=channel_link), parse_mode='MARKDOWN')
                file_path = False
            else:
                service = service_type(url=users[message.chat.id])
                if service == False:
                    bot.reply_to(message, f'Мы не можем найти медиа по этой ссылке', reply_markup=mp.off_markup)
                    file_path = False

                elif service == 'youtube':
                    gif1 = open('video/cat.mp4', 'rb')
                    gif1_msg = bot.send_document(message.chat.id, gif1, caption='Скачиваем с ютуба...', reply_to_message_id=message.message_id)
                    gif1_msg_id = gif1_msg.message_id

                    file_path = download_YT(url=users[message.chat.id], chatid=message.chat.id, ismp3=True)
                    if file_path == 'Video too long':
                        bot.reply_to(message, f'Видео слишком длинное;(', reply_markup=mp.off_markup)

                    gif2 = types.InputMediaDocument(media=open('video/send.mp4', 'rb'), caption='Отправляем в тг')
                    bot.edit_message_media(media=gif2, chat_id=message.chat.id, message_id=gif1_msg_id)

                    doc = open(file_path, 'rb')
                    init_dw_output = db.init_download(chat_id=message.chat.id, src_type='youtube',date_of_join=date_today(),url=users[message.chat.id])
                    print(init_dw_output)
                    bot.send_document(message.chat.id, doc, reply_markup=mp.markup_banner_inline, caption=mp.get_caption(url=users[message.chat.id]))

                elif service == 'tiktok':
                    gif1 = open('video/cat.mp4', 'rb')
                    gif1_msg = bot.send_document(message.chat.id, gif1, caption='Скачиваем с тиктока...', reply_to_message_id=message.message_id)
                    gif1_msg_id = gif1_msg.message_id

                    output = upload_video_tt(chat_id=str(message.chat.id), url = users[message.chat.id])
                    if output == 'not found':
                        bot.reply_to(message, f'Мы не можем найти видео по этой ссылке', reply_markup=mp.off_markup)

                    file_path = os.getenv("downloads_pwd") + output

                    gif2 = types.InputMediaDocument(media=open('video/send.mp4', 'rb'), caption='Отправляем в тг')
                    bot.edit_message_media(media=gif2, chat_id=message.chat.id, message_id=gif1_msg_id)

                    doc = open(file_path, 'rb')
                    init_dw_output = db.init_download(chat_id=message.chat.id, src_type='tiktok',date_of_join=date_today(), url=users[message.chat.id])
                    print(init_dw_output)
                    bot.send_document(message.chat.id, doc, reply_markup=mp.markup_banner_inline, caption=mp.get_caption(url=users[message.chat.id]))

                elif service == 'instagram':
                    file_path = list()
                    gif1 = open('video/cat.mp4', 'rb')
                    gif1_msg = bot.send_document(message.chat.id, gif1, caption='Скачиваем с инсты...', reply_to_message_id=message.message_id)
                    gif1_msg_id = gif1_msg.message_id

                    output = upload_video_inst(chat_id=str(message.chat.id), url=users[message.chat.id])
                    if output == 'not found':
                        bot.reply_to(message, f'Мы не можем найти видео по этой ссылке', reply_markup=mp.off_markup)

                    for i in range(len(output)):
                        file_path.append(os.getenv("downloads_pwd") + output[i])

                    gif2 = types.InputMediaDocument(media=open('video/send.mp4', 'rb'), caption='Отправляем в тг')
                    bot.edit_message_media(media=gif2, chat_id=message.chat.id, message_id=gif1_msg_id)

                    for i in range(len(file_path)):
                        doc = open(file_path[i], 'rb')
                        init_dw_output = db.init_download(chat_id=message.chat.id, src_type='instagram', date_of_join=date_today(), url=users[message.chat.id])
                        print(init_dw_output)
                        bot.send_document(message.chat.id, doc, reply_markup=mp.markup_banner_inline, caption=mp.get_caption(url=users[message.chat.id]))
                        subprocess.run(f'rm {file_path[i]}', shell=True, capture_output=True)
                    file_path = False

                else:
                    file_path = False

                global ad_status
                print(ad_status)
                if ad_status == True:
                    send_random_post(chat_id = message.chat.id)
                else:
                    pass

    except Exception as e:
        print(e)

    finally:
        if file_path == False:
            pass
        else:
            subprocess.run(f'rm {file_path}', shell=True, capture_output=True)

def service_type(url: str) -> 'Return service name of url':
    service_types = ['instagram', 'youtube', 'tiktok']
    if url.find('tiktok') == -1:
        service_types.remove('tiktok')
    if url.find('instagram') == -1:
        service_types.remove('instagram')
    if url.find('youtube') == -1 and url.find('youtu.be') == -1:
        service_types.remove('youtube')
    if url.find('playlist') != -1:
        service_types.remove('youtube')

    if len(service_types) == 0:
        return False
    else:
        return service_types[0]

def extract_unique_code(text):
    return text.split()[1] if len(text.split()) > 1 else None

def date_today():
    today = date.today()
    return str(today.strftime("%d/%m/%Y"))

def referal_stat_msg(data):
    msg = 'Статистика по реферальным ссылкам\n\n'
    if len(data) == 0:
        msg += 'нет реферальных ссылок'
        return msg
    for keys in data:
        msg += f'{db.get_name_by_uuid(uuid=keys)}: {data[keys]}\n'
    return msg

def get_random_int(length: int):
    return randrange(length)

def main():
    bot.polling(none_stop=True)

if __name__ == "__main__":
    main()