import os
import time

import telebot
from bot import markups as mp
from dotenv import load_dotenv
import urlextract
import selenium
import subprocess
from youtube import download_YT
from tiktok import upload_video_tt
from instagram import upload_video_inst
from database import dbworker as db
from datetime import date
from pathlib import Path
from random import randrange

extractor = urlextract.URLExtract()

config = load_dotenv()
bot = telebot.TeleBot(os.getenv("TG_API_KEY"))


users = dict()
repl_message_user = dict()
ads = {'shortname': '', 'text':'', 'file_path':'', 'media_type':'', 'btn_text': '', 'btn_url':''}
language_list = dict()
mail_users_dict = dict()
mail_users_dict['text'] = ''
mail_users_dict['status'] = ''
mail_users_dict['media_type'] = ''
mail_users_dict['src'] = ''
language_msg_ids = dict()
sub_status = True
ad_status = False
# channel_link = 'https://t.me/Tezkor_tg'
# channel_username = '@Tezkor_tg'
channel_link = 'https://t.me/CryptoVedma'
channel_username = '@CryptoVedma'

@bot.message_handler(commands=['start'])
def start(message) -> None:

    try:
        result = bot.get_chat_member(channel_username, message.chat.id)
        print(result.status)
        unique_code = extract_unique_code(message.text)
        if unique_code == None:
            db.init_user(chat_id=message.chat.id, username=message.chat.username, date_of_join=date_today(), referal_code='N/A')
        else:
            db.init_user(chat_id=message.chat.id, username=message.chat.username, date_of_join=date_today(),referal_code=unique_code)

        language = db.get_language(chat_id=message.chat.id)
        if language == 'O’zbek 🇺🇿':
            bot.send_message(message.chat.id, mp.menu_message_uz, reply_markup=mp.off_markup,parse_mode='MARKDOWN')
        elif language == 'Русский 🇷🇺':
            bot.send_message(message.chat.id, mp.menu_message_ru, reply_markup=mp.off_markup,parse_mode='MARKDOWN')
        else:
            msg = bot.send_message(message.chat.id, mp.choose_language, reply_markup=mp.language, parse_mode='MARKDOWN')
            language_msg_ids[message.chat.id] = msg.message_id
    except Exception as e:
        bot.reply_to(message, f'{e}')

@bot.message_handler(commands=['language'])
def language(message) -> None:
    try:
        msg = bot.send_message(message.chat.id, mp.choose_language, reply_markup=mp.language, parse_mode='MARKDOWN')
        language_msg_ids[message.chat.id] = msg.message_id

    except Exception as e:
        bot.reply_to(message, f'{e}')

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
            msg = mp.get_stat_msg(
                number_of_users = stat['number_of_users'],
                users_today=stat['users_today'],
                all_downloads=stat['all_downloads'],
                today_downloads=stat['today_downloads'],
                youtube=stat['youtube'],
                tiktok=stat['tiktok'],
                instagram=stat['instagram'],
                youtube_shorts=stat['youtube_shorts']
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
            msg = bot.send_message(message.chat.id, 'Введите название для реферальной ссылки', reply_markup=mp.cancel, parse_mode='MARKDOWN')
            bot.register_next_step_handler(msg, init_referal)
        else:
            bot.send_message(message.chat.id, mp.not_admin, reply_markup=mp.off_markup, parse_mode='MARKDOWN')
    except Exception as e:
        bot.reply_to(message, f'{e}')

def init_referal(message):
    try:
        if message.text == 'cancel':
            bot.send_message(message.chat.id, 'Админка', reply_markup=mp.menu_admin, parse_mode='MARKDOWN')
        else:

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

mail_users_dict = dict()

@bot.message_handler(commands=['mail_users'])
def mail_users(message) -> None:
    try:
        if db.is_admin(chat_id=message.chat.id):
            mail_users_dict['text'] = ''
            mail_users_dict['status'] = ''
            mail_users_dict['media_type'] = ''
            mail_users_dict['src'] = ''
            msg = bot.send_message(message.chat.id, mp.mail_users_msg, reply_markup=mp.cancel_mail, parse_mode='html')
            bot.register_next_step_handler(msg, add_media_to_mail)
        else:
            bot.send_message(message.chat.id, mp.not_admin, reply_markup=mp.off_markup, parse_mode='MARKDOWN')
    except Exception as e:
        bot.reply_to(message, f'{e}')

def add_media_to_mail(message) -> None:
    try:
        if db.is_admin(chat_id=message.chat.id):
            if message.text == 'cancel_mail':
                bot.send_message(message.chat.id, f'Admin: {message.chat.username}', reply_markup=mp.menu_admin, parse_mode='MARKDOWN')
            else:
                mail_users_dict['text'] = message.text
                msg = bot.send_message(message.chat.id, "Прикрепить меида - 1\nНе прикреплять медиа - 0", reply_markup=mp.cancel_mail, parse_mode='html')
                bot.register_next_step_handler(msg, mail_users_send)
        else:
            bot.send_message(message.chat.id, mp.not_admin, reply_markup=mp.off_markup, parse_mode='MARKDOWN')
    except Exception as e:
        bot.reply_to(message, f'{e} 1')


def mail_users_send(message):
    try:
        if message.text == 'cancel_mail':
            bot.send_message(message.chat.id, f'Admin: {message.chat.username}', reply_markup=mp.menu_admin, parse_mode='MARKDOWN')
        elif message.text == '0':
            mail_users_dict['status'] = ''
            bot.send_message(message.chat.id, mail_users_dict['text'], reply_markup=mp.cancel_1, parse_mode='html')
            msg = bot.send_message(message.chat.id, f"Нажмите push, что бы отправить, cancel - отменить", reply_markup=mp.cancel_1, parse_mode='html')
            bot.register_next_step_handler(msg, confirm_mail)
        elif message.text == '1':
            mail_users_dict['status'] = 'mail' 
            msg = bot.send_message(message.chat.id, "Прикрепите файл\n\n.jpg .jpeg .mp4", reply_markup=mp.off_markup, parse_mode='MARKDOWN')
            bot.register_next_step_handler(msg, handler_file)

    except Exception as e:
        pass

def confirm_mail(message):
    try:
        sended = 0
        unsended = 0
        if message.text == 'cancel_mail':
            bot.send_message(message.chat.id, f'Admin: {message.chat.username}', reply_markup=mp.menu_admin, parse_mode='MARKDOWN')
        elif message.text == 'push':
            users = db.get_users()
            if mail_users_dict['src'] == '':
                for i in range(len(users)):
                    try:
                        msg =  bot.send_message(users[i].chat_id, mail_users_dict['text'], reply_markup=mp.off_markup, parse_mode='MARKDOWN')
                        sended += 1
                    except Exception as e:
                        unsended += 1
                        pass
                bot.send_message(message.chat.id, f'Отправленно: {sended}\nНе отправленно {unsended}')
                print(sended, unsended)
            else:
                for i in range(len(users)):
                        if  mail_users_dict['media_type'] == 'mp4':
                            try:
                                media = open(f"{mail_users_dict['src']}", 'rb')
                                bot.send_video(users[i].chat_id, media, caption= mail_users_dict['text'], reply_markup=mp.off_markup,parse_mode='MARKDOWN')
                                sended += 1
                            except Exception as e:
                                unsended += 1
                                pass
                        else:
                            try:
                                media = open(f"{mail_users_dict['src']}", 'rb')
                                bot.send_photo(users[i].chat_id, media, caption=mail_users_dict['text'], reply_markup=mp.off_markup, parse_mode='MARKDOWN')
                                sended += 1
                                print('Sended: ', sended)
                            except Exception as e:
                                print(e)
                                unsended += 1
                                print('Unsended: ', unsended)
                                pass
                print(sended, unsended)
                bot.send_message(message.chat.id, f'Отправленно: {sended}\nНе отправленно {unsended}')

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
                msg = bot.send_message(message.chat.id,"1 - прикрепить файл\n0- не прикреплять",reply_markup=mp.off_markup, parse_mode='MARKDOWN')
                bot.register_next_step_handler(msg, media_ad)
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
            msg = bot.send_message(message.chat.id, "1 - прикрепить файл\n0- не прикреплять", reply_markup=mp.off_markup, parse_mode='MARKDOWN')
            bot.register_next_step_handler(msg, media_ad)
        else:
            bot.send_message(message.chat.id, mp.not_admin, reply_markup=mp.off_markup, parse_mode='MARKDOWN')
    except Exception as e:
        bot.reply_to(message, f'{e}')

def media_ad(message):
    try:
        if db.is_admin(chat_id=message.chat.id):
            if message.text == '1':
                mail_users_dict['status'] = ''
                msg = bot.send_message(message.chat.id, "Прикрепите медиа (jpg .jpeg .mp4)", reply_markup=mp.off_markup, parse_mode='MARKDOWN')
                bot.register_next_step_handler(msg, handler_file)

            elif message.text == '0':
                if ads['btn_text'] == '':
                    bot.send_message(message.chat.id, text=ads['text'], reply_markup=mp.off_markup, parse_mode='MARKDOWN')
                else:
                    markup = mp.get_inline_url_btn(text=ads['btn_text'], url=ads['btn_url'])
                    bot.send_message(message.chat.id, text=ads['text'], reply_markup=markup,parse_mode='MARKDOWN')
                bot.send_message(message.chat.id, f"short name: {ads['shortname']} - Confirm?", reply_markup=mp.confirm_ad,parse_mode='html')

            else:
                msg = bot.send_message(message.chat.id, "1 - прикрепить файл\n0- не прикреплять\n\n.jpg .jpeg .mp4", reply_markup=mp.off_markup, parse_mode='MARKDOWN')
                bot.register_next_step_handler(msg, media_ad)
        else:
            bot.send_message(message.chat.id, mp.not_admin, reply_markup=mp.off_markup, parse_mode='MARKDOWN')
    except Exception as e:
        bot.reply_to(message, f'{e}')

@bot.message_handler(content_types=['photo', 'document'])
def handler_file(message):
    try:
        print(mail_users_dict)
        if db.is_admin(chat_id=message.chat.id):
            Path(f'files/{message.chat.id}/').mkdir(parents=True, exist_ok=True)
            if mail_users_dict['status'] == 'mail':
                if message.content_type == 'photo':
                    file_info = bot.get_file(message.photo[len(message.photo) - 1].file_id)
                    downloaded_file = bot.download_file(file_info.file_path)
                    src = f"{os.getenv('ad_pwd')}/mail.jpg"
                    with open(src, 'wb') as new_file:
                        new_file.write(downloaded_file)
                    mail_users_dict['src'] = src
                    mail_users_dict['media_type'] = 'jpg'
                    bot.send_message(message.chat.id, f"Изображение загружено",reply_markup=mp.off_markup, parse_mode='html')
                if message.content_type == 'video':
                    file_info = bot.get_file(message.video.file_id)
                    downloaded_file = bot.download_file(file_info.file_path)
                    src = f"{os.getenv('ad_pwd')}/mail.mp4"
                    with open(src, 'wb') as new_file:
                        new_file.write(downloaded_file)
                    mail_users_dict['src'] = src
                    mail_users_dict['media_type'] = 'mp4'
                    bot.send_message(message.chat.id, f"Видео загружено", reply_markup=mp.off_markup, parse_mode='html')

                media = open(f"{mail_users_dict['src']}", 'rb')
                if  mail_users_dict['media_type'] == 'mp4':
                    bot.send_video(message.chat.id, media, caption= mail_users_dict['text'], reply_markup=mp.off_markup,parse_mode='MARKDOWN')
                else:
                    bot.send_photo(message.chat.id, media, caption=mail_users_dict['text'], reply_markup=mp.off_markup, parse_mode='MARKDOWN')

                msg = bot.send_message(message.chat.id, f"Нажмите push, что бы отправить, cancel - отменить", reply_markup=mp.cancel_1, parse_mode='html')
                bot.register_next_step_handler(msg, confirm_mail)
                
            else:
                print(2)
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
                    file_info = bot.get_file(message.video.file_id)
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
            # print(ads['shortname']
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
            msg = bot.send_message(message.chat.id, "Admin menu", reply_markup=mp.menu_admin, parse_mode='MARKDOWN')
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
            # media = open(ads[random_int].file_path, 'rb')
            # if ads[random_int].btn_text == '':
            #     if ads[random_int].media_type == 'jpg':
            #         bot.send_photo(chat_id, media, caption=ads[random_int].text, parse_mode='MARKDOWN')
            #     elif ads[random_int].media_type == 'mp4':
            #         bot.send_video(chat_id, media, caption=ads[random_int].text, parse_mode='MARKDOWN')
            # else:
            #     markup = mp.get_inline_url_btn(text = ads[random_int].btn_text, url = ads[random_int].btn_url)
            #     if ads[random_int].media_type == 'jpg':
            #         bot.send_photo(chat_id, media, caption=ads[random_int].text, parse_mode='MARKDOWN', reply_markup=markup)
            #     else:
            #         bot.send_video(chat_id, media, caption=ads[random_int].text, parse_mode='MARKDOWN',reply_markup=markup)

            if ads[random_int].btn_text == '' and ads[random_int].media_type =='':
                bot.send_message(chat_id, text=ads[random_int].text, parse_mode='MARKDOWN')
            elif ads[random_int].btn_text == '' and ads[random_int].media_type !='':
                media = open(ads[random_int].file_path, 'rb')
                if ads[random_int].media_type == 'mp4':
                    bot.send_video(chat_id, media, caption=ads[random_int].text, parse_mode='MARKDOWN')
                else:
                    bot.send_photo(chat_id, media, caption=ads[random_int].text, parse_mode='MARKDOWN')
            elif ads[random_int].btn_text != '' and ads[random_int].media_type =='':
                markup = mp.get_inline_url_btn(text=ads[random_int].btn_text, url=ads[random_int].btn_url)
                bot.send_message(chat_id, text=ads[random_int].text, parse_mode='MARKDOWN', reply_markup=markup)
            else:
                media = open(ads[random_int].file_path, 'rb')
                markup = mp.get_inline_url_btn(text=ads[random_int].btn_text, url=ads[random_int].btn_url)
                if ads[random_int].media_type == 'mp4':
                    bot.send_video(chat_id, media, caption=ads[random_int].text, parse_mode='MARKDOWN', reply_markup=markup)
                else:
                    bot.send_photo(chat_id, media, caption=ads[random_int].text, parse_mode='MARKDOWN', reply_markup=markup)

    except Exception as e:
        print(f'{e}')

def get_ad(chat_id:int,ad):
    try:
        if ad.btn_text == '' and ad.media_type =='':
            bot.send_message(chat_id, text=ad.text, parse_mode='MARKDOWN')
        elif ad.btn_text == '' and ad.media_type !='':
            media = open(ad.file_path, 'rb')
            if ad.media_type == 'mp4':
                bot.send_video(chat_id, media, caption=ad.text, parse_mode='MARKDOWN')
            else:
                bot.send_photo(chat_id, media, caption=ad.text, parse_mode='MARKDOWN')
        elif ad.btn_text != '' and ad.media_type =='':
            markup = mp.get_inline_url_btn(text=ad.btn_text, url=ad.btn_url)
            bot.send_message(chat_id, text=ad.text, parse_mode='MARKDOWN', reply_markup=markup)
        else:
            media = open(ad.file_path, 'rb')
            markup = mp.get_inline_url_btn(text=ad.btn_text, url=ad.btn_url)
            if ad.media_type == 'mp4':
                bot.send_video(chat_id, media, caption=ad.text, parse_mode='MARKDOWN', reply_markup=markup)
            else:
                bot.send_photo(chat_id, media, caption=ad.text, parse_mode='MARKDOWN', reply_markup=markup)
    except Exception as e:
        print(f'{e}')

@bot.callback_query_handler(func = lambda call:True)
def callback_handler(call):
    try:
        global channel_link

        # language_msg_ids[message.chat.id]

        if call.data == 'Русский 🇷🇺':
            bot.delete_message(call.message.chat.id, message_id=language_msg_ids[call.message.chat.id])
            db.set_language(chat_id=call.message.chat.id, language=call.data)
            bot.send_message(call.message.chat.id, mp.menu_message_ru, reply_markup=mp.off_markup, parse_mode='MARKDOWN')
        elif call.data == 'O’zbek 🇺🇿':
            bot.delete_message(call.message.chat.id, message_id=language_msg_ids[call.message.chat.id])
            db.set_language(chat_id=call.message.chat.id, language=call.data)
            bot.send_message(call.message.chat.id, mp.menu_message_uz, reply_markup=mp.off_markup, parse_mode='MARKDOWN')

        if call.data == 'check':
            result = bot.get_chat_member(channel_username, call.message.chat.id)
            # ans = check(channel=channel_link, username=str(call.message.chat.username).lower())
            if result.status == 'left':
                if language == 'O’zbek 🇺🇿':
                    print(repl_message_user[call.message.chat.id])
                    bot.delete_message(call.message.chat.id, message_id=repl_message_user[call.message.chat.id])
                    language_usr = db.get_language(chat_id=call.message.chat.id)
                    msg = bot.send_message(chat_id=call.message.chat.id, text=mp.channel_post_uz,reply_markup=mp.inline_sub_mp(channel_url=channel_link, language= language_usr), parse_mode='MARKDOWN')
                    repl_message_user[call.message.chat.id] = msg.message_id
                else:
                    bot.delete_message(call.message.chat.id, message_id=repl_message_user[call.message.chat.id])
                    language_usr = db.get_language(chat_id=call.message.chat.id)
                    msg = bot.send_message(chat_id=call.message.chat.id, text=mp.channel_post_ru,reply_markup=mp.inline_sub_mp(channel_url=channel_link, language=language_usr),parse_mode='MARKDOWN')
                    repl_message_user[call.message.chat.id] = msg.message_id

            else:
                print(users[call.message.chat.id])
                language_usr = db.get_language(chat_id=call.message.chat.id)
                file_path = False
                urls = extractor.find_urls(users[call.message.chat.id])
                if len(urls) == 0:
                    if language_usr == 'O’zbek 🇺🇿':
                        bot.reply_to(call.message,
                                     f'Noto’gri havola yubordingiz!\nInstagram, TikTok yoki YouTube dan to’g’ri havola yuboring.',
                                     reply_markup=mp.off_markup)
                        file_path = False
                    else:
                        bot.reply_to(call.message,
                                     f'Неверная ссылка!\nОтправьте правильную ссылку из Instagram, TikTok или YouTube.',
                                     reply_markup=mp.off_markup)
                        file_path = False
                elif len(urls) > 1:
                    if language_usr == 'O’zbek 🇺🇿':
                        bot.reply_to(call.message,
                                     f"juda ko'p havolalar\nInstagram, TikTok yoki YouTube dan to’g’ri havola yuboring.",
                                     reply_markup=mp.off_markup)
                        file_path = False
                    else:
                        bot.reply_to(call.message,
                                     f'Слишком много ссылок!\nОтправьте правильную ссылку из Instagram, TikTok или YouTube.',
                                     reply_markup=mp.off_markup)
                else:
                    users[call.message.chat.id] = urls[0]
                    # global channel_link
                    result = bot.get_chat_member(channel_username, call.message.chat.id)
                    # ans = check(channel=channel_link, username=str(call.message.chat.username).lower())
                    global sub_status
                    if result.status == 'left' and sub_status == True and language_usr == 'Русский 🇷🇺':
                        msg = bot.send_message(chat_id=call.message.chat.id, text=mp.channel_post_ru,
                                               reply_markup=mp.inline_sub_mp(channel_url=channel_link,
                                                                             language=language_usr),
                                               parse_mode='MARKDOWN')
                        repl_message_user[call.message.chat.id] = msg.message_id
                        file_path = False
                    elif result.status == 'left' and sub_status == True and language_usr == 'O’zbek 🇺🇿':
                        msg = bot.send_message(chat_id=call.message.chat.id, text=mp.channel_post_uz,
                                               reply_markup=mp.inline_sub_mp(channel_url=channel_link,
                                                                             language=language_usr),
                                               parse_mode='MARKDOWN')
                        repl_message_user[call.message.chat.id] = msg.message_id
                        file_path = False
                    else:
                        service = service_type(url=users[call.message.chat.id])
                        if service == False and language_usr == 'O’zbek 🇺🇿':
                            bot.reply_to(call.message,
                                         f'Noto’gri havola yubordingiz!\nInstagram, TikTok yoki YouTube dan to’g’ri havola yuboring.',
                                         reply_markup=mp.off_markup)
                            file_path = False
                        elif service == False and language_usr != 'O’zbek 🇺🇿':
                            bot.reply_to(call.message,
                                         f'Неверная ссылка!\nОтправьте правильную ссылку из Instagram, TikTok или YouTube.',
                                         reply_markup=mp.off_markup)
                            file_path = False

                        elif service == 'youtube':
                            if language_usr == 'O’zbek 🇺🇿':
                                gif1_msg = bot.send_message(call.message.chat.id, "YouTubedan yuklanyabti…",
                                                            reply_to_message_id=call.message.message_id)
                                gif1_msg_id = gif1_msg.message_id

                                file_path = download_YT(url=users[call.message.chat.id], chatid=call.message.chat.id, ismp3=True)
                                if file_path == 'Video too long':
                                    bot.reply_to(call.message, f'YouTube dan davomiyligi 10 daqiqadan ko’p bo’lmagan videoni yuklashingiz mumkin!\nIltimos, boshqa havola yuboring.', reply_markup=mp.off_markup)
                                elif file_path == Exception:
                                    bot.reply_to(call.message, f'Error, send link again', reply_markup=mp.off_markup)

                                # gif2 = types.InputMediaDocument(media=open('video/send.mp4', 'rb'), caption='Отправляем в тг')
                                # bot.edit_message_text(text="telegramga yuboring", chat_id=call.message.chat.id,
                                #                       message_id=gif1_msg_id)
                                bot.delete_message(chat_id=call.message.chat.id, message_id=gif1_msg_id)

                                doc = open(file_path, 'rb')
                                init_dw_output = db.init_download(chat_id=call.message.chat.id, src_type='youtube',
                                                                  date_of_join=date_today(), url=users[call.message.chat.id])
                                print(init_dw_output)
                                bot.send_document(call.message.chat.id, doc, reply_markup=mp.off_markup,
                                                  caption=mp.get_caption(language=language_usr), parse_mode="MARKDOWN")

                            else:
                                gif1_msg = bot.send_message(call.message.chat.id, "Скачиваем из youtube",
                                                            reply_to_message_id=call.message.message_id)
                                gif1_msg_id = gif1_msg.message_id

                                file_path = download_YT(url=users[call.message.chat.id], chatid=call.message.chat.id, ismp3=True)
                                if file_path == 'Video too long':
                                    bot.reply_to(call.message, f'Бот может скачивать видео из YouTube с продолжительностью не больше 10 минут!\nПожалуйста, отправьте ссылку другого видео.', reply_markup=mp.off_markup)
                                elif file_path == Exception:
                                    bot.reply_to(call.message, f'Error, send link again', reply_markup=mp.off_markup)

                                # gif2 = types.InputMediaDocument(media=open('video/send.mp4', 'rb'), caption='Отправляем в тг')
                                # bot.edit_message_text(text="Отправляем в телеграмм", chat_id=call.message.chat.id,
                                #                       message_id=gif1_msg_id)
                                bot.delete_message(chat_id=call.message.chat.id, message_id=gif1_msg_id)

                                doc = open(file_path, 'rb')
                                init_dw_output = db.init_download(chat_id=call.message.chat.id, src_type='youtube',
                                                                  date_of_join=date_today(), url=users[call.message.chat.id])
                                print(init_dw_output)
                                bot.send_document(call.message.chat.id, doc, reply_markup=mp.off_markup,
                                                  caption=mp.get_caption(language=language_usr), parse_mode="MARKDOWN")

                        elif service == 'youtube_shorts':
                            if language_usr == 'O’zbek 🇺🇿':
                                gif1_msg = bot.send_message(call.message.chat.id, "YouTubedan yuklanyabti…",
                                                            reply_to_message_id=call.message.message_id)
                                gif1_msg_id = gif1_msg.message_id

                                file_path = download_YT(url=users[call.message.chat.id], chatid=call.message.chat.id, ismp3=False)
                                if file_path == 'Video too long':
                                    bot.reply_to(call.message, f'YouTube dan davomiyligi 10 daqiqadan ko’p bo’lmagan videoni yuklashingiz mumkin!\nIltimos, boshqa havola yuboring.', reply_markup=mp.off_markup)
                                elif file_path == Exception:
                                    bot.reply_to(call.message, f'Error, send link again', reply_markup=mp.off_markup)

                                # gif2 = types.InputMediaDocument(media=open('video/send.mp4', 'rb'), caption='Отправляем в тг')
                                # bot.edit_message_text(text="telegramga yuboring", chat_id=call.message.chat.id,
                                #                       message_id=gif1_msg_id)
                                bot.delete_message(chat_id=call.message.chat.id, message_id=gif1_msg_id)

                                doc = open(file_path, 'rb')
                                init_dw_output = db.init_download(chat_id=call.message.chat.id, src_type='youtube_shorts',
                                                                  date_of_join=date_today(), url=users[call.message.chat.id])
                                print(init_dw_output)
                                bot.send_document(call.message.chat.id, doc, reply_markup=mp.off_markup,
                                                  caption=mp.get_caption(language=language_usr), parse_mode="MARKDOWN")

                            else:
                                gif1_msg = bot.send_message(call.message.chat.id, "Скачиваем из youtube",
                                                            reply_to_message_id=call.message.message_id)
                                gif1_msg_id = gif1_msg.message_id

                                file_path = download_YT(url=users[call.message.chat.id], chatid=call.message.chat.id, ismp3=False)
                                if file_path == 'Video too long':
                                    bot.reply_to(call.message, 'Бот может скачивать видео из YouTube с продолжительностью не больше 10 минут!\nПожалуйста, отправьте ссылку другого видео.', reply_markup=mp.off_markup)
                                elif file_path == Exception:
                                    bot.reply_to(call.message, f'Error, send link again', reply_markup=mp.off_markup)

                                # gif2 = types.InputMediaDocument(media=open('video/send.mp4', 'rb'), caption='Отправляем в тг')
                                # bot.edit_message_text(text="Отправляем в телеграмм", chat_id=call.message.chat.id,
                                #                       message_id=gif1_msg_id)
                                bot.delete_message(chat_id=call.message.chat.id, message_id=gif1_msg_id)

                                doc = open(file_path, 'rb')
                                init_dw_output = db.init_download(chat_id=call.message.chat.id, src_type='youtube_shorts',
                                                                  date_of_join=date_today(), url=users[call.message.chat.id])
                                print(init_dw_output)
                                bot.send_document(call.message.chat.id, doc, reply_markup=mp.off_markup,
                                                  caption=mp.get_caption(language=language_usr), parse_mode="MARKDOWN")

                        elif service == 'tiktok':
                            if language_usr == 'O’zbek 🇺🇿':
                                gif1_msg = bot.send_message(call.message.chat.id, "TikTokdan yuklanyabti…",
                                                            reply_to_message_id=call.message.message_id)
                                gif1_msg_id = gif1_msg.message_id

                                output = upload_video_tt(chat_id=str(call.message.chat.id), url=users[call.message.chat.id])
                                if output == 'not found':
                                    bot.reply_to(call.message, f'media juda uzun', reply_markup=mp.off_markup)

                                file_path = output

                                # gif2 = types.InputMediaDocument(media=open('video/send.mp4', 'rb'), caption='Отправляем в тг')
                                # bot.edit_message_text(text="telegramga yuboring", chat_id=call.message.chat.id,
                                #                       message_id=gif1_msg_id)
                                bot.delete_message(chat_id=call.message.chat.id, message_id=gif1_msg_id)

                                doc = open(file_path, 'rb')
                                init_dw_output = db.init_download(chat_id=call.message.chat.id, src_type='tiktok',
                                                                  date_of_join=date_today(), url=users[call.message.chat.id])
                                print(init_dw_output)
                                try:
                                    bot.send_video(call.message.chat.id, doc, reply_markup=mp.off_markup,
                                                  caption=mp.get_caption(language=language_usr))
                                except Exception as e:
                                    bot.send_message(call.message.chat.id, "fayl juda og'ir", reply_markup=mp.off_markup)

                            else:
                                gif1_msg = bot.send_message(call.message.chat.id, "Скачивается из TikTok...",
                                                            reply_to_message_id=call.message.message_id)
                                gif1_msg_id = gif1_msg.message_id

                                output = upload_video_tt(chat_id=str(call.message.chat.id), url=users[call.message.chat.id])
                                if output == 'not found':
                                    bot.reply_to(call.message, f'Мы не можем найти видео по этой ссылке',
                                                 reply_markup=mp.off_markup)

                                file_path = output

                                # gif2 = types.InputMediaDocument(media=open('video/send.mp4', 'rb'), caption='Отправляем в тг')
                                # bot.edit_message_text(text="Отправляем в тг", chat_id=call.message.chat.id,
                                #                       message_id=gif1_msg_id)
                                bot.delete_message(chat_id=call.message.chat.id, message_id=gif1_msg_id)

                                doc = open(file_path, 'rb')
                                init_dw_output = db.init_download(chat_id=call.message.chat.id, src_type='tiktok',
                                                                  date_of_join=date_today(), url=users[call.message.chat.id])
                                print(init_dw_output)

                                try:
                                    bot.send_video(call.message.chat.id, doc, reply_markup=mp.off_markup,
                                                  caption=mp.get_caption(language=language_usr))
                                except Exception as e:
                                    bot.send_message(call.message.chat.id, "fayl juda og'ir", reply_markup=mp.off_markup)


                        elif service == 'instagram':
                            if language_usr == 'O’zbek 🇺🇿':
                                file_path = list()
                                gif1_msg = bot.send_message(call.message.chat.id, "Instagramdan yuklanyabti…",
                                                            reply_to_message_id=call.message.message_id)
                                gif1_msg_id = gif1_msg.message_id

                                output = upload_video_inst(chat_id=str(call.message.chat.id), url=users[call.message.chat.id])
                                if output == 'not found':
                                    bot.reply_to(call.message, f'🔒Afsuski, siz yuborgan havola yopiq akkaundan olingan\nYopiq akkauntdan yuklashni iloji yo’q!', reply_markup=mp.off_markup)

                                for i in range(len(output)):
                                    file_path.append(os.getenv("downloads_pwd") + output[i])

                                # gif2 = types.InputMediaDocument(media=open('video/send.mp4', 'rb'), caption='Отправляем в тг')
                                # bot.edit_message_text(text="telegramga yuboring", chat_id=call.message.chat.id,
                                #                       message_id=gif1_msg_id)
                                bot.delete_message(chat_id=call.message.chat.id, message_id=gif1_msg_id)

                                for i in range(len(file_path)):
                                    doc = open(file_path[i], 'rb')
                                    init_dw_output = db.init_download(chat_id=call.message.chat.id, src_type='instagram',
                                                                      date_of_join=date_today(),
                                                                      url=users[call.message.chat.id])
                                    print(init_dw_output)
                                    bot.send_document(call.message.chat.id, doc, reply_markup=mp.off_markup,
                                                      caption=mp.get_caption(language=language_usr))
                                    subprocess.run(f'rm {file_path[i]}', shell=True, capture_output=True)
                                file_path = False

                            else:
                                file_path = list()
                                gif1_msg = bot.send_message(call.message.chat.id, "Скачивается из Instagram",
                                                            reply_to_message_id=call.message.message_id)
                                gif1_msg_id = gif1_msg.message_id

                                output = upload_video_inst(chat_id=str(call.message.chat.id), url=users[call.message.chat.id])
                                if output == 'not found':
                                    bot.reply_to(call.message, f'🔒К сожалению, вы отправили ссылку из приватного аккаунта.\nСкачивание из приватного аккаунта невозможно!',
                                                 reply_markup=mp.off_markup)

                                for i in range(len(output)):
                                    file_path.append(os.getenv("downloads_pwd") + output[i])

                                # gif2 = types.InputMediaDocument(media=open('video/send.mp4', 'rb'), caption='Отправляем в тг')
                                # bot.edit_message_text(text="telegramga yuboring", chat_id=call.message.chat.id,
                                #                       message_id=gif1_msg_id)
                                bot.delete_message(chat_id=call.message.chat.id, message_id=gif1_msg_id)

                                for i in range(len(file_path)):
                                    doc = open(file_path[i], 'rb')
                                    init_dw_output = db.init_download(chat_id=call.message.chat.id, src_type='instagram', date_of_join=date_today(), url=users[call.message.chat.id])
                                    print(init_dw_output)
                                    if file_path[i][-3:] == 'jpg' or file_path[i][-3:] == 'jpeg' or file_path[i][-4:] == 'webp':
                                        bot.send_photo(call.message.chat.id, doc, reply_markup=mp.off_markup, caption=mp.get_caption(language=language_usr))
                                    else:
                                        bot.send_video(call.message.chat.id, doc, reply_markup=mp.off_markup, caption=mp.get_caption(language=language_usr))
                                    subprocess.run(f'rm {file_path[i]}', shell=True, capture_output=True)
                                file_path = False


                        else:
                            file_path = False

                        global ad_status
                        print(ad_status)
                        if ad_status == True:
                            send_random_post(chat_id=call.message.chat.id)
                        else:
                            pass




    except Exception as e:
        print(e)
        if e == selenium.common.exceptions.TimeoutException and language_usr == 'O’zbek 🇺🇿':
            bot.reply_to(call.message, f'Yuklash davomida xatolik yuz berdi! Iltimos, havolangizni tekshiring va qayta urinib ko’ring.', reply_markup=mp.off_markup)
        elif e== selenium.common.exceptions.TimeoutException:
            bot.reply_to(call.message, f'Не удалось скачать!\nПожалуйста, проверьте ссылку и повторите попытку.', reply_markup=mp.off_markup)



@bot.message_handler(content_types=["text"])
def text_handler(message):
    try:
        language_usr = db.get_language(chat_id=message.chat.id)
        file_path = False
        urls = extractor.find_urls(message.text)
        if len(urls) == 0:
            if language_usr == 'O’zbek 🇺🇿':
                bot.reply_to(message,
                             f'Noto’gri havola yubordingiz!\nInstagram, TikTok yoki YouTube dan to’g’ri havola yuboring.',
                             reply_markup=mp.off_markup)
                file_path = False
            else:
                bot.reply_to(message,
                             f'Неверная ссылка!\nОтправьте правильную ссылку из Instagram, TikTok или YouTube.',
                             reply_markup=mp.off_markup)
                file_path = False
        elif len(urls) > 1:
            if language_usr == 'O’zbek 🇺🇿':
                bot.reply_to(message,
                             f"juda ko'p havolalar\nInstagram, TikTok yoki YouTube dan to’g’ri havola yuboring.",
                             reply_markup=mp.off_markup)
                file_path = False
            else:
                bot.reply_to(message,
                             f'Слишком много ссылок!\nОтправьте правильную ссылку из Instagram, TikTok или YouTube.',
                             reply_markup=mp.off_markup)
        else:
            users[message.chat.id] = urls[0]
            global channel_link
            result = bot.get_chat_member(channel_username, message.chat.id)
            global sub_status
            if result.status == 'left' and sub_status == True and language_usr == 'Русский 🇷🇺':
                msg = bot.send_message(chat_id=message.chat.id, text=mp.channel_post_ru, reply_markup=mp.inline_sub_mp(channel_url=channel_link, language=language_usr), parse_mode='MARKDOWN')
                repl_message_user[message.chat.id] = msg.message_id
                file_path = False
            elif result.status == 'left' and sub_status == True and language_usr == 'O’zbek 🇺🇿':
                msg = bot.send_message(chat_id=message.chat.id, text=mp.channel_post_uz,reply_markup=mp.inline_sub_mp(channel_url=channel_link, language= language_usr), parse_mode='MARKDOWN')
                repl_message_user[message.chat.id] = msg.message_id
                file_path = False
            else:
                service = service_type(url=users[message.chat.id])
                if service == False and language_usr == 'O’zbek 🇺🇿':
                    bot.reply_to(message, f'Noto’gri havola yubordingiz!\nInstagram, TikTok yoki YouTube dan to’g’ri havola yuboring.', reply_markup=mp.off_markup)
                    file_path = False
                elif service == False and language_usr != 'O’zbek 🇺🇿':
                    bot.reply_to(message, f'Неверная ссылка!\nОтправьте правильную ссылку из Instagram, TikTok или YouTube.', reply_markup=mp.off_markup)
                    file_path = False

                elif service == 'youtube':
                    if language_usr == 'O’zbek 🇺🇿':
                        gif1_msg = bot.send_message(message.chat.id, "YouTubedan yuklanyabti…",
                                                    reply_to_message_id=message.message_id)
                        gif1_msg_id = gif1_msg.message_id

                        file_path = download_YT(url=users[message.chat.id], chatid=message.chat.id, ismp3=True)
                        if file_path == 'Video too long':
                            bot.reply_to(message, f'YouTube dan davomiyligi 10 daqiqadan ko’p bo’lmagan videoni yuklashingiz mumkin!\nIltimos, boshqa havola yuboring.', reply_markup=mp.off_markup)
                        elif file_path == Exception:
                                    bot.reply_to(message, f'Error, send link again', reply_markup=mp.off_markup)

                        # gif2 = types.InputMediaDocument(media=open('video/send.mp4', 'rb'), caption='Отправляем в тг')
                        # bot.edit_message_text(text="telegramga yuboring", chat_id=message.chat.id, message_id=gif1_msg_id)
                        bot.delete_message(chat_id=message.chat.id, message_id=gif1_msg_id)

                        doc = open(file_path, 'rb')
                        init_dw_output = db.init_download(chat_id=message.chat.id, src_type='youtube',
                                                          date_of_join=date_today(), url=users[message.chat.id])
                        print(init_dw_output)
                        bot.send_document(message.chat.id, doc, reply_markup=mp.off_markup,
                                          caption=mp.get_caption(language=language_usr), parse_mode="MARKDOWN")

                    else:
                        gif1_msg = bot.send_message(message.chat.id, "Скачиваем из Youtube...", reply_to_message_id=message.message_id)
                        gif1_msg_id = gif1_msg.message_id

                        file_path = download_YT(url=users[message.chat.id], chatid=message.chat.id, ismp3=True)
                        if file_path == 'Video too long':
                            bot.reply_to(message, f'Бот может скачивать видео из YouTube с продолжительностью не больше 10 минут!\nПожалуйста, отправьте ссылку другого видео.', reply_markup=mp.off_markup)
                        elif file_path == Exception:
                                    bot.reply_to(message, f'Error, send link again', reply_markup=mp.off_markup)

                        # gif2 = types.InputMediaDocument(media=open('video/send.mp4', 'rb'), caption='Отправляем в тг')
                        # bot.edit_message_text(text="Отправляем в телеграмм", chat_id=message.chat.id,
                        #                       message_id=gif1_msg_id)
                        bot.delete_message(chat_id=message.chat.id, message_id=gif1_msg_id)

                        doc = open(file_path, 'rb')
                        init_dw_output = db.init_download(chat_id=message.chat.id, src_type='youtube',
                                                          date_of_join=date_today(), url=users[message.chat.id])
                        print(init_dw_output)
                        bot.send_document(message.chat.id, doc, reply_markup=mp.off_markup,
                                          caption=mp.get_caption(language=language_usr), parse_mode="MARKDOWN")

                elif service == 'youtube_shorts':
                    if language_usr == 'O’zbek 🇺🇿':
                        gif1_msg = bot.send_message(message.chat.id, "YouTubedan yuklanyabti…",
                                                    reply_to_message_id=message.message_id)
                        gif1_msg_id = gif1_msg.message_id

                        file_path = download_YT(url=users[message.chat.id], chatid=message.chat.id, ismp3=False)
                        if file_path == 'Video too long':
                            bot.reply_to(message, f'YouTube dan davomiyligi 10 daqiqadan ko’p bo’lmagan videoni yuklashingiz mumkin!\nIltimos, boshqa havola yuboring.', reply_markup=mp.off_markup)
                        elif file_path == Exception:
                                    bot.reply_to(message, f'Error, send link again', reply_markup=mp.off_markup)

                        # gif2 = types.InputMediaDocument(media=open('video/send.mp4', 'rb'), caption='Отправляем в тг')
                        # bot.edit_message_text(text="telegramga yuboring", chat_id=message.chat.id, message_id=gif1_msg_id)
                        bot.delete_message(chat_id=message.chat.id, message_id=gif1_msg_id)

                        doc = open(file_path, 'rb')
                        init_dw_output = db.init_download(chat_id=message.chat.id, src_type='youtube_shorts',
                                                          date_of_join=date_today(), url=users[message.chat.id])
                        print(init_dw_output)
                        bot.send_document(message.chat.id, doc, reply_markup=mp.off_markup,
                                          caption=mp.get_caption(language=language_usr), parse_mode="MARKDOWN")

                    else:
                        gif1_msg = bot.send_message(message.chat.id, "Скачиваем из Youtube...", reply_to_message_id=message.message_id)
                        gif1_msg_id = gif1_msg.message_id

                        file_path = download_YT(url=users[message.chat.id], chatid=message.chat.id, ismp3=False)
                        if file_path == 'Video too long':
                            bot.reply_to(message, f'Бот может скачивать видео из YouTube с продолжительностью не больше 10 минут!\nПожалуйста, отправьте ссылку другого видео.', reply_markup=mp.off_markup)
                        elif file_path == Exception:
                                    bot.reply_to(message, f'Error, send link again', reply_markup=mp.off_markup)

                        # gif2 = types.InputMediaDocument(media=open('video/send.mp4', 'rb'), caption='Отправляем в тг')
                        # bot.edit_message_text(text="Отправляем в телеграмм", chat_id=message.chat.id,
                        #                       message_id=gif1_msg_id)
                        bot.delete_message(chat_id=message.chat.id, message_id=gif1_msg_id)

                        doc = open(file_path, 'rb')
                        init_dw_output = db.init_download(chat_id=message.chat.id, src_type='youtube_shorts',
                                                          date_of_join=date_today(), url=users[message.chat.id])
                        print(init_dw_output)
                        bot.send_document(message.chat.id, doc, reply_markup=mp.off_markup,
                                          caption=mp.get_caption(language=language_usr), parse_mode="MARKDOWN")

                elif service == 'tiktok':
                    if language_usr == 'O’zbek 🇺🇿':
                        gif1_msg = bot.send_message(message.chat.id, "TikTokdan yuklanyabti…", reply_to_message_id=message.message_id)
                        gif1_msg_id = gif1_msg.message_id

                        output = upload_video_tt(chat_id=str(message.chat.id), url = users[message.chat.id])
                        if output == 'not found':
                            bot.reply_to(message, f'media juda uzun', reply_markup=mp.off_markup)

                        file_path = output

                        bot.delete_message(chat_id=message.chat.id, message_id=gif1_msg_id)
                        print(file_path)
                        doc = open(file_path, 'rb')
                        init_dw_output = db.init_download(chat_id=message.chat.id, src_type='tiktok',date_of_join=date_today(), url=users[message.chat.id])
                        print(init_dw_output)

                        try:
                            bot.send_video(message.chat.id, doc, reply_markup=mp.off_markup, caption=mp.get_caption(language=language_usr))
                        except Exception as e:
                            bot.send_message(message.chat.id, "fayl juda og'ir", reply_markup=mp.off_markup)
                    else:
                        gif1_msg = bot.send_message(message.chat.id, "Скачиваем из TikTok...",
                                                    reply_to_message_id=message.message_id)
                        gif1_msg_id = gif1_msg.message_id

                        output = upload_video_tt(chat_id=str(message.chat.id), url=users[message.chat.id])
                        if output == 'not found':
                            bot.reply_to(message, f'Мы не можем найти видео по этой ссылке', reply_markup=mp.off_markup)

                        file_path = output

                        bot.delete_message(chat_id=message.chat.id, message_id=gif1_msg_id)

                        doc = open(file_path, 'rb')
                        init_dw_output = db.init_download(chat_id=message.chat.id, src_type='tiktok',
                                                          date_of_join=date_today(), url=users[message.chat.id])
                        print(init_dw_output)

                        try:
                            bot.send_video(message.chat.id, doc, reply_markup=mp.off_markup,
                                          caption=mp.get_caption(language=language_usr))
                        except Exception as e:
                            bot.send_message(message.chat.id, "файл слишком большой", reply_markup=mp.off_markup)


                elif service == 'instagram':
                    if language_usr == 'O’zbek 🇺🇿':
                        file_path = list()
                        gif1_msg = bot.send_message(message.chat.id, "Instagramdan yuklanyabti…",reply_to_message_id=message.message_id)
                        gif1_msg_id = gif1_msg.message_id

                        output = upload_video_inst(chat_id=str(message.chat.id), url=users[message.chat.id])
                        if output == 'not found':
                            bot.reply_to(message, f'🔒Afsuski, siz yuborgan havola yopiq akkaundan olingan\nYopiq akkauntdan yuklashni iloji yo’q!', reply_markup=mp.off_markup)

                        for i in range(len(output)):
                            file_path.append(os.getenv("downloads_pwd") + output[i])

                        # gif2 = types.InputMediaDocument(media=open('video/send.mp4', 'rb'), caption='Отправляем в тг')
                        # bot.edit_message_text(text="telegramga yuboring", chat_id=message.chat.id, message_id=gif1_msg_id)
                        bot.delete_message(chat_id=message.chat.id, message_id=gif1_msg_id)

                        for i in range(len(file_path)):
                            doc = open(file_path[i], 'rb')
                            init_dw_output = db.init_download(chat_id=message.chat.id, src_type='instagram', date_of_join=date_today(), url=users[message.chat.id])
                            print(init_dw_output)
                            if file_path[i][-3:] == 'jpg' or file_path[i][-3:] == 'jpeg' or file_path[i][-4:] == 'webp':
                                bot.send_photo(message.chat.id, doc, reply_markup=mp.off_markup, caption=mp.get_caption(language=language_usr))
                            else:
                                bot.send_video(message.chat.id, doc, reply_markup=mp.off_markup, caption=mp.get_caption(language=language_usr))
                            subprocess.run(f'rm {file_path[i]}', shell=True, capture_output=True)
                        file_path = False

                    else:
                        file_path = list()
                        gif1_msg = bot.send_message(message.chat.id, "Скачивается из Instagram...",
                                                    reply_to_message_id=message.message_id)
                        gif1_msg_id = gif1_msg.message_id

                        output = upload_video_inst(chat_id=str(message.chat.id), url=users[message.chat.id])
                        if output == 'not found':
                            bot.reply_to(message, f'🔒К сожалению, вы отправили ссылку из приватного аккаунта.\nСкачивание из приватного аккаунта невозможно!', reply_markup=mp.off_markup)

                        for i in range(len(output)):
                            file_path.append(os.getenv("downloads_pwd") + output[i])

                        # gif2 = types.InputMediaDocument(media=open('video/send.mp4', 'rb'), caption='Отправляем в тг')
                        # bot.edit_message_text(text="telegramga yuboring", chat_id=message.chat.id,
                        #                       message_id=gif1_msg_id)
                        bot.delete_message(chat_id=message.chat.id, message_id=gif1_msg_id)

                        for i in range(len(file_path)):
                            doc = open(file_path[i], 'rb')
                            init_dw_output = db.init_download(chat_id=message.chat.id, src_type='instagram', date_of_join=date_today(), url=users[message.chat.id])
                            print(init_dw_output)
                            if file_path[i][-3:] == 'jpg' or file_path[i][-3:] == 'jpeg' or file_path[i][-4:] == 'webp':
                                bot.send_photo(message.chat.id, doc, reply_markup=mp.off_markup, caption=mp.get_caption(language=language_usr))
                            else:
                                bot.send_video(message.chat.id, doc, reply_markup=mp.off_markup, caption=mp.get_caption(language=language_usr))
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
        if e == selenium.common.exceptions.TimeoutException and language_usr == 'O’zbek 🇺🇿':
            bot.reply_to(message, f'Yuklash davomida xatolik yuz berdi! Iltimos, havolangizni tekshiring va qayta urinib ko’ring.', reply_markup=mp.off_markup)
        elif e == selenium.common.exceptions.TimeoutException:
            bot.reply_to(message, f'Не удалось скачать!\nПожалуйста, проверьте ссылку и повторите попытку.', reply_markup=mp.off_markup)
        else:
            pass

    finally:
        if file_path == False:
            pass
        else:
            subprocess.run(f'rm {file_path}', shell=True, capture_output=True)

def service_type(url: str) -> 'Return service name of url':
    service_types = ['youtube_shorts','instagram', 'youtube', 'tiktok']
    if url.find('tiktok') == -1:
        service_types.remove('tiktok')
    if url.find('instagram') == -1:
        service_types.remove('instagram')
    if url.find('youtube.com/shorts') == -1 and url.find('youtu.be.com/shorts') == -1:
        service_types.remove('youtube_shorts')
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

