import telebot
from telebot.types import ReplyKeyboardMarkup
import datetime

bot = telebot.TeleBot("7750454802:AAFGWBfByWs7E6_2DzpbXWs2FbCof2NL1-I")
dd = 0
mm = 0
yy = 0

# клавиатура
keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
keyboard.row("🔮 Обычный гороскоп", "💼 Рабочий гороскоп")
keyboard.row("❤️ Любовный гороскоп", "🐺 Тотемное животное")
keyboard.row("🧮 Ангельское число", "👩‍❤️‍👨 Совместимость")


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
    if (month == 12 and day >= 22) or (month == 1 and day <= 20):
        return "Козерог"
    elif (month == 1 and day >= 21) or (month == 2 and day <= 18):
        return "Водолей"
    elif (month == 2 and day >= 19) or (month == 3 and day <= 20):
        return "Рыбы"
    elif (month == 3 and day >= 21) or (month == 4 and day <= 20):
        return "Овен"
    elif (month == 4 and day >= 21) or (month == 5 and day <= 21):
        return "Телец"
    elif (month == 5 and day >= 22) or (month == 6 and day <= 21):
        return "Близнецы"
    elif (month == 6 and day >= 22) or (month == 7 and day <= 22):
        return "Рак"
    elif (month == 7 and day >= 23) or (month == 8 and day <= 23):
        return "Лев"
    elif (month == 8 and day >= 24) or (month == 9 and day <= 23):
        return "Дева"
    elif (month == 9 and day >= 24) or (month == 10 and day <= 23):
        return "Весы"
    elif (month == 10 and day >= 24) or (month == 11 and day <= 22):
        return "Скорпион"
    elif (month == 11 and day >= 23) or (month == 12 and day <= 22):
        return "sagittarius"  # Стрелец
    else:
        return "error"


@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.send_message(message.chat.id,
                     "👋 Привет! Я бот-гороскоп. Напиши свою дату рождения в формате ДД.ММ.ГГГГ (например: 14.05.2006)")


@bot.message_handler(func=lambda message: True)
def handle_message(message):
    global dd, mm, yy
    try:
        if message.text in ["🔮 Обычный гороскоп", "💼 Рабочий гороскоп",
                            "❤️ Любовный гороскоп", "🐺 Тотемное животное",
                            "🧮 Ангельское число", "👩‍❤️‍👨 Совместимость"]:
            handle_choice(message)
            return

        if '.' in message.text:
            parts = message.text.strip().split('.')
            if len(parts) == 3:
                day, month, year = map(int, parts)
                if 1 <= day <= 31 and 1 <= month <= 12 and 1900 <= year <= datetime.datetime.now().year:
                    sign = get_zodiac_sign(day, month)
                    if sign != "error":
                        dd, mm, yy = day, month, year
                        bot.send_message(message.chat.id, f"✨ Ваш знак зодиака: {sign}\nВыберите действие:",
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
        bot.send_message(message.chat.id, "❌ Ошибка обработки запроса")
        print(e)


def handle_choice(message):
    choice = message.text
    response = "🔮 Информация временно недоступна"

    if choice == "🐺 Тотемное животное":
        response = "🐺Ваше тотемное животное волк"
    elif "гороскоп" in choice:
        response = "⭐ Сегодня вас ждут приятные сюрпризы!"
    elif choice == "🧮 Ангельское число":
        response = "Ваше ангельское число 444"
    elif choice == "👩‍❤️‍👨 Совместимость":
        response = "❤️‍🔥 Совместимость: 78% с Водолеями, 65% с Тельцами"

    bot.send_message(message.chat.id, response)


if __name__ == '__main__':
    bot.infinity_polling()
