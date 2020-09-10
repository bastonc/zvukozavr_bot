from aiogram import Bot, Dispatcher, executor, types
from datetime import datetime, time, date
import sqlite3

db_file = "zvukozavr.db"
answers = ['Вы отправили голосовое сообщение!\nНа первый раз предупреждаем!\nНе используйте Voice-сообщения',
           'Вижу с первого раза не понятно...\nГолосовые сообщения - запрещены!',
           'Опять ты со своим Войсами.\nЯ тебя запомнил!',
           'Оппа, смотрите кто тут у нас тут - рецедивист!!!\n Помни грешник - кара Админа может настигнуть тебя!\nVoice-сообщения запрещены!',
           'Все голосовые сообщения напрямую отправялются в силовые структуры!\nТы на карандаше у спецслужб!\nВойсы запрещены!']
bad_string_answer = " Эй, в этом чате нельзя использовать голосовые сообщения.\nЯ бот и я все записываю.\nКара Админа может настигнуть тебя..."

bot_token = "1308923090:AAEdo9SfitUkcNdWsPZh3Zw8c7-vUjw06hQ"

bot = Bot(token=bot_token)

ideas = []

dp = Dispatcher(bot)

try:
    conn = sqlite3.connect("file:" + db_file + "?mode=rw", uri=True)
    cursor = conn.cursor()
    print("Open DB file")
except Exception:
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
    cursor.execute("CREATE TABLE zvukozavr (tgm_user_id CHAR(50) , tgm_name CHAR(350), score INT, timestamp DATETIME)")
    conn.commit()
    print("Create DB file")


@dp.message_handler(content_types="voice")
async def reply_to_voice(message: types.Message):
    '''
    If sombody sent voice-message - starting this decorator and fixing in SQLite base

    Table in dase have cells:
    tgm_user_id - user id in telegramm
    tgm_name - user name in telegram
    score - how many vice-message sent this user
    timestamp - date entry or update information by this user
    '''
    #    user = f"[{message.from_user.first_name}]({f'tg://user?id={message.from_user.id}'})"
    cursor.execute(
        "SELECT * FROM zvukozavr WHERE tgm_user_id=?",
        [message.from_user.id])
    conn.commit()
    answer = cursor.fetchall()
    print("find in base", "len:", len(answer))
    if answer != []:
        if answer[0][2] == 1:
            bad_string_answer = answers[1]
        if answer[0][2] == 2:
            bad_string_answer = answers[2]
        if answer[0][2] == 3:
            bad_string_answer = answers[3]
        if answer[0][2] > 3:
            bad_string_answer = answers[4]

        cursor.execute(
            "UPDATE zvukozavr SET score=?, timestamp=? WHERE tgm_user_id=?",
            [int(answer[0][2]) + 1, date.today(), str(message.from_user.id)])
        conn.commit()
    else:
        cursor.execute(
            "INSERT INTO zvukozavr(tgm_user_id, tgm_name, score, timestamp) VALUES (?,?,?,?)",
            [str(message.from_user.id), str(message.from_user.first_name),
             int(1), date.today()])
        conn.commit()
        bad_string_answer = answers[0]

    cursor.execute(
        "SELECT * FROM zvukozavr ")
    conn.commit()
    print("In Base: ", cursor.fetchall())
    await message.reply("@" + message.from_user.first_name + " "+bad_string_answer)


@dp.message_handler(commands="add")
async def add(message: types.Message):
    '''
    I don't know WTF function
    :param message:
    :return:
    '''
    text = message.text
    # print(text)
    if text[:22] == "/add@wit_zvukozavr_bot":
        if len(text) != 22:
            text = text[23:]
        else:
            await message.reply("Вы отправили пустое сообщение.")
            return
    elif text[:4] == "/add":
        if len(text) != 4:
            text = text[5:]
        else:
            await message.reply("Вы отправили пустое сообщение.")
            return
    print(text)
    ideas.append(text)
    await message.reply(f"{text} добавлено в предложку.")


@dp.message_handler(commands="pozorToday")
async def pozor_func(message: types.Message):
    '''This fnction reply on command pozorToday
    Used select with timestamp on today
    '''
    await message.reply(pozor_engine(message.chat.id, mode='today'), parse_mode="markdown")


@dp.message_handler(commands="pozorAll")
async def pozor_func(message: types.Message):
    '''This fnction reply on command pozorAll
    Used select ALL records from base
    '''
    await message.reply(pozor_engine(message.chat.id), parse_mode="markdown")


def pozor_engine(chat_id, mode='all'):
    '''
    This function selecting data from base in dependense at mode-selector
    :param chat_id: not used
    :param mode: have two status: 'all'(default) - selecting all record from base; 'today' - selecting by today
    :return: string fo answer to telegramm (var. reply)
    '''
    # global pozor
    if mode == 'today':
        cursor.execute(
            "SELECT * FROM zvukozavr WHERE timestamp=? ORDER BY score DESC ", [date.today()])
        conn.commit()
    elif mode == 'all':
        cursor.execute(
            "SELECT * FROM zvukozavr ORDER BY score DESC ")
        conn.commit()
    answer = cursor.fetchall()
    reply_today = pozor_engine_out(answer)
    return reply_today


def pozor_engine_out(answer):
    '''
    This function formated text for message
    :param answer: list with tulips (from base)
    :return: formated string (var. reply)
    '''
    if answer != []:
        string_out = ''
        for i in range(len(answer)):
            print(answer[i][1], answer[i][2])
            if i == 0:
                string_out += "\n     🥇 " + answer[i][1] + "  штрафных баллов - " + str(answer[i][2])
            elif i == 1:
                string_out += "\n     🥈 " + answer[i][1] + "  штрафных баллов - " + str(answer[i][2])
            elif i == 2:
                string_out += "\n     🥉 " + answer[i][1] + "  штрафных баллов - " + str(answer[i][2])
            elif i > 2:
                string_out += "\n       ⚧ " + answer[i][1] + "  штрафных баллов - " + str(answer[i][2])

        reply = "\n 📛 → Доска Voice-грешников ← 📛 \n" + string_out + "\n\n ⚠ Не используй войсы в чате! ⚠"
    else:
        reply = "\nВ этом чате не использоваи войсов. \nКрасавчики!\n"
    return reply


executor.start_polling(dp)
