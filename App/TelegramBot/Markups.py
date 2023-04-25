from telebot import types

off_markup = types.ReplyKeyboardRemove(selective=False)
choose_language_text = "Hello, choose language"
not_found_service_urls = "Sorry, but bot cant find urls in message or url is not valid"


def choose_language_markup():
    languageMK = types.InlineKeyboardMarkup(row_width=1)

    ru = types.InlineKeyboardButton(text='RU', callback_data='ru')
    en = types.InlineKeyboardButton(text='EN', callback_data='en')

    languageMK.add(ru, en)
    return languageMK
