from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
from aiogram.utils import executor
from aiogram.dispatcher.filters import Text
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
import requests, bs4, sqlite3, getpass, socket, platform, psutil
from uuid import getnode as get_mac
from datetime import datetime

token = '5789451039:AAG9jOP1OBJ4m-CbawOB8yFqm1Anol-DV3A'

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/106.0.0.0 "
                  "Safari/537.36 "
}

math_contact = ['''Мажуга Андрей Михайлович
Телефон:
+7 (495) 531-00-00
27244
Адрес: АУК "Покровский бульвар", Покровский б-р, д. 11, каб. S808
Время консультаций: По договоренности
Начал работать в НИУ ВШЭ в 2018 году.
Научно-педагогический стаж: 1 год 6 месяцев.
''']
programming_contact = ['''Горшков Сергей Сергеевич
Телефон:
28116
Адрес: АУК "Покровский бульвар", Покровский б-р, д. 11, каб. S812
Время работы: По расписанию. 
Расписание: https://www.hse.ru/org/persons/307352167/timetable
Начал работать в НИУ ВШЭ в 2019 году.
''']

bot = Bot(token)
dp = Dispatcher(bot, storage=MemoryStorage())

user_key = InlineKeyboardMarkup(row_width=1)
user_key.add(InlineKeyboardMarkup(text='👤 Администрация 👤', url='https://t.me/chikubrikule322'))
user_key.add(InlineKeyboardMarkup(text='☁️ Погода ☁️', callback_data='weather'))
user_key.add(InlineKeyboardMarkup(text='👩‍🏫 Преподаватели 👩‍🏫', callback_data='teacher'))
user_key.add(InlineKeyboardMarkup(text='👥 Пользователи 👥', callback_data='users'))

user_key.add(InlineKeyboardMarkup(text='🗂 Информация о пк моего создателя 🗂', callback_data='server_info'))

back_menu = InlineKeyboardMarkup(row_width=1)
back_menu.add(InlineKeyboardButton(text='◀️ Назад ◀️', callback_data='back'))

predmet = InlineKeyboardMarkup(row_width=1)
predmet.add(InlineKeyboardMarkup(text='💻 Программирование 💻', callback_data='pred_programming'))
predmet.add(InlineKeyboardMarkup(text='🧮 Дискретная математика 🧮', callback_data='pred_math'))
predmet.add(InlineKeyboardMarkup(text='◀️ Назад ◀️', callback_data='back'))

base = sqlite3.connect('users.db', check_same_thread=False)
cur = base.cursor()

base.execute('CREATE TABLE IF NOT EXISTS {}(id PRIMARY KEY, username TEXT, full_name TEXT)'.format('user'))
base.commit()


class City(StatesGroup):
    city = State()


@dp.message_handler(commands='start')
async def start(message: types.Message):
    full_name = message.from_user.full_name
    username = message.from_user.username
    try:
        cur.execute('INSERT INTO user VALUES(?, ?, ?)', (f'{message.from_user.id}', f'{username}', f'{full_name}'))
        base.commit()
        await bot.send_message(message.from_user.id, 'Привет, я бот студента ВШЭ, давай поможем друг другу.',
                               reply_markup=user_key)

    except Exception as e:

        await bot.send_message(message.from_user.id, 'Привет, я бот студента ВШЭ, давай поможем друг другу.',
                               reply_markup=user_key)


@dp.callback_query_handler(text='server_info')
async def server_infprmation(message: types.Message):
    await bot.delete_message(chat_id=message.from_user.id, message_id=message.message.message_id)

    name = getpass.getuser()
    ip = socket.gethostbyname(socket.getfqdn())
    mac = get_mac()
    ost = platform.uname()
    zone = psutil.boot_time()
    time = datetime.fromtimestamp(zone)
    text = f'''
🗂 Информация о системе 🗂

Имя пользователя: {name}
IP адрес системы: {ip}
MAC адрес системы: {mac}
Название операционной системы: {ost[0]}
Время установленное в системе: {time}
'''
    await bot.send_message(message.from_user.id, text, reply_markup=back_menu)


@dp.callback_query_handler(text='users')
async def users_db(callback: types.CallbackQuery):
    await bot.delete_message(chat_id=callback.from_user.id, message_id=callback.message.message_id)

    id_user = cur.execute('SELECT id FROM user').fetchall()
    username = cur.execute('SELECT username FROM user').fetchall()
    full_name = cur.execute('SELECT full_name FROM user').fetchall()

    n = len(id_user)

    num = 0

    for i in range(n):
        id = id_user[num][0]
        us = username[num][0]
        name = full_name[num][0]

        await bot.send_message(callback.from_user.id, f'ID: {id}\nUsename: @{us}\nFull Name: {name}')

        num += 1

    await bot.send_message(callback.from_user.id, 'Что бы вернуться в главное меню воспользуйтесь кнопкой ниже',
                           reply_markup=back_menu)


@dp.callback_query_handler(text='backup')
async def backup_save(message: types.Message):
    await bot.delete_message(chat_id=message.from_user.id, message_id=message.message.message_id)

    await bot.send_document(message.from_user.id, open("users.db", "rb"))

    await bot.send_message(message.from_user.id, 'Вы находитесь в главном меню', reply_markup=user_key)


@dp.callback_query_handler(text='teacher')
async def teacher_hand(message: types.Message):
    await bot.delete_message(chat_id=message.from_user.id, message_id=message.message.message_id)

    await bot.send_message(message.from_user.id, 'Выберите предмет и бот выдаст Вам контакты преподавателя',
                           reply_markup=predmet)


@dp.callback_query_handler(Text(startswith='pred_'))
async def predmet_hand(callback: types.CallbackQuery):
    await bot.delete_message(chat_id=callback.from_user.id, message_id=callback.message.message_id)

    msg = callback.data
    msg = msg.replace('pred_', '')

    if msg == 'math':

        await bot.send_message(callback.from_user.id,
                               f'Контакты преподавателя по дискретной математике:\n{math_contact[0]}',
                               reply_markup=back_menu)

    else:

        await bot.send_message(callback.from_user.id,
                               f'Контакты преподавателя по программированию:\n{programming_contact[0]}',
                               reply_markup=back_menu)


@dp.callback_query_handler(text='back')
async def back_hand(message: types.Message):
    await bot.delete_message(chat_id=message.from_user.id, message_id=message.message.message_id)

    await bot.send_message(message.from_user.id, 'Вы находитесь в главном меню', reply_markup=user_key)


@dp.callback_query_handler(text='weather')
async def pasrer(message: types.Message):
    await bot.delete_message(chat_id=message.from_user.id, message_id=message.message.message_id)

    await bot.send_message(message.from_user.id, 'Введите город')

    await City.city.set()


@dp.message_handler(state=City.city)
async def ref_code(message: types.Message, state: FSMContext):
    await bot.delete_message(chat_id=message.from_user.id, message_id=message.message_id)
    await bot.delete_message(chat_id=message.from_user.id, message_id=message.message_id - 1)

    try:
        wether = requests.get(f'https://www.google.com/search?q=погода+{message.text}', headers=headers)

        wether_response = bs4.BeautifulSoup(wether.text, "html.parser")
        we = wether_response.find("span", id='wob_tm')
        pogoda = wether_response.find("span", id="wob_dc")

        await bot.send_message(message.from_user.id, f'Погода в городе {message.text} {we.text} °C\n{pogoda.text}',
                               reply_markup=back_menu)

        await state.finish()

    except:

        await bot.send_message(message.from_user.id, f'Кажется, такого города ещё нет, но ты можешь его основать.',
                               reply_markup=back_menu)


executor.start_polling(dp, skip_updates=True)
