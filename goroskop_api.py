import requests
from bs4 import BeautifulSoup
import time
import threading
from apscheduler.schedulers.background import BackgroundScheduler



# Словарь для хранения подписок на ежедневный гороскоп
daily_subscriptions = {}

# Инициализация планировщика
scheduler = BackgroundScheduler()
scheduler.start()

# Функция для отправки ежедневных гороскопов
def send_daily_horoscopes():
    now = datetime.datetime.now()
    print(f"Запущена отправка ежедневных гороскопов в {now}")

    for chat_id, sub_data in daily_subscriptions.items():
        try:
            sign = sub_data['sign']
            text = get_horoscope(sign, "🔮 Обычный гороскоп")

            # Добавляем заголовок
            today = datetime.datetime.now().strftime("%d.%m.%Y")
            message = f"✨ Ежедневный гороскоп для {get_zodiac_sign_display1(sign)} на {today} ✨\n\n{text}"

            bot.send_message(chat_id, message)

        except Exception as e:
            print(f"Ошибка при отправке гороскопа в чат {chat_id}: {e}")


# Настраиваем ежедневную отправку в 9:00 утра
scheduler.add_job(
    send_daily_horoscopes,
    'cron',
    hour=9,
    minute=00,
    timezone='Europe/Moscow'
)

def get_zodiac_sign_display1(day: int, month: int) -> str:
    sign_map = {
        "capricorn": "Козерогов",
        "aquarius": "Водолеев",
        "pisces": "Рыб",
        "aries": "Овнов",
        "taurus": "Телецов",
        "gemini": "Близнецов",
        "cancer": "Раков",
        "leo": "Львов",
        "virgo": "Дев",
        "libra": "Весов",
        "scorpio": "Скорпионов",
        "sagittarius": "Стрелецов"
    }
    return sign_map.get(get_zodiac_sign(day, month), "Неизвестный знак")

# Функция для парсинга гороскопа с сайта
def get_horoscope(sign, horoscope_type):
    # Преобразуем тип гороскопа в URL-часть
    type_map = {
        "🔮 Обычный гороскоп": "today",
        "❤️ Любовный гороскоп": "love",
        "💼 Рабочий гороскоп": "business"
    }

    url_type = type_map.get(horoscope_type, "today")
    url = f"https://horo.mail.ru/prediction/{sign.lower()}/{url_type}/"

    try:
        response = requests.get(url)
        response.raise_for_status()  # Проверяем на ошибки HTTP

        soup = BeautifulSoup(response.text, 'html.parser')

        # Ищем основной текст гороскопа
        content = soup.find('div', class_='b6a5d4949c e45a4c1552')
        if not content:
            return "Не удалось найти гороскоп для этого знака."

        # Удаляем ненужные элементы (например, рекламу)
        for elem in content.find_all(['a', 'script', 'style', 'img']):
            elem.decompose()

        # Получаем чистый текст
        text = content.get_text(separator='\n', strip=True)

        # Укорачиваем слишком длинные гороскопы
        if len(text) > 4000:
            text = text[:4000] + "..."

        return text if text else "Гороскоп временно недоступен, попробуйте позже."

    except Exception as e:
        print(f"Ошибка при парсинге гороскопа: {e}")
        return "Не удалось получить гороскоп. Попробуйте позже."

# Функция определения знака зодиака
def get_zodiac_sign(day: int, month: int) -> str:
    if (month == 12 and day >= 22) or (month == 1 and day <= 20):
        return "capricorn"  # Козерог
    elif (month == 1 and day >= 21) or (month == 2 and day <= 18):
        return "aquarius"  # Водолей
    elif (month == 2 and day >= 19 and day <= 29) or (month == 3 and day <= 20):
        return "pisces"  # Рыбы
    elif (month == 3 and day >= 21) or (month == 4 and day <= 20):
        return "aries"  # Овен
    elif (month == 4 and day >= 21) or (month == 5 and day <= 21):
        return "taurus"  # Телец
    elif (month == 5 and day >= 22) or (month == 6 and day <= 21):
        return "gemini"  # Близнецы
    elif (month == 6 and day >= 22) or (month == 7 and day <= 22):
        return "cancer"  # Рак
    elif (month == 7 and day >= 23) or (month == 8 and day <= 23):
        return "leo"  # Лев
    elif (month == 8 and day >= 24) or (month == 9 and day <= 23):
        return "virgo"  # Дева
    elif (month == 9 and day >= 24) or (month == 10 and day <= 23):
        return "libra"  # Весы
    elif (month == 10 and day >= 24) or (month == 11 and day <= 22):
        return "scorpio"  # Скорпион
    else:
        return "sagittarius"  # Стрелец

@bot.message_handler(func=lambda message: message.text == "📅 Подписаться на ежедневный гороскоп")
def handle_subscribe(message):
    if dd == 0 or mm == 0:
        bot.send_message(message.chat.id, "❌ Сначала укажите вашу дату рождения")
        return

    sign = get_zodiac_sign(dd, mm)
    daily_subscriptions[message.chat.id] = {'sign': sign}

    bot.send_message(
        message.chat.id,
        f"✅ Вы подписались на ежедневный гороскоп для {get_zodiac_sign_display1(dd, mm)}!\n"
        f"Гороскоп будет приходить ежедневно в 9:00 утра.",
        reply_markup=keyboard
    )


@bot.message_handler(func=lambda message: message.text == "❌ Отписаться")
def handle_unsubscribe(message):
    chat_id = message.chat.id
    if chat_id in daily_subscriptions:
        del daily_subscriptions[chat_id]
        bot.send_message(chat_id, "❌ Вы отменили подписку на ежедневный гороскоп.", reply_markup=keyboard)
    else:
        bot.send_message(chat_id, "ℹ️ У вас нет активной подписки.", reply_markup=keyboard)

def get_work_horoscope(sign):
    # Словарь для преобразования знаков в URL-формат Rambler
    sign_mapping = {
        "capricorn": "capricorn",
        "aquarius": "aquarius",
        "pisces": "pisces",
        "aries": "aries",
        "taurus": "taurus",
        "gemini": "gemini",
        "cancer": "cancer",
        "leo": "leo",
        "virgo": "virgo",
        "libra": "libra",
        "scorpio": "scorpio",
        "sagittarius": "sagittarius"
    }

    rambler_sign = sign_mapping.get(sign.lower(), "deva")
    url = f"https://horoscopes.rambler.ru/{rambler_sign}/career/"

    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(url, headers=headers)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')

        # Ищем основной текст гороскопа на Rambler
        content = soup.find('div', class_='dGWT9 cidDQ')
        if not content:
            return "Не удалось найти рабочий гороскоп для этого знака."

        # Удаляем ненужные элементы
        for elem in content.find_all(['a', 'script', 'style', 'img', 'iframe']):
            elem.decompose()

        # Получаем чистый текст и немного его форматируем
        text = content.get_text(separator='\n', strip=True)
        text = text.replace('Читайте также:', '').strip()

        # Укорачиваем слишком длинные гороскопы
        if len(text) > 4000:
            text = text[:4000] + "..."

        return text if text else "Рабочий гороскоп временно недоступен, попробуйте позже."

    except Exception as e:
        print(f"Ошибка при парсинге рабочего гороскопа: {e}")
        return "Не удалось получить рабочий гороскоп. Попробуйте позже."

def get_love_horoscope(sign):
    # Словарь для преобразования знаков в URL-формат Rambler
    sign_mapping = {
        "capricorn": "capricorn",
        "aquarius": "aquarius",
        "pisces": "pisces",
        "aries": "aries",
        "taurus": "taurus",
        "gemini": "gemini",
        "cancer": "cancer",
        "leo": "leo",
        "virgo": "virgo",
        "libra": "libra",
        "scorpio": "scorpio",
        "sagittarius": "sagittarius"
    }

    rambler_sign = sign_mapping.get(sign.lower(), "oven")
    url = f"https://horoscopes.rambler.ru/{rambler_sign}/erotic/weekly/"

    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(url, headers=headers)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')

        # Ищем основной текст гороскопа на Rambler
        content = soup.find('div', class_='yLX2x Jgl8N vXHy6 YZauy')
        if not content:
            return "Не удалось найти любовный гороскоп для этого знака."

        # Удаляем ненужные элементы
        for elem in content.find_all(['a', 'script', 'style', 'img', 'iframe']):
            elem.decompose()

        # Получаем чистый текст и немного его форматируем
        text = content.get_text(separator='\n', strip=True)
        text = text.replace('Читайте также:', '').strip()

        # Укорачиваем слишком длинные гороскопы
        if len(text) > 4000:
            text = text[:4000] + "..."

        return text if text else "Любовный гороскоп временно недоступен, попробуйте позже."

    except Exception as e:
        print(f"Ошибка при парсинге любовного гороскопа: {e}")
        return "Не удалось получить любовный гороскоп. Попробуйте позже."