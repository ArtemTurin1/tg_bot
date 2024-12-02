import asyncio
from datetime import datetime, timedelta
from gc import callbacks
from app.database.models import User
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardRemove
from aiogram.types import Message, CallbackQuery
from aiogram import Bot, Dispatcher, types, F, Router
from aiogram.filters import CommandStart, Command
import sqlite3
import app.keyboards as kb
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
import app.database.requests as rq
from sqlalchemy import select
from app.database.models import async_session
from app.database.requests import get_liders
from aiogram.types import LabeledPrice, PreCheckoutQuery
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types.message import ContentType
PAYMENT_PROVIDER_TOKEN = "381764678:TEST:101677"
router = Router()
import random

user_messages = {}

conn = sqlite3.connect('db.sqlite3')
cursor = conn.cursor()
bot = Bot(token='7882619849:AAF4WABwNdKvnQ39-mgh0STAztWMyD-VXpM')

supports_canal = '-1002335317649'

def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        return False

class Donat_xzizn(StatesGroup):
    restoration_balls = State()
    restoration_life = State()

class Support(StatesGroup):
    ansversupport = State()
    zacl = State()
class Otvetil(StatesGroup):
    vanswer = State()
    answer = State()
    number = State()

class Register(StatesGroup):
    login = State()
    age = State()
    whu = State()
    number = State()
    tg_id = State()

@router.message(F.photo)
async def photo_handler(message: Message):
    photo_data = message.photo[-1]
    await message.answer(f'{photo_data.file_id}')


@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    await state.clear()
    user_id = message.from_user.id
    if any(user_id in pair for pair in active_games.keys()):
        await message.answer("Вы не можете использовать другие команды во время соревнования.")
        return
    await message.answer(f'Приветствуем вас {message.from_user.full_name}.\nЭтот бот поможет вам подготовиться к экзаменам, или узнать что-то новое. Выберите одну из предложенных команд, для начала использования бота.', reply_markup = kb.main)

@router.message(Command('help'))
async def cmd_start(message: Message):
    user_id = message.from_user.id
    if any(user_id in pair for pair in active_games.keys()):
        await message.answer("Вы не можете использовать другие команды во время соревнования.")
        return
    await message.answer('/start - Перезапуск бота\n'
                         '/register - регестрация')

@router.message(Command('register'))
async def reg(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    if any(user_id in pair for pair in active_games.keys()):
        await message.answer("Вы не можете использовать другие команды во время соревнования.")
        return
    async with async_session() as session:
        user = await session.scalar(select(User).where(User.tg_id == message.from_user.id))
    if not user:
        await state.set_state(Register.login)
        await state.update_data(tg_id = message.from_user.id)
        await message.answer('Придумай себе крутой никнейм! Он появится в таблице лидеров, так что выбирай запоминающийся!',reply_markup=types.ReplyKeyboardRemove())
    else:
        await message.answer('Вы уже зарегистрированы')

@router.message(Register.login)
async def reg_login(message: Message, state: FSMContext):
    async with async_session() as session:
        user_loggin = await session.scalar(select(User).where(User.name == message.text))
    if (len(message.text) > 15) or ('@' in message.text) or ('/' in message.text) or (' ' in message.text):
        await message.answer('Кажется твой никнейм не подходит. Он должен содержать не более 15 символов и не может включать пробелы, а также символы / и @. '
                             'Пожалуйста, попробуй ещё раз.')

    elif user_loggin:
        await message.answer('Пользователь с таким именем уже существует')
    else:
        await state.update_data(login = message.text)
        await state.set_state(Register.age)
        await message.answer('Введи свой возраст! Это поможет нам подобрать для тебя самые подходящие задания и сделать игру еще интереснее!')

@router.message(Register.age)
async def reg_age(message: Message, state: FSMContext):

    if not is_number(message.text):
        await message.answer('Возраст нужно указать цифрами')
    else:
        await state.update_data(age = message.text)
        await state.set_state(Register.whu)
        await message.answer('Выберите кем вы хотите быть на платформе', reply_markup=kb.iam)

@router.message(Register.whu)
async def reg_whu(message: Message, state: FSMContext):
    if message.text != 'Учитель' and message.text != 'Ученик':
        await message.answer('Выберите один из предложенных выриантов')
    else:
        await state.update_data(whu = message.text)
        await state.set_state(Register.number)
        await message.answer('Отправьте ваш номер', reply_markup=kb.get_number)

@router.message(Register.number, F.contact)
async def reg_number(message: Message, state: FSMContext):

    await state.update_data(number=message.contact.phone_number)
    data = await state.get_data()
    global last_message
    last_message = await message.answer(f'Регистрация успешно пройдена. Теперь ты можешь приступить к решению интересных задач.'
                                        f'',reply_markup=kb.main)
    cursor.execute(
        "INSERT INTO users (tg_id, name, age, count_otvet, whuare, number, premium,balls,solved_tasks,balance,count_otvet_x,balls_x,level) VALUES (?,?,?,?, ?, ?, ?, ?,?,?,?,?,?)",
        (data['tg_id'], data['login'], data['age'], 3, data['whu'], data['number'], 0,0,0,0,0,0,0,))
    conn.commit()

    await state.clear()

@router.message(F.text == 'Мой персонаж')
async def lk(message: Message):
    user_id = message.from_user.id
    if any(user_id in pair for pair in active_games.keys()):
        await message.answer("Вы не можете использовать другие команды во время соревнования.")
        return
    await message.delete()
    if user_id in user_messages:
        for msg_id in user_messages[user_id]:
            try:
                await message.bot.delete_message(chat_id=message.chat.id, message_id=msg_id)
            except Exception:
                pass
        user_messages[user_id] = []
    async with async_session() as session:
        user = await session.scalar(select(User).where(User.tg_id == message.from_user.id))
    if not user:
        new_message = await message.answer('Вам нужно пройти регистрацию\n/register')
    else:
        new_message = await message.answer('Вы в личном кабинете', reply_markup=kb.lk)
    user_messages[user_id] = [message.message_id, new_message.message_id]


@router.message(F.text == 'Ежедневные задания')
async def daily_tasks(message: Message):
    user_id = message.from_user.id
    if any(user_id in pair for pair in active_games.keys()):
        await message.answer("Вы не можете использовать другие команды во время соревнования.")
        return
    await message.delete()
    if user_id in user_messages:
        for msg_id in user_messages[user_id]:
            try:
                await message.bot.delete_message(chat_id=message.chat.id, message_id=msg_id)
            except Exception:
                pass
        user_messages[user_id] = []
    async with async_session() as session:
        user = await session.scalar(select(User).where(User.tg_id == message.from_user.id))
    if not user:
        new_message = await message.answer('Вам нужно пройти регистрацию\n/register')
    else:
        new_message = await message.answer('Выберите пункт', reply_markup=kb.zd)
    user_messages[user_id] = [message.message_id, new_message.message_id]


@router.message(F.text == 'Решать задачи')
async def daily_tasks_one(message: Message):
    user_id = message.from_user.id
    if any(user_id in pair for pair in active_games.keys()):
        await message.answer("Вы не можете использовать другие команды во время соревнования.")
        return
    cursor.execute("SELECT count_otvet FROM users WHERE tg_id = ?",
                   (message.from_user.id,))
    result = cursor.fetchone()
    count_otvet = int(result[0])
    conn.commit()
    user_id = message.from_user.id
    await message.delete()
    if user_id in user_messages:
        for msg_id in user_messages[user_id]:
            try:
                await message.bot.delete_message(chat_id=message.chat.id, message_id=msg_id)
            except Exception:
                pass
        user_messages[user_id] = []
    if count_otvet > 0:

        new_message = await message.answer(f'Выбирите предмет', reply_markup=await kb.materialcategorii())
    else:
        new_message = await message.answer(
            'Ваши попытки закончились\nВозвращайтесь завтра, чтобы решать новые задачи\nЧтобы решать задачи без ограничений, вы можете оформить подписку',
            reply_markup=await kb.glavn())
    user_messages[user_id] = [message.message_id, new_message.message_id]


@router.callback_query(F.data.startswith('category_'))
async def maretialcotegori(callback: CallbackQuery):
    await callback.answer(f'Вы выбрали  предмет')
    await bot.edit_message_text(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        text="Выберите номер",
        reply_markup= await kb.materials(callback.data.split('_')[1])
    )





@router.callback_query(F.data.startswith('material_'))
async def materialcotegori(callback: CallbackQuery, state: FSMContext):
    user_id = callback.message.from_user.id
    await callback.message.delete()
    if user_id in user_messages:
        for msg_id in user_messages[user_id]:
            try:
                await callback.message.bot.delete_message(chat_id=callback.message.chat.id, message_id=msg_id)
            except Exception:
                pass
        user_messages[user_id] = []
    material_data = await rq.get_material(callback.data.split('_')[1])
    photo_data = await rq.get_photo(callback.data.split('_')[1])
    photo_data2 = await rq.get_photo(callback.data.split('_')[1])
    await state.update_data(number=material_data.materialcat)
    rand_photo = []
    await callback.answer('Вы выбрали номер')
    await callback.message.answer(f'Вы выбрали: {material_data.name}\n{material_data.description}\nВаше задание:', reply_markup= types.ReplyKeyboardRemove())
    for photo in photo_data:
        rand_photo.append(photo.photo)
    randomphoto = random.choice(rand_photo)
    await callback.message.answer_photo(photo = randomphoto)
    for i in photo_data2:
        if randomphoto == i.photo:
            await state.update_data(vanswer = i.answer)
    await state.set_state(Otvetil.answer)
    await callback.message.answer('Введите ответ:')

@router.message(Otvetil.answer)
async def his_answer(message: Message, state: FSMContext):
    cursor.execute("SELECT count_otvet FROM users WHERE tg_id = ?",
                   (message.from_user.id,))
    result = cursor.fetchone()
    count_otvet = int(result[0])
    conn.commit()
    user_id = message.from_user.id
    await message.delete()
    if user_id in user_messages:
        for msg_id in user_messages[user_id]:
            try:
                await message.bot.delete_message(chat_id=message.chat.id, message_id=msg_id)
            except Exception:
                pass
        user_messages[user_id] = []
    your_balls = 0
    solved_tasks = 0
    await state.update_data(answer=message.text)
    data = await state.get_data()
    if data['vanswer'] == data['answer'] and count_otvet >1:
        new_message = await message.answer('🎉Верный ответ🎉\nВы получаете 1 балл', reply_markup=await kb.materials(data['number']))
        cursor.execute("SELECT balls, solved_tasks FROM users WHERE tg_id = ?",
                       (message.from_user.id,))
        result = cursor.fetchone()
        your_balls = int(result[0])
        solved_tasks = int(result[1])
        your_balls += 1
        solved_tasks += 1
        cursor.execute(
            "UPDATE users SET balls = ? WHERE tg_id = ?",
            (int(your_balls), message.from_user.id,))
        cursor.execute(
            "UPDATE users SET solved_tasks = ? WHERE tg_id = ?",
            (int(solved_tasks), message.from_user.id,))
        user_messages[user_id] = [message.message_id, new_message.message_id]
        conn.commit()


        await state.clear()
    elif data['vanswer'] != data['answer'] and count_otvet > 1:
        cursor.execute("UPDATE users SET count_otvet = count_otvet - 1 WHERE tg_id = ?",
                       (user_id,))
        cursor.execute("SELECT solved_tasks FROM users WHERE tg_id = ?",
                       (message.from_user.id,))
        result = cursor.fetchone()
        solved_tasks = int(result[0])
        solved_tasks += 1
        cursor.execute(
            "UPDATE users SET solved_tasks = ? WHERE tg_id = ?",
            (int(solved_tasks), message.from_user.id,))

        conn.commit()
        await state.clear()
        new_message = await message.answer(f'😿Ответ не верный😿\nколичество оставшихся попыток:{count_otvet}',
                                    reply_markup=await kb.materials(data['number']))
        user_messages[user_id] = [message.message_id, new_message.message_id]
    else:
         cursor.execute("UPDATE users SET count_otvet = 0 WHERE tg_id = ?",
                        (user_id,))
         await state.clear()
         new_message = await message.answer('😿Ответ не верный😿\nВаши попытки закончились\nВозвращайтесь завтра, чтобы решать новые задачи\nЧтобы решать задачи без ограничений, вы можете оформить подписку',
            reply_markup=await kb.glavn())
         user_messages[user_id] = [message.message_id, new_message.message_id]
         conn.commit()

@router.callback_query(F.data.startswith('to_main'))
async def nazad(callback: CallbackQuery):
    user_id = callback.message.from_user.id
    await callback.message.delete()
    if user_id in user_messages:
        for msg_id in user_messages[user_id]:
            try:
                await callback.message.bot.delete_message(chat_id=callback.message.chat.id, message_id=msg_id)
            except Exception:
                pass
        user_messages[user_id] = []
    await callback.answer('Вы перешли в главное меню')
    new_message = await callback.message.answer('Вы перешли в главное меню', reply_markup= kb.main)
    user_messages[user_id] = [callback.message.message_id, new_message.message_id]

@router.message(Command('menu'))
async def menu(message: Message):
    user_id = message.from_user.id
    await message.delete()
    if user_id in user_messages:
        for msg_id in user_messages[user_id]:
            try:
                await message.bot.delete_message(chat_id=message.chat.id, message_id=msg_id)
            except Exception:
                pass
        user_messages[user_id] = []
    new_message = await message.answer('Вы перешли в главное меню', reply_markup= kb.main)
    user_messages[user_id] = [message.message_id, new_message.message_id]


@router.message(F.text == 'Поддержка и предложения')
async def support(message: Message,state: FSMContext):
    user_id = message.from_user.id
    if any(user_id in pair for pair in active_games.keys()):
        await message.answer("Вы не можете использовать другие команды во время соревнования.")
        return
    user_id = message.from_user.id
    try:
        await message.delete()
    except Exception:
        pass
    if user_id in user_messages:
        for msg_id in user_messages[user_id]:
            try:
                await message.bot.delete_message(chat_id=message.chat.id, message_id=msg_id)
            except Exception:
                pass
        user_messages[user_id] = []
    async with async_session() as session:
        user = await session.scalar(select(User).where(User.tg_id == user_id))

    if not user:
        new_message = await message.answer('Вам нужно пройти регистрацию\n/register')
    else:
        new_message = await message.answer('Расскажите нам о вашей проблеме, или предложении одним сообщением')
        await state.set_state(Support.ansversupport)
    user_messages[user_id] = [new_message.message_id]


@router.message(Support.ansversupport)
async def supportansver(message: Message,state: FSMContext):
    await state.update_data(ansversupport=message.text)
    data = await state.get_data()
    await message.forward(supports_canal)
    await message.answer(
        f'Ваша проблема:\n{data['ansversupport']}\nНаш модератор скоро свяжется с вами для решения вашей проблемы')
    await state.clear()


@router.message(F.text == 'Таблица лидеров')
async def support(message: Message):
    user_id = message.from_user.id
    if any(user_id in pair for pair in active_games.keys()):
        await message.answer("Вы не можете использовать другие команды во время соревнования.")
        return
    await message.delete()
    if user_id in user_messages:
        for msg_id in user_messages[user_id]:
            try:
                await message.bot.delete_message(chat_id=message.chat.id, message_id=msg_id)
            except Exception:
                pass
        user_messages[user_id] = []
    async with async_session() as session:
        user = await session.scalar(select(User).where(User.tg_id == message.from_user.id))
    if not user:
        new_message = await message.answer('Вам нужно пройти регистрацию\n/register')
    else:
        top_balls_user = await get_liders()
        msg = ''
        max_users_balls = 10
        id_count = 0
        for name_user, balls_usser in top_balls_user:
            id_count += 1
            if id_count <= max_users_balls:
                msg += f'{id_count}) {name_user} -- {balls_usser} балла(ов)\n'
            else:
                break
        new_message = await message.answer(f'Топ 10 пользователей:\n{msg}')
    user_messages[user_id] = [message.message_id, new_message.message_id]

@router.message(F.text == 'Вернуться в главное меню')
async def gl(message: Message):
    user_id = message.from_user.id
    if any(user_id in pair for pair in active_games.keys()):
        await message.answer("Вы не можете использовать другие команды во время соревнования.")
        return
    await message.delete()
    if user_id in user_messages:
        for msg_id in user_messages[user_id]:
            try:
                await message.bot.delete_message(chat_id=message.chat.id, message_id=msg_id)
            except Exception:
                pass
        user_messages[user_id] = []
    new_message = await message.answer('Вы перешли в главное меню', reply_markup= kb.main)
    user_messages[user_id] = [message.message_id, new_message.message_id]

@router.message(F.text == 'Вернуться назад')
async def back_button(message: types.Message):
    user_id = message.from_user.id
    if any(user_id in pair for pair in active_games.keys()):
        await message.answer("Вы не можете использовать другие команды во время соревнования.")
        return
    await message.delete()
    if user_id in user_messages:
        for msg_id in user_messages[user_id]:
            try:
                await message.bot.delete_message(chat_id=message.chat.id, message_id=msg_id)
            except Exception:
                pass
        user_messages[user_id] = []
        new_message = await message.answer("Вы вернулись назад", reply_markup=kb.lk)
        user_messages[user_id] = [message.message_id, new_message.message_id]



@router.message(F.text == 'Статистика персонажа')
async def stats(message: Message):
    user_id = message.from_user.id
    if any(user_id in pair for pair in active_games.keys()):
        await message.answer("Вы не можете использовать другие команды во время соревнования.")
        return
    await message.delete()
    if user_id in user_messages:
        for msg_id in user_messages[user_id]:
            try:
                await message.bot.delete_message(chat_id=message.chat.id, message_id=msg_id)
            except Exception:
                pass
        user_messages[user_id] = []
        cursor.execute("SELECT name, age, whuare, number, premium, balls, solved_tasks,level, count_otvet_x, balls_x, balance FROM users WHERE tg_id = ?",
                       (message.from_user.id,))
        result = cursor.fetchone()
        name = str(result[0])
        age = int(result[1])
        whuare = str(result[2])
        number = int(result[3])
        premium = int(result[4])
        balls = int(result[5])
        solved_tasks = int(result[6])
        level = str(result[7])
        count_otvet_x = str(result[8])
        balls_x = str(result[9])
        balance = str(result[10])
        conn.commit()
        your_premium = ''
        if premium == 0:
            your_premium = 'Подиска не активированна'
        elif premium == 1:
            your_premium = 'Подиска 1 уровня'
        new_message = await message.answer(f'Никнейм: {name}({whuare})\n'
                             f'Возраст: {age}\n'
                             f'Телефон: {number}\n'
                             f'Количество решенных задач: {solved_tasks}\n'
                             f'Количество баллов: {balls}\n'
                             f'Уровень: {level}\n'
                             f'X к востановлению жизни: {count_otvet_x}\n'
                             f'X к увеличению баллов: {balls_x}\n'
                             f'Баланс: {balance}\n'
                             f'{your_premium}', reply_markup=kb.lk)
        user_messages[user_id] = [message.message_id, new_message.message_id]

@router.message(Command('pay'))
async def send_payment_options(message: types.Message):
    user_id = message.from_user.id
    if any(user_id in pair for pair in active_games.keys()):
        await message.answer("Вы не можете использовать другие команды во время соревнования.")
        return
    await message.delete()
    if user_id in user_messages:
        for msg_id in user_messages[user_id]:
            try:
                await message.bot.delete_message(chat_id=message.chat.id, message_id=msg_id)
            except Exception:
                pass
        user_messages[user_id] = []
    new_message = await message.answer("Выберите сумму для пополнения:", reply_markup=kb.donat)
    user_messages[user_id] = [message.message_id, new_message.message_id]

@router.message(F.text == 'Донат')
async def send_payment_options(message: types.Message):
    user_id = message.from_user.id
    if any(user_id in pair for pair in active_games.keys()):
        await message.answer("Вы не можете использовать другие команды во время соревнования.")
        return
    await message.delete()
    if user_id in user_messages:
        for msg_id in user_messages[user_id]:
            try:
                await message.bot.delete_message(chat_id=message.chat.id, message_id=msg_id)
            except Exception:
                pass
        user_messages[user_id] = []
    new_message = await message.answer("Выберите сумму для пополнения:", reply_markup=kb.donat)
    user_messages[user_id] = [message.message_id, new_message.message_id]

@router.callback_query(lambda callback: callback.data.startswith("pay_"))
async def send_invoice(callback: types.CallbackQuery):
    amount = int(callback.data.split("_")[1])
    prices = [LabeledPrice(label=f"Пополнение баланса ({amount} руб)", amount=amount * 100)]
    await callback.message.delete()
    await bot.send_invoice(
        chat_id=callback.message.chat.id,
        title="Пополнение баланса",
        description=f"Пополнение на {amount} руб",
        payload=f"user_{callback.from_user.id}_{amount}",
        provider_token=PAYMENT_PROVIDER_TOKEN,
        currency="RUB",
        prices=prices,
        start_parameter="test-payment"
    )
    await callback.answer()

@router.pre_checkout_query()
async def process_pre_checkout_query(pre_checkout_query: PreCheckoutQuery):
    await bot.answer_pre_checkout_query(pre_checkout_query.id, ok=True)

@router.message(F.content_type == ContentType.SUCCESSFUL_PAYMENT)
async def successful_payment(message: types.Message):
    payment_info = message.successful_payment
    amount = payment_info.total_amount / 100
    cursor.execute("UPDATE users SET balance = balance + ? WHERE tg_id = ?",
                   (amount, message.from_user.id,))
    conn.commit()
    await message.answer(f"Оплата успешно проведена! Ваш баланс пополнен на {amount} руб.")


@router.message(F.text == 'Жизни')
async def donat_life1(message: types.Message):
    user_id = message.from_user.id
    if user_id in user_messages:
        for msg_id in user_messages[user_id]:
            try:
                await message.bot.delete_message(chat_id=message.chat.id, message_id=msg_id)
            except Exception:
                pass
        user_messages[user_id] = []
    if any(user_id in pair for pair in active_games.keys()):
        await message.answer("Вы не можете использовать другие команды во время соревнования.")
        return

    await message.delete()

    new_message = await message.answer("Выберите сумму для пополнения:", reply_markup=kb.donat_life)

    user_messages[user_id] = [message.message_id, new_message.message_id]




@router.callback_query(lambda callback: callback.data.startswith("payl_"))
async def donat_life2(callback: types.CallbackQuery):
    user_id = callback.message.from_user.id
    if user_id in user_messages:
        for msg_id in user_messages[user_id]:
            try:
                await callback.message.bot.delete_message(chat_id=callback.message.chat.id, message_id=msg_id)
            except Exception:
                pass
        user_messages[user_id] = []
    try:
        amount = int(callback.data.split("_")[1])
        cursor.execute("SELECT balance FROM users WHERE tg_id = ?", (callback.from_user.id,))
        result = cursor.fetchone()
        if result is None:
            await callback.answer("Ошибка: пользователь не найден.", show_alert=True)
            return

        balance = int(result[0])
        required_balance = {3: 19, 6: 28, 9: 35, 12: 45}.get(amount)

        if required_balance is None:
            await callback.answer("Ошибка: неверная сумма.", show_alert=True)
            return

        if balance >= required_balance:
            balance -= required_balance
            cursor.execute("UPDATE users SET balance = ?, count_otvet = count_otvet + ? WHERE tg_id = ?",
                           (balance, amount, callback.from_user.id,))
            conn.commit()
            await callback.answer(f"Успешно оплачено! С вашего баланса списано {required_balance}.", show_alert=True)
        else:
            await callback.answer(f"Недостаточно средств на балансе. Необходимо {required_balance}. Чтобы пополнить баланс воспользуйтесь /pay", show_alert=True)
    except Exception as e:
        await callback.answer(f"Произошла ошибка: {e}", show_alert=True)

@router.message(F.text == 'Прокачать способности')
async def ability(message: Message):
    user_id = message.from_user.id
    if any(user_id in pair for pair in active_games.keys()):
        await message.answer("Вы не можете использовать другие команды во время соревнования.")
        return
    await message.delete()
    if user_id in user_messages:
        for msg_id in user_messages[user_id]:
            try:
                await message.bot.delete_message(chat_id=message.chat.id, message_id=msg_id)
            except Exception:
                pass
        user_messages[user_id] = []
    cursor.execute("SELECT count_otvet, count_otvet_x, balls_x, balance, balls FROM users WHERE tg_id = ?",
                   (message.from_user.id,))
    result = cursor.fetchone()
    count_otvet = int(result[0])
    count_otvet_x = str(result[1])
    balls_x = str(result[2])
    balance = int(result[3])
    balls = str(result[4])
    new_message = await message.answer(f'Ваши способности:\n'
                                 f'Количество жизней: {count_otvet}\n'
                                 f'X к востановлению жизни: {count_otvet_x}\n'
                                 f'X к увеличению баллов:{balls_x}\n'
                                 f'\nКоличество баллов:{balls}'
                                 f'\nБаланс: {balance}\n'
                                 f'\nВыберите способность, которую хотите прокочать:', reply_markup=kb.ability)
    user_messages[user_id] = [message.message_id, new_message.message_id]
    conn.commit()

@router.message(F.text == 'X к увеличению баллов')
async def ability(message: Message,state: FSMContext):
    user_id = message.from_user.id
    if any(user_id in pair for pair in active_games.keys()):
        await message.answer("Вы не можете использовать другие команды во время соревнования.")
        return
    await message.delete()
    if user_id in user_messages:
        for msg_id in user_messages[user_id]:
            try:
                await message.bot.delete_message(chat_id=message.chat.id, message_id=msg_id)
            except Exception:
                pass
        user_messages[user_id] = []
        cursor.execute("SELECT balls_x FROM users WHERE tg_id = ?",
                       (message.from_user.id,))
        result = cursor.fetchone()
        balls_x = str(result[0])
        upgrade_costs_balls = {
            0: (9, 1.2),  # count_otvet_x до 1.2 стоит 9 баллов
            1.2: (19, 1.4),
            1.4: (29, 1.8),
            1.8: (39, 2.0),
        }
        next_level_cost_balls, next_level_value_balls = upgrade_costs_balls.get(float(balls_x),
                                                              (0, 0))
        upgrade_costs_pay = {
            0: (19, 1.2),  # count_otvet_x до 1.2 стоит 9 баллов
            1.2: (29, 1.4),
            1.4: (39, 1.8),
            1.8: (49, 2.0),
        }
        next_level_cost_pay, next_level_value_pay = upgrade_costs_pay.get(float(balls_x),
                                                                                (0, 0))
        if next_level_cost_balls <= 0:
            new_message = await message.answer(
                f'На данный момент у вас X {balls_x} к востановлению баллов\n'
                f'Это максимальный уровень\n',
                reply_markup=kb.pump)
        else:
            new_message = await message.answer(
                f'На данный момент у вас X {balls_x} к востановлению баллов'
                f'\nСледующее улучшение: {next_level_value_pay}'
                f'\nСтоимость следующего улучшения за баллы: {next_level_cost_balls}'
                f'\nСтоимость следующего улучшения за донат: {next_level_cost_pay}'
                f'\nВыберите за каую валюту вы хотите прокачать способность(!!!после выбора ваши баллы(донат рубли) сразу спишуться с баланса!!!)',
                reply_markup=kb.pump)
        conn.commit()
        await state.set_state(Donat_xzizn.restoration_balls)
        user_messages[user_id] = [message.message_id, new_message.message_id]

@router.message(Donat_xzizn.restoration_balls)
async def restoration_of_balls(message: Message,state: FSMContext):
    user_id = message.from_user.id
    await message.delete()
    if user_id in user_messages:
        for msg_id in user_messages[user_id]:
            try:
                await message.bot.delete_message(chat_id=message.chat.id, message_id=msg_id)
            except Exception:
                pass
        user_messages[user_id] = []
    cursor.execute("SELECT balls_x, balls,balance FROM users WHERE tg_id = ?",
                   (message.from_user.id,))
    result = cursor.fetchone()
    balls_x = float(result[0])
    balls = int(result[1])
    balance = int(result[2])
    upgrade_costs_balls = {
        0: (9, 1.2),
        1.2: (19, 1.4),
        1.4: (29, 1.8),
        1.8: (39, 2.0),
    }
    next_level_cost_balls, next_level_value_balls = upgrade_costs_balls.get(float(balls_x),
                                                                            (0, 0))
    upgrade_costs_pay = {
        0: (19, 1.2),
        1.2: (29, 1.4),
        1.4: (39, 1.8),
        1.8: (49, 2.0),
    }
    next_level_cost_pay, next_level_value_pay = upgrade_costs_pay.get(float(balls_x),
                                                                      (0, 0))

    if message.text == 'За баллы':
        if next_level_cost_balls > 0 and balls >= next_level_cost_balls:
            balls -= next_level_cost_balls
            balls_x = next_level_value_balls

            cursor.execute(
                "UPDATE users SET balls_x = ?, balls = ? WHERE tg_id = ?",
                (balls_x, balls, message.from_user.id,)
            )
            conn.commit()
            await state.clear()
            new_message = await message.answer(
                f"Вы прокачали X к востановлению баллов!\n"
                f"Теперь вы будете получать за каждый ответ {balls_x} балла.\n"
                f"Оставшиеся баллы: {balls}", reply_markup=kb.ability
            )
        else:
            new_message = await message.answer(
                f"Недостаточно баллов для прокачки. У вас {balls} баллов. "
                f"Стоимость следующей прокачки: {next_level_cost_balls} баллов." if next_level_cost_balls > 0 else "Максимальный уровень прокачки достигнут!",
                reply_markup=kb.ability
            )
        user_messages[user_id] = [message.message_id, new_message.message_id]
        await state.clear()


    if message.text == 'За донат':
        if next_level_cost_pay > 0 and balance >= next_level_cost_pay:
            balance -= next_level_cost_pay
            balls_x = next_level_value_pay

            cursor.execute(
                "UPDATE users SET balls_x = ?, balance = ? WHERE tg_id = ?",
                (balls_x, balance, message.from_user.id,)
            )
            conn.commit()
            await state.clear()
            new_message = await message.answer(
                f"Вы прокачали X к востановлению баллов!\n"
                f"Теперь вы будете получать за каждый ответ {balls_x} балла.\n"
                f"Оставшийся баланс: {balance}", reply_markup=kb.ability
            )
        else:
            new_message = await message.answer(
                f"Недостаточно баллов для прокачки. У вас {balance} баллов. "
                f"Стоимость следующей прокачки: {next_level_cost_pay} баллов." if next_level_cost_pay > 0 else "Максимальный уровень прокачки достигнут!",
                reply_markup=kb.ability
            )
        user_messages[user_id] = [message.message_id, new_message.message_id]
        await state.clear()



@router.message(F.text == 'X к востановлению жизни')
async def restoration_of_life(message: Message,state: FSMContext):
    user_id = message.from_user.id
    if any(user_id in pair for pair in active_games.keys()):
        await message.answer("Вы не можете использовать другие команды во время соревнования.")
        return
    await message.delete()
    if user_id in user_messages:
        for msg_id in user_messages[user_id]:
            try:
                await message.bot.delete_message(chat_id=message.chat.id, message_id=msg_id)
            except Exception:
                pass
        user_messages[user_id] = []
        cursor.execute("SELECT count_otvet_x FROM users WHERE tg_id = ?",
                       (message.from_user.id,))
        result = cursor.fetchone()
        count_otvet_x = str(result[0])
        upgrade_costs_balls1 = {
            0: (9, 1.2),
            1.2: (19, 1.4),
            1.4: (29, 1.8),
            1.8: (39, 2.0),
            2.0: (49, 2.2),
            2.2: (59, 2.4),
            2.4: (69, 2.8),
            2.8: (69, 3.0),
        }
        next_level_cost_balls1, next_level_value_balls1 = upgrade_costs_balls1.get(float(count_otvet_x),
                                                                                (0, 0))
        upgrade_costs_pay1 = {
            0: (9, 1.2),
            1.2: (19, 1.4),
            1.4: (29, 1.8),
            1.8: (39, 2.0),
            2.0: (49, 2.2),
            2.2: (59, 2.4),
            2.4: (69, 2.8),
            2.8: (69, 3.0),
        }
        next_level_cost_pay1, next_level_value_pay1 = upgrade_costs_pay1.get(float(count_otvet_x),
                                                                          (0, 0))
        if next_level_cost_balls1 <= 0:
            new_message = await message.answer(
                f'На данный момент у вас X {count_otvet_x} к востановлению баллов\n'
                f'Это максимальный уровень\n',
                reply_markup=kb.pump)
        else:
            new_message = await message.answer(
                f'На данный момент у вас X {count_otvet_x} к востановлению жизней'
                f'\nСледующее улучшение: {next_level_value_pay1}'
                f'\nСтоимость следующего улучшения за баллы: {next_level_cost_balls1}'
                f'\nСтоимость следующего улучшения за донат: {next_level_cost_pay1}'
                f'\nВыберите за каую валюту вы хотите прокачать способность(!!!после выбора ваши баллы(донат рубли) сразу спишуться с баланса!!!)',
                reply_markup=kb.pump)
        conn.commit()
        await state.set_state(Donat_xzizn.restoration_life)
        user_messages[user_id] = [message.message_id, new_message.message_id]

@router.message(Donat_xzizn.restoration_life)
async def restoration_of_life_one(message: Message,state: FSMContext):
    user_id = message.from_user.id
    await message.delete()
    if user_id in user_messages:
        for msg_id in user_messages[user_id]:
            try:
                await message.bot.delete_message(chat_id=message.chat.id, message_id=msg_id)
            except Exception:
                pass
        user_messages[user_id] = []
    cursor.execute("SELECT count_otvet_x, balls,balance FROM users WHERE tg_id = ?",
                   (message.from_user.id,))
    result = cursor.fetchone()
    count_otvet_x = float(result[0])
    balls = int(result[1])
    balance = int(result[2])
    upgrade_costs_balls1 = {
        0: (9, 1.2),
        1.2: (19, 1.4),
        1.4: (29, 1.8),
        1.8: (39, 2.0),
        2.0: (49, 2.2),
        2.2: (59, 2.4),
        2.4: (69, 2.8),
        2.8: (69, 3.0),
    }
    next_level_cost_balls1, next_level_value_balls1 = upgrade_costs_balls1.get(count_otvet_x,
                                                                            (0, 0))

    upgrade_costs_pay1 = {
        0: (9, 1.2),
        1.2: (19, 1.4),
        1.4: (29, 1.8),
        1.8: (39, 2.0),
        2.0: (49, 2.2),
        2.2: (59, 2.4),
        2.4: (69, 2.8),
        2.8: (69, 3.0),
    }
    next_level_cost_pay1, next_level_value_pay1 = upgrade_costs_pay1.get(count_otvet_x,
                                                                      (0, 0))
    if message.text == 'За баллы':

        if next_level_cost_balls1 > 0 and balls >= next_level_cost_balls1:
            balls -= next_level_cost_balls1
            count_otvet_x = next_level_value_balls1

            cursor.execute(
                "UPDATE users SET count_otvet_x = ?, balls = ? WHERE tg_id = ?",
                (count_otvet_x, balls, message.from_user.id,)
            )
            conn.commit()
            await state.clear()
            new_message = await message.answer(
                f"Вы прокачали X к востановлению жизни!\n"
                f"Теперь вы будете получать за каждый ответ {count_otvet_x} балла.\n"
                f"Оставшиеся баллы: {balls}", reply_markup=kb.ability
            )
        else:
            new_message = await message.answer(
                f"Недостаточно баллов для прокачки. У вас {balls} баллов. "
                f"Стоимость следующей прокачки: {next_level_cost_balls1} баллов." if next_level_cost_balls1 > 0 else f"Максимальный уровень прокачки достигнут!", reply_markup=kb.ability
            )
        user_messages[user_id] = [message.message_id, new_message.message_id]
        await state.clear()

    if message.text == 'За донат':
        if next_level_cost_pay1 > 0 and balance >= next_level_cost_pay1:
            balance -= next_level_cost_pay1
            count_otvet_x = next_level_value_pay1

            cursor.execute(
                "UPDATE users SET count_otvet_x = ?, balance = ? WHERE tg_id = ?",
                (count_otvet_x, balance, message.from_user.id,)
            )
            conn.commit()
            await state.clear()
            new_message = await message.answer(
                f"Вы прокачали X к востановлению баллов!\n"
                f"Теперь вы будете получать за каждый ответ {count_otvet_x} балла.\n"
                f"Оставшийся баланс: {balance}", reply_markup=kb.ability
            )
        else:
            new_message = await message.answer(
                f"Недостаточно баллов для прокачки. У вас {balance} баллов. "
                f"Стоимость следующей прокачки: {next_level_cost_pay1} баллов." if next_level_cost_pay1 > 0 else "Максимальный уровень прокачки достигнут!",
                reply_markup=kb.ability
            )
        user_messages[user_id] = [message.message_id, new_message.message_id]
        await state.clear()



async def check_premium_arena(user_id):
    cursor.execute("SELECT premium, count_otvet FROM users WHERE tg_id = ?",
                   (user_id,))
    result = cursor.fetchone()
    premium = int(result[0])
    count_otvet = int(result[1])
    conn.commit()
    if premium == 0 and count_otvet == 0:
        return False
    else:
        return True


waiting_queue = {}
active_games = {}

# Список активных пользователей, которым нельзя отправлять команды
active_players = set()


@router.message(F.text == 'Арена')
async def arena(message: Message):
    user_id = message.from_user.id
    await message.delete()

    if user_id in active_players:
        await message.answer("Вы уже находитесь в соревновании. Вы не можете использовать другие команды.")
        return

    if user_id in user_messages:
        for msg_id in user_messages[user_id]:
            try:
                await message.bot.delete_message(chat_id=message.chat.id, message_id=msg_id)
            except Exception:
                pass
        user_messages[user_id] = []

    if await check_premium_arena(user_id):
        new_message = await message.answer(f'Выберите категорию материала', reply_markup=await kb.arenacatalog())
        cursor.execute("UPDATE users SET count_otvet = count_otvet - 2 WHERE tg_id = ?", (message.from_user.id,))
        conn.commit()
    else:
        new_message = await message.answer(f'У вас закончилились попытки\n'
                                           f'Чтобы иметь неограниченный доступ к арене, вы можете оформить подписку',
                                           reply_markup=await kb.main())
    user_messages[user_id] = [message.message_id, new_message.message_id]


@router.callback_query(F.data.startswith('arenacategory_'))
async def select_category(callback: CallbackQuery):
    user_id = callback.from_user.id
    category = callback.data.split('_')[1]

    if category not in waiting_queue:
        waiting_queue[category] = []

    if waiting_queue[category]:
        opponent_id = waiting_queue[category].pop(0)

        active_games[(user_id, opponent_id)] = {
            "category": category,
            "tasks": [],
            "scores": {user_id: 0, opponent_id: 0},
        }
        active_players.add(user_id)
        active_players.add(opponent_id)

        await bot.send_message(user_id, f"Соперник найден! Соревнование начинается.",reply_markup=await kb.leave())
        await bot.send_message(opponent_id, f"Соперник найден! Соревнование начинается.",reply_markup=await kb.leave())
        await send_task(user_id, opponent_id, category)
    else:
        waiting_queue[category].append(user_id)
        await callback.message.edit_text("Ожидаем соперника...",reply_markup=await kb.leave())




async def send_task(user1_id, user2_id, category):
    task = get_random_task(category)
    if not task:
        await bot.send_message(user1_id, "Ошибка: задачи отсутствуют в выбранной категории.")
        await bot.send_message(user2_id, "Ошибка: задачи отсутствуют в выбранной категории.")
        return
    active_games[(user1_id, user2_id)]["tasks"].append(task)

    try:

        await bot.send_photo(user1_id, task['question'], caption="Ваша задача:")
        await bot.send_photo(user2_id, task['question'], caption="Ваша задача:")
    except Exception as e:
        pass

def get_random_task(category):
    cursor.execute("SELECT id, photo, answer FROM photos WHERE materialcat = ? ORDER BY RANDOM() LIMIT 1;", (category,))
    result = cursor.fetchone()
    if result:
        return {"id": result[0], "question": result[1], "answer": result[2]}
    return None

@router.message()
async def handle_answer(message: Message):
    user_id = message.from_user.id

    # Проверяем, находится ли пользователь в активной игре
    if user_id in active_players:
        active_game = next(
            ((game_data, user1, user2) for (user1, user2), game_data in active_games.items() if
             user_id in (user1, user2)),
            None,
        )
        if not active_game:
            return

        game_data, user1_id, user2_id = active_game
        task = game_data["tasks"][-1]
        opponent_id = user1_id if user_id == user2_id else user2_id

        if message.text.strip() == task["answer"]:
            game_data["scores"][user_id] += 1
            cursor.execute("UPDATE users SET balls = balls + 1 WHERE tg_id = ?", (user_id,))
            conn.commit()

            await message.answer("🎉 Верно! Вы получили 1 балл.",reply_markup=await kb.leave())
            await bot.send_message(opponent_id, "Ваш соперник ответил правильно.",reply_markup=await kb.leave())

            if len(game_data["tasks"]) >= 3:
                winner_id = max(game_data["scores"], key=game_data["scores"].get)
                cursor.execute("SELECT name FROM users WHERE tg_id = ?", (winner_id,))
                result = cursor.fetchone()
                name = str(result[0])
                scores = game_data["scores"]
                await bot.send_message(user1_id, f"Игра окончена! Победитель: {name} с {scores[winner_id]} баллами.",reply_markup=await kb.main())
                await bot.send_message(user2_id, f"Игра окончена! Победитель: {name} с {scores[winner_id]} баллами.",reply_markup=await kb.main())
                active_players.remove(user1_id)
                active_players.remove(user2_id)
                del active_games[(user1_id, user2_id)]
            else:
                await send_task(user1_id, user2_id, game_data["category"])
        else:
            await message.answer("Ответ неверный")
    else:
        await message.answer("Вы не можете отправлять сообщения во время соревнования.")

@router.message(F.text == 'Покинуть соревнование')
async def leave_competition(message: Message):
    user_id = message.from_user.id

    if user_id in active_players:
        game_to_exit = next(((user1, user2) for (user1, user2) in active_games if user_id in (user1, user2)), None)

        if game_to_exit:
            del active_games[game_to_exit]
            await message.answer("Вы вышли из игры. Вы можете использовать другие команды.", reply_markup=await kb.main())
            active_players.remove(user_id)
        else:
            await message.answer("Вы не участвуйте в игре.")
    else:
        await message.answer("Вы не находитесь в соревновании.")
