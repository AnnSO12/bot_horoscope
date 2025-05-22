import telebot
from telebot.types import ReplyKeyboardMarkup
import datetime
import requests
import json
from bs4 import BeautifulSoup
from apscheduler.schedulers.background import BackgroundScheduler

bot = telebot.TeleBot("")
dd = 0
mm = 0
yy = 0
user_names = {}
bg_signs = {}

# Словарь для хранения подписок на ежедневный гороскоп

daily_subscriptions = {}

# Создаем клавиатуру
keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
keyboard.row("🔮 Обычный гороскоп", "💼 Рабочий гороскоп")
keyboard.row("❤️ Любовный гороскоп", "🐺 Тотемное животное")
keyboard.row("🧮 Ангельское число", "👩‍❤️‍👨 Совместимость")
keyboard.row("📅 Подписаться на ежедневный гороскоп", "❌ Отписаться")

# отдельная клавиатура для совместимости
keyboard_sov = ReplyKeyboardMarkup(resize_keyboard=True)
keyboard_sov.row('Совместимость по именам')
keyboard_sov.row('Совместимость по знакам зодиака')
keyboard_sov.row('⬅️ Назад')

# Инициализация планировщика
scheduler = BackgroundScheduler()
scheduler.start()

user_placement = {}

user_start = 0
user_sov_choice = 1
user_sov_name1 = 2
user_sov_name2 = 3
user_sov_data1 = 4
user_sov_data2 = 5


@bot.message_handler(commands=['start'])
def send_welcome(message):
    user_placement[message.chat.id] = user_start
    bot.send_message(message.chat.id,
                     "👋 Привет! Я бот-гороскоп. Напиши свою дату рождения в формате ДД.ММ.ГГГГ(например: 14.05.2006).")


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


def back(message):
    user_id = message.chat.id
    state = user_placement[user_id]

    if state == user_sov_choice:
        bot.send_message(message.chat.id, "Выберите действие:", reply_markup=keyboard)
        user_placement[user_id] = user_start
    elif state == user_sov_name1 or state == user_sov_name2:
        bot.send_message(message.chat.id, "Какую совместимость вы хотите узнать?", reply_markup=keyboard_sov)
        user_placement[user_id] = user_sov_choice
    elif state == user_sov_data1 or state == user_sov_data2:
        bot.send_message(message.chat.id, "Какую совместимость вы хотите узнать?", reply_markup=keyboard_sov)
        user_placement[user_id] = user_sov_choice
    else:
        bot.send_message(message.chat.id, "Вы в главном меню.", reply_markup=keyboard)
        user_placement[user_id] = user_start


# Тотемное животное
def get_totem_info(day: int, month: int) -> tuple[str, str | None]:
    zodiac = get_zodiac_sign_display_from_eng(get_zodiac_sign(day, month))
    animals = {
        "Овен": (
            "🐶 Собака: Воин света, облаченный в шерсть! Ваша верность – легенда, ваша храбрость – миф. "
            "Вы бежите навстречу приключениям, даже если это всего лишь доставка пиццы. "
            "Идеалы? Верность хозяйской руке! Энергия? Неиссякаемый источник лая, способного разрушить тишину вселенной! "
            "Ваше кредо: 'За мной! Там кошка!",
            "https://i.pinimg.com/736x/2e/99/43/2e99438f37e830d04d25da78fd8f6524.jpg"
        ),
        "Телец": (
            "🐢 Черепаха: Мудрец, познавший дзен задолго до появления интернета! Время для вас – иллюзия, стабильность – константа. "
            "Вы плывете по реке жизни с грацией баржи, груженной мудростью. "
            "Комфорт – ваша главная ценность, настойчивость – способна сдвинуть гору, если на её вершине одуванчик.",
            "https://i.pinimg.com/736x/b8/ce/d0/b8ced0c33c6acaebd5a36f5e9ef4e7aa.jpg"
        ),
        "Близнецы": (
            "🐬 Дельфин: Гений коммуникации, взламывающий коды социальных сетей одним щелчком плавника! "
            "Любопытство – ваш двигатель. "
            "Вы – проводник информации и повелитель океанских вечеринок!",
            "https://i.pinimg.com/736x/55/00/3a/55003a9356aa22760e32c3a5a37dbe6a.jpg"
        ),
        "Рак": (
            "🐧 Пингвин: Хранитель домашнего очага, собирающий тепло по кусочкам в суровых льдах бытия! "
            "Семья – ваш якорь, преданность – ваша мантра. Вы создаёте уют даже там, где его быть не может.",
            "https://i.pinimg.com/736x/88/4b/89/884b8919119c2e0e9aad2b7effe826e7.jpg"
        ),
        "Лев": (
            "🐺 Волк: Король саванны, затерявшийся в городских джунглях! Благородный лидер? Возможно... "
            "Доверяйте интуиции – она подскажет, где стейк! Войте? Пусть мир услышит вашу мощь!",
            "https://pin.it/4SGI8f4mC"
        ),
        "Дева": (
            "🦝 Енот: Архитектор хаоса, превращающий беспорядок в искусство! "
            "Вы наведёте порядок... в чужом мусорном баке. Практичность — ваш дар. Ловкие лапки? Неотразимы!",
            "https://pin.it/6ahccMCsk"
        ),
        "Весы": (
            "🦦 Выдра: Гармонизатор вселенной, ищущий баланс даже между игрой и медитацией. "
            "Доброжелательность — ваш козырь, дипломатия — ваше второе имя!",
            "https://pin.it/4X8xNeRAK"
        ),
        "Скорпион": (
            "🐱 Кот: Ночной охотник, чья страсть горит ярче звезд! Загадочный, независимый и абсолютно непредсказуемый. "
            "Интуиция? Охота на лазерную указку — священна!",
            "https://i.pinimg.com/736x/69/d4/91/69d491c5c27bce7f2b58cf9a4aa86424.jpg"
        ),
        "Стрелец": (
            "🐴 Лошадь:  Повелитель ветра и оптимизма, скачущий к горизонту. "
            "Пусть ветер свободы развевает вашу гриву и приносит запах новых приключений!",
            "https://pin.it/23tirzJXv"
        ),
        "Козерог": (
            "🐐 Козел: Архитектор успеха, взбирающийся по склонам к вершине! "
            "Ни одна гора не устоит перед вашим упорством… и аппетитом!",
            "https://i.pinimg.com/736x/eb/c7/fe/ebc7feaee202ec5f18ffb2ebafcdcec2.jpg"
        ),
        "Водолей": (
            "🦅 Орел: Провидец и мыслитель, взлетающий выше предрассудков. "
            "Ваши идеи меняют мир. Полетите? Только вверх!",
            "https://i.pinimg.com/736x/19/1a/4f/191a4fdbc00a64e6957c5f269ec90083.jpg"
        ),
        "Рыбы": (
            "🐬 Дельфин: Творец гармонии, чей вдохновляющий поток ведёт к счастью. "
            "Творите чудеса добротой, каждый день!",
            "https://i.pinimg.com/736x/cd/63/95/cd6395c6b4efb9a815cd94e2a8409a05.jpg"
        )
    }
    return animals.get(zodiac, ("🐾 Не удалось определить тотемное животное", None))


def get_angel_number_text(day: int, month: int, year: int) -> str:
    total = sum(int(d) for d in f"{day:02d}{month:02d}{year}")
    while total > 9:
        total = sum(int(d) for d in str(total))
    triple = str(total) * 3

    angel_numbers = {
        "111": "✨ 111 — Станция Материализации открыта! Ваши мысли становятся реальностью. Следите за тем, что заказываете, чтобы не получить билет в один конец на Луну вместо повышения на работе.",
        "222": "🌟 222 — Доверяйте процессу, даже если не понимаете, что происходит. Вселенная работает над вашим проектом.",
        "333": "🔥 333 — Вы не одиноки! Вселенная на вашей стороне, а вознесенные мастера готовы поддержать вас. Просто попросите их о помощи.",
        "444": "🛡️ 444 — Ангелы наблюдают за вами. Помните, что все ваши поступки видны и важны.",
        "555": "🌪️ 555 — Готовьтесь к большим переменам. Ваша жизнь может перевернуться с ног на голову, но это всегда к лучшему.",
        "666": "🧘 666 — Перестаньте зацикливаться на материальном. В жизни есть вещи поважнее, найдите свой духовный баланс.",
        "777": "🎯 777 — Вы на пути к просветлению. Продолжайте сиять и делиться своей мудростью.",
        "888": "💰 888 — Изобилие приближается. Приготовьтесь принять все блага, которые вам предлагает Вселенная.",
        "999": "🌌 999 — Завершение важного этапа. Время прощаться с прошлым и двигаться вперед с оптимизмом."
    }

    return angel_numbers.get(triple, "🔍 Ангельское число не найдено, попробуйте ещё раз.")


def get_zodiac_sign_display_from_eng(sign):
    sign_map = {
        "capricorn": "Козерог",
        "aquarius": "Водолей",
        "pisces": "Рыбы",
        "aries": "Овен",
        "taurus": "Телец",
        "gemini": "Близнецы",
        "cancer": "Рак",
        "leo": "Лев",
        "virgo": "Дева",
        "libra": "Весы",
        "scorpio": "Скорпион",
        "sagittarius": "Стрелец",
        "error": "error"
    }
    return sign_map.get(sign, "Неизвестный знак")


def get_zodiac_sign_display(day: int, month: int) -> str:
    sign_map = {
        "capricorn": "Козерог",
        "aquarius": "Водолей",
        "pisces": "Рыбы",
        "aries": "Овен",
        "taurus": "Телец",
        "gemini": "Близнецы",
        "cancer": "Рак",
        "leo": "Лев",
        "virgo": "Дева",
        "libra": "Весы",
        "scorpio": "Скорпион",
        "sagittarius": "Стрелец",
        "error": "error"
    }
    return sign_map.get(get_zodiac_sign(day, month), "Неизвестный знак")


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
        "sagittarius": "Стрелецов",
        "error": "error"
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


def d_in_y(day: int, month: int):
    if (
            month == 1 or month == 3 or month == 5 or month == 7 or month == 8 or month == 10 or month == 12) and 1 <= day <= 31:
        return True
    elif (month == 4 or month == 6 or month == 9 or month == 11) and 1 <= day <= 30:
        return True
    elif month == 2 and 1 <= day <= 28:
        return True
    else:
        return False


# Функция определения знака зодиака
def get_zodiac_sign(day: int, month: int) -> str:
    if (month == 12 and day >= 22) or (month == 1 and day <= 19):
        return "capricorn"  # Козерог
    elif (month == 1 and day >= 20) or (month == 2 and day <= 19):
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
    elif (month == 11 and day >= 23) or (month == 12 and day <= 22):
        return "sagittarius"  # Стрелец
    else:
        return "error"


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


@bot.message_handler(func=lambda message: True)
def handle_message(message):
    global dd, mm, yy
    try:
        user_id = message.chat.id

        if user_id not in user_placement:
            user_placement[user_id] = user_start

        if message.text == '⬅️ Назад':
            back(message)
            return

        if message.text in ["🔮 Обычный гороскоп", "💼 Рабочий гороскоп",
                            "❤️ Любовный гороскоп", "🐺 Тотемное животное",
                            "🧮 Ангельское число", "👩‍❤️‍👨 Совместимость"]:
            handle_choice(message)
            return

        if message.text in ['Совместимость по именам', 'Совместимость по знакам зодиака']:
            sov(message)
            return

        if '.' in message.text:
            parts = message.text.strip().split('.')
            if len(parts) == 3:
                day, month, year = map(int, parts)
                if 1 <= day <= 31 and 1 <= month <= 12 and 1900 <= year <= datetime.datetime.now().year:
                    sign = get_zodiac_sign_display(day, month)
                    if sign != "error":
                        dd, mm, yy = day, month, year
                        bot.send_message(message.chat.id,
                                         f"✨ Ваш знак зодиака: {sign}\nВыберите действие:",
                                         reply_markup=keyboard)
                    else:
                        bot.send_message(message.chat.id, "❌ Некорректная дата рождения")
                else:
                    bot.send_message(message.chat.id,
                                     "❌ Некорректная дата. Используйте формат ДД.ММ.ГГГГ(например: 15.09.2006)")
                return
        else:
            bot.send_message(message.chat.id, "❌ Неверный формат. Используйте формат ДД.ММ.ГГГГ(например: 15.09.2006)")

    except Exception as e:
        print(f"Ошибка в handle_message: {e}")
        bot.send_message(message.chat.id, "❌ Ошибка обработки запроса")


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


def handle_choice(message):
    global dd, mm
    user_id = message.chat.id
    choice = message.text

    if choice == "👩‍❤️‍👨 Совместимость":
        bot.send_message(message.chat.id, 'Какую совместимость вы хотите узнать?',
                         reply_markup=keyboard_sov)
        user_placement[user_id] = user_sov_choice
        return

    if choice == "❤️ Любовный гороскоп":
        if dd == 0 or mm == 0:
            bot.send_message(message.chat.id, "❌ Сначала укажите вашу дату рождения")
            return

        sign = get_zodiac_sign(dd, mm)
        horoscope_text = get_love_horoscope(sign)
        bot.send_message(message.chat.id, horoscope_text)
        return

    if choice == "💼 Рабочий гороскоп":
        if dd == 0 or mm == 0:
            bot.send_message(message.chat.id, "❌ Сначала укажите вашу дату рождения")
            return

        sign = get_zodiac_sign(dd, mm)
        horoscope_text = get_work_horoscope(sign)
        bot.send_message(message.chat.id, horoscope_text)
        return

    if choice == "🔮 Обычный гороскоп":
        if dd == 0 or mm == 0:
            bot.send_message(message.chat.id, "❌ Сначала укажите вашу дату рождения")
            return

        sign = get_zodiac_sign(dd, mm)
        horoscope_text = get_horoscope(sign, choice)
        bot.send_message(message.chat.id, horoscope_text)
        return

    if choice == "🐺 Тотемное животное":
        if dd > 0 and mm > 0:
            description, image_url = get_totem_info(dd, mm)
            bot.send_message(message.chat.id, description)
            if image_url:
                bot.send_photo(message.chat.id, image_url)
        else:
            bot.send_message(message.chat.id, "❗️ Сначала введите дату рождения.(например: 15.09.2006)")
        return

    if choice == "🧮 Ангельское число":
        if dd > 0 and mm > 0 and yy > 0:
            result = get_angel_number_text(dd, mm, yy)
            bot.send_message(message.chat.id, f"🔢 Ваше ангельское число: {result}")
        else:
            bot.send_message(message.chat.id,
                             "❗️ Сначала введите дату рождения в формате ДД.ММ.ГГГГ(например: 15.09.2006)")
        return
    # Обработка других вариантов
    response = "🔮 Информация временно недоступна"
    bot.send_message(message.chat.id, response)


def sov(message):
    user_id = message.chat.id
    choice = message.text

    if message.text in ['Совместимость по именам']:
        bot.send_message(message.chat.id, 'Напишите первое имя')
        bot.register_next_step_handler(message, sov_name1)
        return
    if message.text in ['Совместимость по знакам зодиака']:
        bot.send_message(message.chat.id, 'Напишите дату рождения мальчика в формате ДД.ММ (например: 15.09)')
        bot.register_next_step_handler(message, sov_signs_b)
        return


def sov_name1(message):
    chat_id = message.chat.id
    if message.text == '⬅️ Назад':
        back(message)
        return
    user_names[chat_id] = {'name1': message.text}
    bot.send_message(chat_id, 'Напишите второе имя')
    bot.register_next_step_handler(message, sov_name2)


def sov_name2(message):
    chat_id = message.chat.id
    if message.text == '⬅️ Назад':
        back(message)
        return
    user_names[chat_id]['name2'] = message.text

    name1 = user_names[chat_id]['name1']
    name2 = user_names[chat_id]['name2']
    sov_names(name1, name2, message)
    del user_names[chat_id]


def calculate_name(name):
    alphabet = "абвгдеёжзийклмнопрстуфхцчшщъыьэюяabcdefghijklmnopqrstuvwxyz"
    alp_values = {letter: i + 1 for i, letter in enumerate(alphabet)}
    name = name.lower()
    total_sum = sum(alp_values.get(char, 0) for char in name)
    while total_sum > 9:
        digits_sum = sum(int(digit) for digit in str(total_sum))
        total_sum = digits_sum
    return total_sum


def sov_names(name1, name2, message):
    num1 = calculate_name(name1)
    num2 = calculate_name(name2)
    sov_num = num1 + num2
    while sov_num > 9:
        digits_sum = sum(int(digit) for digit in str(sov_num))
        sov_num = digits_sum

    names_text(sov_num, message)


def names_text(sov_num, message):
    if sov_num == 1:
        response = 'Союз лидеров, где каждый стремится отстаивать свою точку зрения. Учитесь искать компромисс'
    elif sov_num == 2:
        response = ('Мир и согласие, пара будет решать проблемы сообща, а препятствия преодолевать с '
                    'помощью обсуждения. Такие отношения строятся на дружбе и уважении')
    elif sov_num == 3:
        response = ('Гармоничные отношения, в любой ситуации партнёры смогут хорошо понять друг друга. Союз может быть '
                    'неустойчивым, если одна сторона возьмёт верх и будет главенствовать')
    elif sov_num == 4:
        response = ('Спокойная и ответственная пара. В этих отношениях нечасто бывают ссоры, но'
                    ' и проявления чувств выражены не слишком ярко')
    elif sov_num == 5:
        response = ('В этой паре отношения яркие и страстные. С одной стороны, это хороший союз двух влюблённых '
                    'и семейных людей, с другой для деловых партнёров такое сочетание не самое благоприятное.')
    elif sov_num == 6:
        response = ('Доверительные, основанные на любви, доверии и взаимопонимании. Эти отношения могут оставаться '
                    'крепкими на протяжении долгих лет, но партнеры должны быть парой, и надолго не разлучаться')
    elif sov_num == 7:
        response = ('Один из партнёров сильно выделяется. Хороший союз возможен при условии, что «ведущий» '
                    'поддерживает «ведомого». А тот, в свою очередь, уважает и ценит его поддержку.')
    elif sov_num == 8:
        response = ('Партнёры могут несколько раз встречаться и расходиться. Но их притягивает друг к другу какой-то'
                    ' силой. Они не могут друг без друга, в то же время каждому нужно место уединения. Супруги могут'
                    ' совершать ошибки, но не делают выводов и снова наступают на те же грабли.')
    else:
        response = ('Множество общих интересов, идей, взглядов на мир. Однако, один из супругов может перетягивать '
                    'одеяло на себя и стать лидером. Не стоит соперничать, лучше поддержать партнера, а самому'
                    ' развиваться в другой сфере')
    bot.send_message(message.chat.id, response)


def sov_signs_b(message):
    if message.text == "⬅️ Назад":
        back(message)
        return
    try:
        day, month = map(int, message.text.split('.'))
        if 1 <= day <= 31 and 1 <= month <= 12:
            sign_b = get_zodiac_sign_display_from_eng(get_zodiac_sign(day, month))
            if sign_b != "error":
                chat_id = message.chat.id  # ID чата
                bg_signs[chat_id] = {'sign_b': sign_b}
                bot.send_message(chat_id, f"✨Знак зодиака мальчика: {sign_b}")
                bot.send_message(chat_id, 'Напишите дату рождения девочки в формате ДД.ММ (например: 15.09)')
                bot.register_next_step_handler(message, sov_signs_g)
            else:
                bot.send_message(message.chat.id, "❌ Некорректная дата. Попробуйте снова.")
        else:
            bot.send_message(message.chat.id, "❌ Некорректная дата. Попробуйте снова.")
    except ValueError:
        bot.send_message(message.chat.id, "❌ Некорректный формат даты. Попробуйте снова (ДД.ММ).")
    except Exception as e:
        print(f"Ошибка в sov_signs_b: {e}")
        bot.send_message(message.chat.id, "❌ Произошла ошибка при обработке даты. Попробуйте снова.")


def sov_signs_res(filename, sign_b, sign_g, chat_id):
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            data = json.load(f)
            try:
                compatibility = data[sign_b][sign_g]
                bot.send_message(chat_id, f"Совместимость между {sign_b} и {sign_g}:\n\n{compatibility}")
            except KeyError:
                bot.send_message(chat_id, f"❌ Информация о совместимости между {sign_b} и {sign_g} не найдена.")
    except FileNotFoundError:
        bot.send_message(chat_id, "❌ Файл с данными о совместимости не найден.")
        print(f"Ошибка: Файл {filename} не найден.")
    except json.JSONDecodeError:
        bot.send_message(chat_id, "❌ Ошибка в формате файла с данными о совместимости.")
        print(f"Ошибка: Некорректный JSON формат в файле {filename}.")
    except Exception as e:
        bot.send_message(chat_id, "❌ Произошла ошибка при обработке совместимости. Попробуйте позже.")
        print(f"Ошибка в sov_signs_res: {e}")


def sov_signs_g(message):
    if message.text == "⬅️ Назад":
        back(message)
        return
    day, month = map(int, message.text.split('.'))
    if 1 <= day <= 31 and 1 <= month <= 12:
        sign_g = get_zodiac_sign_display_from_eng(get_zodiac_sign(day, month))
        chat_id = message.chat.id
        sign_b = bg_signs[chat_id]['sign_b']
        bot.send_message(chat_id, f"✨Знак зодиака девочки: {sign_g}")
        sov_signs_res('sov_znaki.json', sign_b, sign_g, chat_id)
        del bg_signs[chat_id]
    else:
        bot.send_message(message.chat.id, "❌ Некорректная дата. Попробуйте снова.")


if __name__ == '__main__':
    print("Бот запущен...")
    try:
        bot.infinity_polling()
    except KeyboardInterrupt:
        scheduler.shutdown()
