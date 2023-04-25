from App.TelegramBot.Bot import bot, TelegramBot
from App.TelegramBot import Markups as mk
from App.MediaUploader import MediaUploader


@bot.message_handler(commands=['start', 'language'])
def language(message) -> None:
    bot.send_message(chat_id=message.chat.id, text=mk.choose_language_text, reply_markup=mk.choose_language_markup(), parse_mode='MARKDOWN')


@bot.message_handler(content_types=['text'])
def text_handler(message):
    service_urls = MediaUploader.find_urls(text=message.text)
    if service_urls is False:
        bot.send_message(chat_id=message.chat.id, text=mk.not_found_service_urls, reply_markup=mk.off_markup, parse_mode='MARKDOWN')
    else:
        for url in service_urls:
            service = MediaUploader.select_service_type(url=url)
            print(service)
            match service:
                case 'youtube_shorts':
                    pass

                case 'instagram':
                    pass

                case 'youtube':
                    pass

                case 'tiktok':
                    pass


@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    if call.data == 'ru':
        print('user set ru')
    if call.data == 'en':
        print('user set en')


bot.polling()

