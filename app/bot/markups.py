import os
from telebot import types
from dotenv import load_dotenv

config = load_dotenv()
off_markup = types.ReplyKeyboardRemove(selective=False)

def get_inline_url_btn(text:str, url:str) -> types.InlineKeyboardMarkup:
    channel_url_mp = types.InlineKeyboardMarkup(row_width=1)
    channel = types.InlineKeyboardButton(text=text, url=f'{url}')
    channel_url_mp.add(channel)
    return channel_url_mp

invalid_url = 'Нет ссылки или ссылка не валидна!'
toomuch_urls = 'Слишком много ссылок... Прикрепите только одну ссылку'

menu_message = '''
*Приветствую!*
Ниже я расскажу вам как пользоваться ботом!

    /language - Выберите язык
   
    1. Зайдите в одну из социальных сетей.
    2. Выберите интересное для вас видео.
    3. Нажми кнопку «Скопировать».
    4. Отправьте нашему боту и получите ваш файл!
       
Бот может скачивать с:
    1. TikTok (без водяного знака)
    2. YouTube (Только звук)
    3. Instagram (Посты, истории, Reels)
'''

channel_post = '''
*Пожалуйста, подпишись на наш канал!*
Поддержите подпиской на канал и затем нажмите кнопку «Подписался » чтобы получить видео.

*Для использования Бота , необходимо подписаться на канал!*
'''

def inline_sub_mp(channel_url:str):
    channel_post_mp = types.InlineKeyboardMarkup(row_width=1)

    channel = types.InlineKeyboardButton(text='Перейти на канал', url=channel_url)
    check = types.InlineKeyboardButton(text='✅Подписался', callback_data='check')

    channel_post_mp.add(channel, check)
    return channel_post_mp

menu_admin = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
itembtn1 = types.KeyboardButton('/stat')
itembtn2 = types.KeyboardButton('/create_referal')
itembtn3 = types.KeyboardButton('/referal_stat')
itembtn4 = types.KeyboardButton('/mail_users')
itembtn5 = types.KeyboardButton('/subscription')
itembtn6 = types.KeyboardButton('/ads')
menu_admin.add(itembtn1,itembtn2,itembtn3,itembtn4,itembtn5,itembtn6)


def get_stat_msg(number_of_users,users_today,all_downloads,today_downloads,youtube,tiktok,instagram):
    msg = f'''
Статистика бота

Количество всех пользователей бота: {number_of_users}
Количество пользователей за сегодня: {users_today}
Количество всех скачанных видео: {all_downloads}
Количество всех скачанных видео за сегодня: {today_downloads}
Количество скачанных видео (за все время) из тикток: {tiktok}
Количество скачанных видео (за все время) из инстаграм: {instagram}
Количество скачанных аудио (за все время) из ютуб: {youtube}
'''
    return msg

mail_users_msg = '''
Напишите текст в разметке MARKDOWN
'''

subscription = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
itembtn1 = types.KeyboardButton('/turn_on_subscription')
itembtn2 = types.KeyboardButton('/turn_off_subscription')
itembtn3 = types.KeyboardButton('/change_channel')
itembtn4 = types.KeyboardButton('/admin_menu')
subscription.add(itembtn1,itembtn2,itembtn3,itembtn4)

change_group = 'Отправьте ссылку на канал для обязательной подписки. Аккаунт привзяанный к приложению телетона должен быть администратором канала'
not_admin = 'account is not admin'

ads_menu = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
itembtn1 = types.KeyboardButton('/turn_on_ads')
itembtn2 = types.KeyboardButton('/turn_off_ads')
itembtn3 = types.KeyboardButton('/new_ad')
itembtn4 = types.KeyboardButton('/delete_ad')
itembtn5 = types.KeyboardButton('/list_ad')
itembtn6 = types.KeyboardButton('/get_ad')
itembtn7 = types.KeyboardButton('/admin_menu')

ads_menu.add(itembtn1,itembtn2,itembtn3,itembtn4,itembtn5,itembtn6,itembtn7)

confirm_ad = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
itembtn1 = types.KeyboardButton('/conirm_ad')
itembtn2 = types.KeyboardButton('/decline_ad')
confirm_ad.add(itembtn1,itembtn2)

language = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
itembtn1 = types.KeyboardButton('Русский')
itembtn2 = types.KeyboardButton('Узбекский')
language.add(itembtn1,itembtn2)

def get_caption(url:str):
    msg = url + f'\n\n{os.getenv("banner")}'
    return msg


markup_banner_inline = types.InlineKeyboardMarkup()
switch_button = types.InlineKeyboardButton(text='Попробовать➡️', url="https://t.me/UzSavebot")
markup_banner_inline.add(switch_button)
