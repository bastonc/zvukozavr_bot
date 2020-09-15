from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import ReplyKeyboardRemove, \
    ReplyKeyboardMarkup, KeyboardButton, \
    InlineKeyboardMarkup, InlineKeyboardButton
from datetime import datetime, time, date
import sqlite3
import random

db_file = "zvukozavr.db"
answers = [
    '⚠ Вы отправили голосовое сообщение! ⚠\nНа первый раз предупреждаем!\nНе используйте Voice-сообщения в этом чате',
    '🐓 Вижу с первого раза не понятно... 🐓\nГолосовые сообщения - запрещены!',
    '⛷ Опять ты со своим Войсами. ⛷\nЯ тебя запомнил!',
    '🧘 Войсо-рецедивист!!!\n 🧘 Помни грешник - кара Админа может настигнуть тебя!\nVoice-сообщения запрещены!',
    '🚷 Все голосовые сообщения напрямую отправялются в силовые структуры!\nТы на карандаше у спецслужб! 🚷']


with open("settings.cfg", "r") as f:
    strings = f.readlines()

setting_dict = {}
if strings != []:
    for string in strings:
        if string !='' and string[0] != "#":
            split_string = string.split("=")

            setting_dict.update({split_string[0].strip(): split_string[1].strip()})
bot_token = setting_dict['token']
try:
    bot = Bot(token=bot_token)
    dp = Dispatcher(bot)
except:
    print("Не могу подключиться к серверу")

try:
    conn = sqlite3.connect("file:" + db_file + "?mode=rw", uri=True)
    cursor = conn.cursor()

    print("Open DB file")
except Exception:
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
    cursor.execute(
        "CREATE TABLE zvukozavr (id INTEGER PRIMARY KEY AUTOINCREMENT, tgm_user_id CHAR(50) , tgm_name CHAR(350), tgm_chat_id CHAR(50), score INT, timestamp DATETIME)")
    cursor.execute(
        "CREATE TABLE messages (id INTEGER PRIMARY KEY AUTOINCREMENT, message CHAR(500) , status CHAR(10), tgm_chat_id CHAR(150), timestamp DATETIME)")
    cursor.execute(
        "CREATE TABLE admins (id INTEGER PRIMARY KEY AUTOINCREMENT, tgm_user_name CHAR(500) , tgm_user_id CHAR(150), tgm_chat_id CHAR(150), status CHAR(10), timestamp DATETIME)")

    conn.commit()
    print("Create DB file")

@dp.message_handler(commands="gui")
async def gui(message: types.Message):
    adm_user = privelege_user(message)
    if adm_user !=[]:
        if str(message.chat.id) == str(adm_user[2]):
            cursor.execute("SELECT * FROM messages WHERE tgm_chat_id=? AND status='N'",
                           [adm_user[3]])
            message_len = len(cursor.fetchall())
            cursor.execute("""
                        SELECT * FROM admins WHERE tgm_chat_id=? AND status='N'""",
                           [adm_user[3]])
            admins_len = len(cursor.fetchall())

            btn_admin_message = InlineKeyboardButton("Предложка ответов ("+str(message_len)+")", callback_data='Test Inline')
            btn_admin_message_all = InlineKeyboardButton("Все ответы", callback_data='Test Inline')
            btn_root_admin = InlineKeyboardButton("Предложка Админов ("+str(admins_len)+")", callback_data='Test Inline')
            btn_admin_all = InlineKeyboardButton("Все Админы", callback_data='Test Inline')
            btn_clearAll = InlineKeyboardButton("Удалить всех грешников", callback_data='Test Inline')
            btn_clear_admin = InlineKeyboardButton("Удалить всех админов", callback_data='Test Inline')
            keyboard = InlineKeyboardMarkup().row(btn_admin_message, btn_admin_message_all).row(btn_root_admin,
                                                  btn_admin_all).row(btn_clearAll, btn_clear_admin)
            await message.reply("Привет "+message.from_user.username, reply_markup=keyboard)

        else:
            await message.reply("Для этой комманды перейдите в личный чат с ботом")

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

    cursor.execute(
        "SELECT * FROM zvukozavr WHERE tgm_user_id=? AND tgm_chat_id=?",
        [message.from_user.id, message.chat.id])
    conn.commit()
    answer = cursor.fetchall()
    #print("find in base", "len:", answer)
    if answer != []:
        if answer[0][4] == 1:
            bad_string_answer = answers[1]
        if answer[0][4] > 1:
            cursor.execute(
                "SELECT * FROM messages WHERE tgm_chat_id=? AND status='Y' ",
                [message.chat.id])
            conn.commit()
            messages_from_base = cursor.fetchall()
            if messages_from_base !=[]:
                index_random = random.randint(0, len(messages_from_base)-1)
                bad_string_answer = messages_from_base[index_random][1]
            else:
                bad_string_answer = "Нельзя использовать Войсы"

        cursor.execute(
            "UPDATE zvukozavr SET score=?, timestamp=? WHERE tgm_user_id=? AND tgm_chat_id=?",
            [int(answer[0][4]) + 1, date.today(), str(message.from_user.id), str(message.chat.id)])
        conn.commit()
    else:
        cursor.execute("INSERT INTO zvukozavr (tgm_user_id, tgm_name, tgm_chat_id, score, timestamp) VALUES(?,?,?,?,?)",
            [str(message.from_user.id), str(message.from_user.first_name), str(message.chat.id), 1, date.today()])
        conn.commit()
        bad_string_answer = answers[0]

    cursor.execute(
        "SELECT * FROM zvukozavr ")
    conn.commit()
    #print("In Base: ", cursor.fetchall())
    await message.reply(bad_string_answer)

@dp.message_handler(commands="addMessage")
async def addMessage(message: types.Message):
    '''
    I don't know WTF function
    :param message:
    :return:
    '''
    full_text = message.text

    text = full_text[12:]
    #print(text)
    if len(text) < 500 and text != '':
        cursor.execute(
            "INSERT INTO messages (message, status, tgm_chat_id, timestamp) VALUES (?,?,?,?)",
            [str(text), "N", message.chat.id, date.today()])
        conn.commit()
        answer_string = "Спасибо\nВаше сообщение отправлено на модерацию"
    else:
        answer_string = "Сообщение не должно быть пустым и не должно превышать 500 символов.\nВаше сообщение: " + str(len(text))+ " символов"

    await message.answer(answer_string)

@dp.message_handler(commands="сlearAll")
async def ClearAll(message: types.Message):
    adm_user = privelege_user(message)
    if adm_user != []:
        if str(message.chat.id) == str(adm_user[2]):
            cursor.execute(
                "DELETE FROM zvukozavr WHERE tgm_chat_id=?",
                [adm_user[3]])
            conn.commit()
            await message.answer("База пользователей удалена")
        else:
            await message.reply("Для этой комманды перейдите в личный чат с ботом")

@dp.message_handler(commands="allAdmins")
async def allAdmins(message: types.Message):
    """
    adm_user[2] - id tgm_user_id (Admin  user)
    adm_user[3] - id tgm_chat_id
    :param message:
    :return:
    """

    adm_user = privelege_user(message)
    if adm_user != []:

        if str(message.chat.id) == str(adm_user[2]):
            #print(adm_user[3])
            cursor.execute(
                "SELECT * FROM admins WHERE tgm_chat_id=?",
                [str(adm_user[3])])
            conn.commit()
            all_admins = cursor.fetchall()
            for i in range(len(all_admins)):

                btn_del = InlineKeyboardButton('Удалить',
                                               callback_data="FDA|" + str(all_admins[i][2])+'|'+str(all_admins[i][3]))
                inline_kb_full = InlineKeyboardMarkup()
                inline_kb_full.row(btn_del)
                await message.answer(
                    "["+all_admins[i][1]+"](tg://user?="+all_admins[i][3]+")",
                    reply_markup=inline_kb_full,
                    parse_mode='markdown'
                )
        else:
            await message.reply("Для этой комманды перейдите в личный чат с ботом")

@dp.message_handler(commands="adminMessage")
async def adminMessage(message: types.Message):
    '''
    I don't know WTF function
    :param message:
    :return:
    '''
    adm_user = privelege_user(message)

    if  adm_user != []:
        if str(message.chat.id) == str(adm_user[2]):
            cursor.execute(
                "SELECT * FROM messages WHERE tgm_chat_id=? AND status='N'",
                [adm_user[3]])
            conn.commit()
            answer_adm = cursor.fetchall()

            if answer_adm != []:
                for i in range(len(answer_adm)):
                    btn_yes = InlineKeyboardButton('Одобрить',  callback_data="Y|"+str(answer_adm[i][0]))
                    btn_no = InlineKeyboardButton('Удалить', callback_data="N|"+str(answer_adm[i][0]))
                    inline_kb_full = InlineKeyboardMarkup(row_width=2)
                    inline_kb_full.row(btn_yes, btn_no)
                    await message.answer(answer_adm[i][1], reply_markup=inline_kb_full)


            else:
                await message.answer("Новых сообщений в предложку нет")
        else:
            await message.reply("Для этой комманды перейдите в ЛС бота")
    out_base("messages")

@dp.message_handler(commands="adminMessageAll")
async def adminMessageAll(message: types.Message):
    '''
    Admin messages
    :param message:
    :return:
    '''

    adm_user = privelege_user(message)
    if adm_user != []:
        if str(message.chat.id) == str(adm_user[2]):
            cursor.execute(
                "SELECT * FROM messages WHERE tgm_chat_id=?",
                [adm_user[3]])
            conn.commit()
            answer_adm = cursor.fetchall()
            if answer_adm != []:
                for i in range(len(answer_adm)):
                    #btn_yes = InlineKeyboardButton('Одобрить',  callback_data="Y|"+str(answer_adm[i][0]))
                    btn_no = InlineKeyboardButton('Удалить', callback_data="D|"+str(answer_adm[i][0]))
                    inline_kb_full = InlineKeyboardMarkup(row_width=2)
                    inline_kb_full.row(btn_no)
                    await message.answer(answer_adm[i][1], reply_markup=inline_kb_full)


            else:
                await message.answer("Новых сообщений в предложку нет")
        else:
            await message.reply("Для этой комманды перейдите в ЛС бота")

@dp.message_handler(commands="addAdmin")
async def addAdmin(message: types.Message):
    cursor.execute("SELECT * FROM admins WHERE tgm_chat_id=?", [message.chat.id])
    conn.commit()
    answer = cursor.fetchall()
    if answer == []:  # if not root in this chat

        cursor.execute("""INSERT INTO admins(tgm_user_name, tgm_user_id, tgm_chat_id, status, timestamp) 
                          VALUES(?,?,?,?,?)""",[message.from_user.username, message.from_user.id,
                                              message.chat.id, "ROOT", date.today()])
        await message.answer("Zvukozavr\nБот который ругает тех кто присылает войсы\n"
                             "Вы ROOT!")

    else: # add in condidate list (need moderate by ROOT)
        cursor.execute("SELECT * FROM admins WHERE tgm_chat_id=? AND tgm_user_id=?",
                       [message.chat.id, message.from_user.id])
        conn.commit()
        admins_records = cursor.fetchall()
        if admins_records == []:
            cursor.execute("""INSERT INTO admins(tgm_user_name, tgm_user_id, tgm_chat_id, status, timestamp) 
                                      VALUES(?,?,?,?,?)""", [message.from_user.username, message.from_user.id,
                                                             message.chat.id, "N", date.today()])
            await message.answer("Ваша заявка на Админа Звукозавра принята")
        else:
            await message.answer("Вы уже подавали заявку на Админа Звукозавра")

    out_base("admins")

@dp.message_handler(commands="rootAdmins")
async def rootAdmins(message: types.Message):
    adm_user = privelege_user(message)
    if adm_user != []:
        if str(message.chat.id) == str(adm_user[2]):
            tgm_chat_id_user=adm_user[3]
            cursor.execute("SELECT * FROM admins WHERE status='N' AND tgm_chat_id=?",
                            [tgm_chat_id_user])
            conn.commit()
            candidate = cursor.fetchall()
            if candidate != []:
                #print("Candidate found: ", candidate)
                for i in range(len(candidate)):
                    candidate_string = "[" + candidate[i][1] + "](tg://user?id='" + candidate[i][2] + "') кандидат в Админы"
                    btn_yes = InlineKeyboardButton("Одобрить",
                                                   callback_data='YA|'+str(candidate[i][2]+'|'+ candidate[i][3]))
                    btn_no = InlineKeyboardButton("Отклонить",
                                                   callback_data='YA|' + str(candidate[i][2] + '|' + candidate[i][3]))

                    kb_lay = InlineKeyboardMarkup(row_width=2)
                    kb_lay.row(btn_yes, btn_no)
                    await message.answer(candidate_string, reply_markup=kb_lay, parse_mode="markdown")
            else:
                await message.answer("Новых заявок на Админа нет", parse_mode="markdown")
        else:
            await message.reply("Для этой комманды перейдите в ЛС бота")

    else:
        await message.answer("Доступ запрещен")

@dp.callback_query_handler(lambda c: True)
async def process_callback(call: types.CallbackQuery):
    data = call.data.split("|")
    if data[0] == 'Y':
        cursor.execute(
            "UPDATE messages SET status='Y' WHERE id=? ",
            [data[1]])
        conn.commit()

        await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text="Одобрено")

    if data[0] == 'N' or data[0] == 'D':
        cursor.execute(
            "DELETE FROM messages WHERE id=?", [data[1]])
        conn.commit()
        await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text="Удалено")
    if data[0] == 'YA':

        tgm_user_id = data[1]
        tgm_chat_id = data[2]
        print ("tgm_user_id: ", tgm_user_id, "tgm_chat_id: ", tgm_chat_id )
        cursor.execute(
            "UPDATE admins SET status='Y' WHERE tgm_user_id=? AND tgm_chat_id=?", [tgm_user_id, tgm_chat_id])
        conn.commit()
        cursor.execute(
            "SELECT * FROM admins WHERE tgm_user_id=? AND tgm_chat_id=?", [tgm_user_id, tgm_chat_id])
        conn.commit()
        answer = cursor.fetchall()
        await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=answer[0][1] + " Одобрен")

    if data[0] == 'DA':

        tgm_user_id = data[1]
        tgm_chat_id = data[2]
        print ("tgm_user_id: ", tgm_user_id, "tgm_chat_id: ", tgm_chat_id )
        cursor.execute(
            "DELETE FROM admins WHERE tgm_user_id=? AND tgm_chat_id=?", [tgm_user_id, tgm_chat_id])
        conn.commit()
        await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                    text="Удален")
    if data[0] == 'FDA':
        #id_all = call.data.split("|")
        tgm_user_id = data[1]
        tgm_chat_id = data[2]
        cursor.execute(
            "DELETE FROM admins WHERE tgm_user_id=? AND tgm_chat_id=?", [tgm_user_id, tgm_chat_id])
        conn.commit()
        await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                    text="Удален")

#### This development functions
@dp.message_handler(commands="clearAdmin")
async def clearAdmin(message: types.Message):
    if setting_dict['mode'] == "Develop":
        del_from_base('admins')
    else:
        await message.answer("Production mode")

@dp.message_handler(commands="addVadmin")
async def addVadmin(message: types.Message):
    if setting_dict['mode'] == "Develop":
        cursor.execute("""INSERT INTO admins(tgm_user_name, tgm_user_id, tgm_chat_id, status, timestamp) 
                                  VALUES(?,?,?,?,?)""", ["Test  user", "0000000001", '270122177', 'N', date.today()])
        conn.commit()
        out_base("admins")
        await message.answer("Add virtualAdmin ")
    else:
        await message.answer("Production mode")

def out_base (name_base):

    if setting_dict['mode'] == "Develop":
        sql_query = "SELECT * FROM " + name_base
        cursor.execute(sql_query)
        conn.commit()
        print(cursor.fetchall())

def del_from_base (name_base):
    if setting_dict['mode'] == "Develop":
        sql_query = "DELETE FROM " + name_base
        cursor.execute(sql_query)
        conn.commit()
        print(cursor.fetchall())

####

@dp.message_handler(commands="pozorToday")
async def pozor_func(message: types.Message):
    '''This fnction reply on command pozorToday
    Used select with timestamp on today
    '''
    full_string_answer = "На " + str(date.today()) + pozor_engine(message.chat.id, mode='today')
    await message.answer(full_string_answer, parse_mode="markdown")

@dp.message_handler(commands="pozorAll")
async def pozor_func(message: types.Message):
    '''This fnction reply on command pozorAll
    Used select ALL records from base
    '''

    full_string_answer = "Общий рейтинг" + pozor_engine(message.chat.id)
    await message.answer(full_string_answer, parse_mode="markdown")

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
            "SELECT * FROM zvukozavr WHERE timestamp=? AND tgm_chat_id=? ORDER BY score DESC ", [date.today(), chat_id])
        conn.commit()
    elif mode == 'all':
        cursor.execute(
            "SELECT * FROM zvukozavr WHERE tgm_chat_id=? ORDER BY score DESC ", [chat_id])
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

    # user = f"[{message.from_user.first_name}]({f'tg://user?id={message.from_user.id}'})"
    if answer != []:
        string_out = ''
        for i in range(len(answer)):
            # print(answer[i][0], answer[i][1], answer[i][2])
            if i == 0:
                string_out += "\n     🥇 [" + answer[i][2] + "](tg://user?id=" + answer[i][1] + ") войсов - " + str(
                    answer[i][4])
            elif i == 1:
                string_out += "\n     🥈 [" + answer[i][2] + "](tg://user?id=" + answer[i][1] + ") войсов - " + str(
                    answer[i][4])
            elif i == 2:
                string_out += "\n     🥉 [" + answer[i][2] + "](tg://user?id=" + answer[i][1] + ") войсов - " + str(
                    answer[i][4])
            elif i > 2:
                string_out += "\n       ⚧ [" + answer[i][1] + "](tg://user?id=" + answer[i][1] + ") войсов - " + str(
                    answer[i][4])

        reply = "\n 📛 → Доска Voice-грешников ← 📛 \n" + string_out + "\n\n ⚠ Не используй войсы в чате! ⚠"
    else:
        reply = "\nВ этом чате не использовали войсов. \nКрасавчики!\n"
    return reply

def privelege_user (message):
    #### Chek privelegies start #####
    cursor.execute("SELECT * FROM admins WHERE (status='Y' OR status = 'ROOT') AND tgm_user_id=?",
                   [message.from_user.id])
    conn.commit()
    answer = cursor.fetchall()

    if answer != []:
        return answer[0]
    else:
        return answer
    #### Chek privelegies end #####

executor.start_polling(dp)