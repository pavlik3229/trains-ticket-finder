import time
import logging

from .parser import Parser
from .bot import Bot

logger = logging.getLogger(__name__)

class BeljdTicketCheckerApp:
    def __init__(self):
        self._bot = Bot()
        self._parser = Parser

    def start(self):
        while True:
            try:
                parser = self._parser(self._bot)
                parser.run()

            except Exception as e:
                logger.error('Парсер остановлен из-за ошибки %s', e)
                try:
                    self._bot.send_error_message(e)
                except:
                    logger.warning('Не удалось отправить сообщение об ошибке')

            finally:
                logger.info('Перезагрузка через 2 минуты')
                try:
                    self._bot.send_message_to_user("Парсер будет перезапущен через 2 минуты")
                except:
                    logger.warning('Не удалось отправить сообщение о перезапуске')
                time.sleep(120)
