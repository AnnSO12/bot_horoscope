user_placement = {}

user_start = 0
user_sov_choice = 1
user_sov_name1 = 2
user_sov_name2 = 3
user_sov_data1 = 4
user_sov_data2 = 5


def sov(message):
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
            chat_id = message.chat.id  # ID чата
            bg_signs[chat_id] = {'sign_b': sign_b}
            bot.send_message(chat_id, f"✨Знак зодиака мальчика: {sign_b}")
            bot.send_message(chat_id, 'Напишите дату рождения девочки в формате ДД.ММ (например: 15.09)')
            bot.register_next_step_handler(message, sov_signs_g)
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
