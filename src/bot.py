import time
import logging
from telebot import telebot
from pathlib import Path
from os import environ

from dotenv import load_dotenv



load_dotenv(Path(__file__).resolve().parents[1] / '.env')

logger = logging.getLogger(__name__)


class Bot:
    def __init__(self):
        token = environ.get('TG_TOKEN')
        if not token:
            raise RuntimeError("Не найден TG_TOKEN. Проверьте файл .env в корне проекта или переменные окружения.")

        self.spam_flag = True
        self.old_info = None
        self.delay = 10
        self.bot = telebot.TeleBot(token)

        self.trains = []
        self.user_chat_id = None
        self.running = False

        self.bot.message_handler(commands=['start'])(self.start)
        self.bot.message_handler(commands=['help'])(self.help)
        self.bot.message_handler(commands=['spam_off'])(self.spam)
        self.bot.message_handler(commands=['list_trains'])(self.send_trains_list)
        self.bot.message_handler(commands=['report'])(self.report_command)

    def start(self, message):
        self.running = True
        self.spam_flag = True
        self.user_chat_id = message.from_user.id
        self.help(message)
        self.bot.send_message(self.user_chat_id, f"Бот запущен, до проверки {self.delay} секунд")
        self.send_trains_list(message)
        logger.info('Бот запущен')


    def error_start(self):
        self.running = True
        self.spam_flag = True
        self.bot.send_message(self.user_chat_id, f"Бот запущен, до проверки {self.delay} секунд")
        self.send_trains_list()
        logger.info('Бот запущен')


    def spam(self, message):
        self.spam_flag = False
        self.bot.send_message(self.user_chat_id, 'Сообщения о отсутствии изменений будут отключены, для включения перезапустите бота')

    def help(self, message):
        self.bot.send_message(self.user_chat_id,
                              "Список команд:\n"
                              "/start - запуск бота\n"
                              "/list_trains - информация о отслеживаемых поездах\n"
                              "/spam_off - отключение сообщения об отсутствии изменений\n"
                              "/report - свежий репорт\n"
                              "/help - вызов этого списка команд"
                              )

    def send_message_to_user(self, text):
        if self.user_chat_id:
            self.bot.send_message(self.user_chat_id, text)

    def report_command(self, message):
        self.old_info = None
        self.spam_flag = True

    def send_report(self, trains):
        markup = telebot.types.InlineKeyboardMarkup()



        info_message = 'Текущая информация: \n'


        for train in trains:
            info_message += f"\n{train['name']}: \n"
            if not train['places']:
                info_message += 'мест нет\n'
            else:
                for name in train['places']:
                    info_message += f"{name}: {train['places'][name]} \n"

            train_btn = telebot.types.InlineKeyboardButton(text=train['name'], url=train['link'])
            markup.add(train_btn)
        info_message += f'\nСледущее обновление через {self.delay} секунд'

        if self.old_info == info_message:
            if self.spam_flag:
                logger.info('Отправлен репорт о том что изменений нет----' + str(time.ctime(time.time())))
                self.bot.send_message(self.user_chat_id, f'Изменений нет, до следующей проверки {self.delay} секунд')
            else:
                logger.warning('Изменений нет, репорт не отправлен ' + str(time.ctime(time.time())))
                logger.info('репорт: ' + '\n' + info_message)
        else:
            logger.info('Отправлен репорт  ' + str(time.ctime(time.time())) + '\n' + info_message)
            self.bot.send_message(self.user_chat_id, info_message, reply_markup=markup)

        self.old_info = info_message

    def send_error_message(self, e):
        self.bot.send_message(self.user_chat_id, "Бот остановлен из-за ошибки:\n" + str(e))

    def send_trains_list(self, message=None):
        markup = telebot.types.InlineKeyboardMarkup()

        for train in self.trains:
            train_btn = telebot.types.InlineKeyboardButton(text=train['name'], url=train['link'])
            markup.add(train_btn)

        self.bot.send_message(self.user_chat_id, "Список отслеживаемых поездов: ", reply_markup=markup)


    def run(self):
        self.bot.infinity_polling()