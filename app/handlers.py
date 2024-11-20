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
count_otvet = 0

async def count_otvetil_user(tg_id):
    global count_otvet
    cursor.execute("SELECT count_otvet FROM users WHERE tg_id = ?",
                   (tg_id,))
    result = cursor.fetchone()
    count_otvet = int(result[0])
    conn.commit()

async def count_save_otvetil_user(count_otvet_posle,tg_id):
    global count_otvet
    cursor.execute(
        "UPDATE users SET count_otvet = ? WHERE tg_id = ?",
        (int(count_otvet_posle), tg_id,))
    conn.commit()



supports_canal = '-1002335317649'





async def update_count_otvet(tg_id):
    global count_otvet
    if count_otvet < 3:
        while count_otvet <= 2:
            await asyncio.sleep(14400)
            count_otvet += 1
            await count_save_otvetil_user(count_otvet,tg_id)

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
    await message.answer(f'Приветствуем вас {message.from_user.full_name}.\nЭтот бот поможет вам подготовиться к экзаменам, или узнать что-то новое. Выберите одну из предложенных команд, для начала использования бота.', reply_markup = kb.main)

@router.message(Command('help'))
async def cmd_start(message: Message):
    await message.answer('/start - Перезапуск бота\n'
                         '/register - регестрация')

@router.message(Command('register'))
async def reg(message: types.Message, state: FSMContext):

    async with async_session() as session:
        user = await session.scalar(select(User).where(User.tg_id == message.from_user.id))
    if not user:
        await state.set_state(Register.login)
        await state.update_data(tg_id = message.from_user.id)
        await message.answer('Введите отображаемое имя',reply_markup=types.ReplyKeyboardRemove())
    else:
        await message.answer('Вы уже зарегистрированы')

@router.message(Register.login)
async def reg_login(message: Message, state: FSMContext):
    async with async_session() as session:
        user_loggin = await session.scalar(select(User).where(User.name == message.text))
    if (len(message.text) > 15) or ('@' in message.text) or ('/' in message.text) or (' ' in message.text):
        await message.answer('Логин должен содержать не больше 15 символов, не содержать пробелов и символов / и @')

    elif user_loggin:
        await message.answer('Пользователь с таким именем уже существует')
    else:
        await state.update_data(login = message.text)
        await state.set_state(Register.age)
        await message.answer('Введите ваш возраст')

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
    last_message = await message.answer(f'Ваш логин: {data["login"]} ({data["whu"]})\nВаш возраст:{data["age"]}\nВаш номер:{data["number"]}',reply_markup=kb.main)
    cursor.execute(
        "INSERT INTO users (tg_id, name, age, count_otvet, whuare, number, premium,balls,solved_tasks,balance,count_otvet_x,balls_x,level) VALUES (?,?,?,?, ?, ?, ?, ?,?,?,?,?,?)",
        (data['tg_id'], data['login'], data['age'], 3, data['whu'], data['number'], 0,0,0,0,0,0,0,))
    conn.commit()

    await state.clear()

@router.message(F.text == 'Мой персонаж')
async def lk(message: Message):
    user_id = message.from_user.id
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
    await message.delete()
    if user_id in user_messages:
        for msg_id in user_messages[user_id]:
            try:
                await message.bot.delete_message(chat_id=message.chat.id, message_id=msg_id)
            except Exception:
                pass
        user_messages[user_id] = []
    await count_otvetil_user(message.from_user.id)
    if count_otvet > 0:

        new_message = await message.answer(f'Выбирите предмет', reply_markup=await kb.materialcategorii())
    else:
        await message.answer(
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
            await state.update_data(vanswer = i.otvet)
    await state.set_state(Otvetil.answer)
    await callback.message.answer('Введите ответ:')

@router.message(Otvetil.answer)
async def his_answer(message: Message, state: FSMContext):
    global count_otvet
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
    await count_otvetil_user(message.from_user.id)
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
    elif data['vanswer'] != data['answer'] and count_otvet >1:
        count_otvet -= 1
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
        await count_save_otvetil_user(count_otvet, message.from_user.id)
        new_message = await message.answer(f'😿Ответ не верный😿\nколичество оставшихся попыток:{count_otvet}',
                                    reply_markup=await kb.materials(data['number']))
        await update_count_otvet(message.from_user.id)
        user_messages[user_id] = [message.message_id, new_message.message_id]
    else:
         count_otvet = 0
         await count_save_otvetil_user(count_otvet,message.from_user.id)
         await state.clear()
         new_message = await message.answer('😿Ответ не верный😿\nВаши попытки закончились\nВозвращайтесь завтра, чтобы решать новые задачи\nЧтобы решать задачи без ограничений, вы можете оформить подписку',
            reply_markup=await kb.glavn())
         await update_count_otvet(message.from_user.id)
         user_messages[user_id] = [message.message_id, new_message.message_id]


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


@router.message(F.text == 'Поддержка и предложения')
async def support(message: Message,state: FSMContext):
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
    await message.delete()
    if user_id in user_messages:
        for msg_id in user_messages[user_id]:
            try:
                await message.bot.delete_message(chat_id=message.chat.id, message_id=msg_id)
            except Exception:
                pass
        user_messages[user_id] = []
        cursor.execute("SELECT name, age, whuare, number, premium, balls, solved_tasks,level, count_otvet_x, balls_x FROM users WHERE tg_id = ?",
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
        count_otvet_x = int(result[8])
        balls_x = str(result[9])
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
                             f'{your_premium}', reply_markup=kb.lk)
        user_messages[user_id] = [message.message_id, new_message.message_id]

@router.message(Command('pay'))
async def send_payment_options(message: types.Message):
    await message.answer("Выберите сумму для пополнения:", reply_markup=kb.donat)

@router.callback_query(lambda callback: callback.data.startswith("pay_"))
async def send_invoice(callback: types.CallbackQuery):
    amount = int(callback.data.split("_")[1])
    prices = [LabeledPrice(label=f"Пополнение баланса ({amount} руб)", amount=amount * 100)]
    print(amount, prices)

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
    # Подтверждаем запрос
    print('ok')
    await bot.answer_pre_checkout_query(pre_checkout_query.id, ok=True)

@router.message(F.content_type == ContentType.SUCCESSFUL_PAYMENT)
async def successful_payment(message: types.Message):
    payment_info = message.successful_payment
    amount = payment_info.total_amount / 100  # Преобразуем в рубли
    user_id = message.from_user.id

    # Обновляем баланс пользователя в базе данных
    cursor.execute("UPDATE users SET balance = balance + ? WHERE tg_id = ?", (amount, user_id))
    conn.commit()

    # Отправляем уведомление
    await message.answer(f"Оплата успешно проведена! Ваш баланс пополнен на {amount} руб.")

@router.message(F.text == 'Прокачать способности')
async def ability(message: Message):
    user_id = message.from_user.id
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
    balans = int(result[3])
    balls = str(result[4])
    new_message = await message.answer(f'Ваши способности:\n'
                                 f'Количество жизней: {count_otvet}\n'
                                 f'X к востановлению жизни: {count_otvet_x}\n'
                                 f'X к увеличению баллов:{balls_x}\n'
                                 f'\nКоличество баллов:{balls}'
                                 f'\nБаланс: {balans}\n'
                                 f'\nВыберите способность, которую хотите прокочать:', reply_markup=kb.ability)
    user_messages[user_id] = [message.message_id, new_message.message_id]
    conn.commit()

@router.message(F.text == 'X к увеличению баллов')
async def ability(message: Message,state: FSMContext):
    user_id = message.from_user.id
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
        balls_x = float(result[0])
        new_message = await message.answer(
            f'На данный момент у вас X {balls_x} к востановлению баллов\nВыберите за каую валюту вы хотите прокачать способность',
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

    if message.text == 'За баллы':
        cursor.execute("SELECT balls_x, balls FROM users WHERE tg_id = ?",
                       (message.from_user.id,))
        result = cursor.fetchone()
        balls_x = float(result[0])
        balls = int(result[1])
        upgrade_costs = {
            0: (9, 1.2),  # count_otvet_x до 1.2 стоит 9 баллов
            1.2: (19, 1.4),
            1.4: (29, 1.8),
            1.8: (39, 2.0),
        }

        next_level_cost, next_level_value = upgrade_costs.get(balls_x,
                                                              (0, 0))

        if next_level_cost > 0 and balls >= next_level_cost:
            balls -= next_level_cost
            balls_x = next_level_value

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
                f"Стоимость следующей прокачки: {next_level_cost} баллов." if next_level_cost > 0 else "Максимальный уровень прокачки достигнут!", reply_markup=kb.ability
            )
        user_messages[user_id] = [message.message_id, new_message.message_id]


    if message.text == 'За донат':
        await message.answer(f'')
        await state.clear()



@router.message(F.text == 'X к востановлению жизни')
async def restoration_of_life(message: Message,state: FSMContext):
    user_id = message.from_user.id
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
        count_otvet_x = float(result[0])
        new_message = await message.answer(f'На данный момент у вас X {count_otvet_x}  к востановлению жизни\nВыберите за каую валюту вы хотите прокачать способность', reply_markup= kb.pump)
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

    if message.text == 'За баллы':
        cursor.execute("SELECT count_otvet_x, balls FROM users WHERE tg_id = ?",
                       (message.from_user.id,))
        result = cursor.fetchone()
        count_otvet_x = float(result[0])
        balls = int(result[1])
        upgrade_costs = {
            0: (9, 1.2),  # count_otvet_x до 1.2 стоит 9 баллов
            1.2: (19, 1.4),
            1.4: (29, 1.8),
            1.8: (39, 2.0),
            2.0: (49, 2.2),
            2.2: (59, 2.4),
            2.4: (69, 2.8),
            2.8: (69, 3.0),
        }

        next_level_cost, next_level_value = upgrade_costs.get(count_otvet_x,
                                                              (0, 0))

        if next_level_cost > 0 and balls >= next_level_cost:
            balls -= next_level_cost
            count_otvet_x = next_level_value

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
                f"Стоимость следующей прокачки: {next_level_cost} баллов." if next_level_cost > 0 else "Максимальный уровень прокачки достигнут!", reply_markup=kb.ability
            )
        user_messages[user_id] = [message.message_id, new_message.message_id]


    if message.text == 'За донат':
        await message.answer(f'')
        await state.clear()