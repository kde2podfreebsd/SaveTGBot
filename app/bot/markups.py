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

choose_language = 'Выберите язык 🇷🇺 | 🇺🇿 Tilni tanlang'

menu_message_ru = '''
Привет, через этого бота вы можете скачивать видео из Instagram, TikTok и YouTube.

/language - Выберите язык 🇷🇺 | 🇺🇿 Tilni tanlang

Отправьте ссылку на видео, которое хотите скачать:
'''

menu_message_uz = '''
*Salom!*, ushbu bot yordamida Instagram, TikTok va YouTube dan video yuklab olishingiz mumkin.

/language - Выберите язык 🇷🇺 | 🇺🇿 Tilni tanlang

Yuklash kerak bo'lgan video havolasini yuboring:
'''

channel_post_ru = '''
Пожалуйста, чтобы пользоваться ботом подпишитесь на наш канал и нажмите на кнопку «Подтвердить» 👇🏻

'''

channel_post_uz = '''
Iltimos, botdan foydalanish uchun kanalimizga obuna bo'ling va «Tasdiqlash» tugmasini bosing 👇🏻
'''


def inline_sub_mp(channel_url:str, language:str):
    channel_post_mp = types.InlineKeyboardMarkup(row_width=1)

    if language == 'O’zbek 🇺🇿':
        channel = types.InlineKeyboardButton(text='Kanalga obuna bo’lish ⬅️', url=channel_url)
        check = types.InlineKeyboardButton(text='✅Tasdiqlash', callback_data=f'check')
    else:
        channel = types.InlineKeyboardButton(text='Перейти на канал', url=channel_url)
        check = types.InlineKeyboardButton(text='✅Подтвердить', callback_data=f'check')

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


def get_stat_msg(number_of_users,users_today,all_downloads,today_downloads,youtube,tiktok,instagram,youtube_shorts):
    msg = f'''
Статистика бота

Количество всех пользователей бота: {number_of_users}
Количество пользователей за сегодня: {users_today}
Количество всех скачанных видео: {all_downloads}
Количество всех скачанных видео за сегодня: {today_downloads}
Количество скачанных видео (за все время) из тикток: {tiktok}
Количество скачанных видео (за все время) из инстаграм: {instagram}
Количество скачанных аудио (за все время) из ютуб: {youtube}
Колличество скачанных видео (за все время) из ютуб: {youtube_shorts}
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
itembtn1 = types.KeyboardButton('Русский 🇷🇺')
itembtn2 = types.KeyboardButton('O’zbek 🇺🇿')
language.add(itembtn1,itembtn2)

def get_caption(language:str):
    if language == "O’zbek 🇺🇿":
        return "📥 @UzSavebot orqali yuklandi\n\nhttps://t.me/+KYRaNYz3BMo0ZmMy"
    else:
        return f'📥 Скачано из @UzSavebot\n\nhttps://t.me/+KYRaNYz3BMo0ZmMy'

