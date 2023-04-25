import os
import telebot
from dotenv import load_dotenv
from App.Wrappers import singleton


@singleton
class TelegramBot(object):

    def __init__(self):
        load_dotenv()
        self.__APIToken = os.getenv('TelegramBotToken')
        self._bot = telebot.TeleBot(self.__APIToken)

    @property
    def bot(self):
        return self._bot

    @staticmethod
    def polling(self):
        self._bot.infinity_polling()


tgbot = TelegramBot()
bot = tgbot.bot

