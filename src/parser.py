import threading
import time
import logging
import requests
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)


class Parser:

    def __init__(self, bot):
        self.trains = [
            {'repr': '733Б',

             # ссылка на страницу маршрута
             'link': 'https://pass.rw.by/ru/route/?from=Минск-Пассажирский&from_exp=0&from_esr=0&to=Берёза&to_exp=2100003&to_esr=134116&front_date=завтра&date=tomorrow',
             'name': 'Минск -> Берёза/ 18.04.26 / 17.20: - 20.02',
             'places': {},
             },

            # {'repr': '',
            #  'link': '',
            #  'name': '->/ 00.00 / 00:00 - 00:00',
            #  'places': {},
            #  },

        ]

        self.target_divs = {
            # train['repr']: (sch-table__cell cell-4 div, Empty or not)
        }
        self.bot = bot
        self.error_delay = 60
        self.started_message()

    def started_message(self):
        self.bot.send_message_to_user("Парсер запущен")

    def get_target(self):
        for train in self.trains:
            try:
                response = requests.get(train['link']).text
                soup = BeautifulSoup(response, 'lxml')
                target_train = soup.find_all('div', attrs={'data-train-number': train['repr']})[0]
                target = (target_train.find('div', attrs={'class': 'sch-table__cell cell-4'}), True)
                if target[0] is None:
                    target = (target_train.find('div', attrs={'class': 'sch-table__cell cell-4 empty'}), False)

                self.target_divs[train['repr']] = target
                logger.info('Таргет получен')
            except Exception as e:
                logger.error('Ошибка при получении таргета: %s', e)
                self.bot.send_error_message(e)
                self.bot.send_message_to_user(f"Ожидание после ошибки {self.error_delay}c")
                time.sleep(self.error_delay)

    def ticket_cheker(self):
        for train in self.trains:

            div = self.target_divs[train['repr']]
            if not div[1]:
                train['places'] = {}

            else:
                target = div[0]
                places = {}
                for name_tag in target.select('.sch-table__t-name'):
                    name = name_tag.get_text(strip=True)
                    quant_tag = name_tag.find_next('a')
                    count = quant_tag.find('span').get_text(strip=True) if quant_tag and quant_tag.find('span') else '0'
                    places[name] = int(count)
                train['places'] = places
            logger.info(f"Билеты для поезда {train['name']} прочеканы")

    def run(self):
        self.bot.trains = self.trains

        thread = threading.Thread(target=self.bot.run)
        thread.daemon = True
        thread.start()

        while True:
            if self.bot.running:
                self.get_target()
                self.ticket_cheker()
                self.bot.send_report(self.trains)
            else:
                logger.info('Ожидание бота')
            time.sleep(self.bot.delay)
