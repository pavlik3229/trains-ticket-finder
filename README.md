# trains-ticket-finder

Telegram-бот для отслеживания мест в поездах.

## Окружение

- Python 3.12+
- Docker и Docker Compose — если нужен запуск в контейнере
- Файл `.env` в корне проекта рядом с `compose.yml`

```env
TG_TOKEN=ваш_токен_бота
```

## Установка и запуск локально

```zsh
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python -m src.main
```

## Запуск в Docker

Запускайте команду из корня проекта:

```zsh
docker compose up --build
```

## Список отслеживания

Список поездов задаётся в `src/parser.py` в `Parser.__init__`:

```python
self.trains = [
	{
		'repr': '733Б',
		'link': 'https://pass.rw.by/ru/route/?from=...&to=...&date=tomorrow',
		'name': 'Минск -> Берёза / 18.04.26 / 17.20 - 20.02',
		'places': {},
	},
]
```

Меняйте `repr`, `link` и `name` под нужные маршруты.

