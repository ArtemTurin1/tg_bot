import asyncio
from gc import callbacks
from site import USER_BASE

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.date import DateTrigger
from datetime import datetime, timedelta
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

from app.keyboards import form_redact

PAYMENT_PROVIDER_TOKEN = "390540012:LIVE:62751"
router = Router()
import random

user_messages = {}

conn = sqlite3.connect('db.sqlite3')
cursor = conn.cursor()
bot = Bot(token='7882619849:AAF4WABwNdKvnQ39-mgh0STAztWMyD-VXpM')

supports_canal = '-1002427853005'

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
    id_num = State()
    answer = State()
    number = State()

class Register(StatesGroup):
    login = State()
    age = State()
    whu = State()
    number = State()
    tg_id = State()
    referral = State()

active_timers = {}

async def reset_premium(user_id: int):
    async with async_session() as session:
        user = await session.scalar(select(User).where(User.tg_id == user_id))
        if user:
            user.premium = 0
            await session.commit()
            print(f"Премиум для пользователя {user_id} обнулён.")

async def start_timer_for_attempts(user_id):
    while True:
        cursor.execute("SELECT count_otvet_x FROM users WHERE tg_id = ?", (user_id,))
        count_otvet_x = int(cursor.fetchone()[0])
        if count_otvet_x == 0:
            count_otvet_x = 1
        await asyncio.sleep(3600 / count_otvet_x)
        conn.commit()
        cursor.execute("""
                UPDATE users 
                SET count_otvet = CASE 
                                      WHEN count_otvet < 3 THEN count_otvet + 1  
                                   END 
                WHERE tg_id = ?;
            """, (user_id,))
        conn.commit()
        cursor.execute("SELECT count_otvet FROM users WHERE tg_id = ?", (user_id,))
        count_otvet = int(cursor.fetchone()[0])

        if count_otvet >= 3:
            active_timers.pop(user_id, None)
            break


@router.message(F.text == 'Добавить задание')
async def add_task(message: Message):
    cursor.execute("SELECT name FROM users WHERE tg_id = ?", (message.chat.id,))
    result = cursor.fetchone()
    name = str(result[0])
    user_id = message.from_user.id
    await message.delete()
    if user_id in user_messages:
        for msg_id in user_messages[user_id]:
            try:
                await message.bot.delete_message(chat_id=message.chat.id, message_id=msg_id)
            except Exception:
                pass
        user_messages[user_id] = []
    if name[-1] == '💯':

        new_message = await message.answer("Выберите задание, которое вы хотите добавить:", reply_markup= await kb.add_materialcategorii())

    else:
        new_message = await message.answer("Вы не можете добавлять задания(",
                                           reply_markup=kb.main)
    user_messages[user_id] = [message.message_id, new_message.message_id]

class AddMaterial(StatesGroup):
    id_material = State()
    id_materialcat = State()
    waiting_for_file_or_photo = State()
    waiting_for_answer = State()

@router.callback_query(F.data.startswith('task_'))
async def task_selected(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text(
        f"Выберите номер", reply_markup=await kb.add_materials(callback.data.split('_')[1]))
    await state.update_data(id_task=callback.data.split('_')[1])
    await state.set_state(AddMaterial.id_material)




@router.callback_query(AddMaterial.id_material, F.data.startswith('addmaterial_'))
async def material_category(callback: CallbackQuery, state: FSMContext):
    user_id = callback.message.from_user.id
    await callback.message.delete()

    # Удаление старых сообщений пользователя
    if user_id in user_messages:
        for msg_id in user_messages[user_id]:
            try:
                await callback.message.bot.delete_message(chat_id=callback.message.chat.id, message_id=msg_id)
            except Exception:
                pass
        user_messages[user_id] = []

    # Получаем данные о материале
    material_data = await rq.get_material(callback.data.split('_')[1])

    # Определяем, нужно ли отправить файл или фото
    if material_data.materialcat == 2 and material_data.name == 'Номер 1-5':
        await callback.message.answer("Пришлите файл с заданием.")
    else:
        await callback.message.answer("Пришлите фото с заданием.")

    # Сохранение типа материала в состояние
    await state.update_data(id_material=callback.data.split('_')[1])

    # Переключение FSM на ожидание файла или фото
    await state.set_state(AddMaterial.waiting_for_file_or_photo)


# Обработка получения файла или фото
@router.message(AddMaterial.waiting_for_file_or_photo, F.content_type.in_({'photo', 'document'}))
async def process_material(message: Message, state: FSMContext):
    document = message.document  # Получаем объект документа

    if message.photo:
        file_id = message.photo[-1].file_id
        file_type = "photo"
    elif message.document:
        file_id = message.document.file_id
        file_type = "document"
    else:
        await message.answer("Пожалуйста, отправьте фото или файл с заданием.")
        return

    # Сохраняем file_id в состояние
    await state.update_data(file_id=file_id, file_type=file_type)

    await message.answer("Файл получен! Теперь отправьте ваш ответ.")

    # Переключение на ожидание ответа
    await state.set_state(AddMaterial.waiting_for_answer)


# Обработка ответа пользователя
@router.message(AddMaterial.waiting_for_answer, F.text)
async def process_answer(message: Message, state: FSMContext):
    user_data = await state.get_data()
    id_task = user_data['id_task']
    id_material = user_data['id_material']
    file_id = user_data['file_id']
    answer = message.text

    # Сохранение в базу данных (пример)
    await save_to_database(id_task=id_task, id_material=id_material, file_id=file_id, answer=answer)

    await message.answer("Ваше задание успешно сохранено в базе данных!")

    # Завершаем FSM
    await state.clear()


async def save_to_database(id_task, id_material, file_id, answer):

    cursor.execute("SELECT MAX(id) FROM photos")
    result = cursor.fetchone()
    max_id = int(result[0]) + 1
    print(max_id, id_task, id_material, file_id, answer)
    cursor.execute("""
        INSERT INTO photos (id, photo, answer, material, materialcat)
        VALUES (?, ?, ?, ?, ?)
    """, (max_id, file_id, answer, id_material, id_task,))
    conn.commit()



@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    await state.clear()
    user_id = message.from_user.id
    if any(user_id in pair for pair in active_games.keys()):
        await message.answer("Вы не можете использовать другие команды во время соревнования.")
        return
    await message.answer(f'👋 Всем привет! Добро пожаловать в PLAYEX – вашего помощника в учебе! Мы понимаем, что подготовка к экзаменам может быть сложной и утомительной, особенно если ваш репетитор не объясняет задания так, как нужно.'
                         f'\n\n📚 Устали от скучной учёбы? Плохо усваиваете материал? Не переживайте, мы здесь, чтобы помочь вам! '
                         f'\n\n🎮 Занимайтесь подготовкой к ОГЭ и ЕГЭ с удовольствием, играя в нашем телеграм-боте! С нами вы сможете улучшить свои знания и навыки в игровой форме, что сделает процесс обучения увлекательным и эффективным. '
                         f'\n\n✨ Присоединяйтесь к PLAYEX и начните свое захватывающее учебное приключение уже сегодня!', reply_markup = kb.main)




@router.message(Command('help'))
async def cmd_start(message: Message):
    user_id = message.from_user.id
    if any(user_id in pair for pair in active_games.keys()):
        await message.answer("Вы не можете использовать другие команды во время соревнования.")
        return
    await message.answer('Если возникли вопросы/проблемы связанные с ботом или появилось предложение по улучшению бота, то можно сообщить об этом в пункте Поддержка и предложения\n(если желаете получить обратную связь, то откройте профиль в настройках телеграмма)\n'
                         '\n/start - Перезапуск бота\n'
                         '\n/register - регистрация\n'
                         '\n/menu переход в главное меню\n')

@router.message(Command('register'))
async def reg(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    if any(user_id in pair for pair in active_games.keys()):
        await message.answer("⛔Вы не можете использовать другие команды во время соревнования⛔")
        return
    async with async_session() as session:
        user = await session.scalar(select(User).where(User.tg_id == message.from_user.id))
    if not user:
        await state.set_state(Register.login)
        await state.update_data(tg_id = message.from_user.id)
        await message.answer('🎭Придумай себе крутой никнейм!\n'
                             'Он появится в таблице лидеров, так что выбирай запоминающийся!',reply_markup=types.ReplyKeyboardRemove())
    else:
        await message.answer('Вы уже зарегистрированы')

@router.message(Register.login)
async def reg_login(message: Message, state: FSMContext):
    async with async_session() as session:
        user_loggin = await session.scalar(select(User).where(User.name == message.text))
    if (len(message.text) > 15) or ('@' in message.text) or ('/' in message.text) or (' ' in message.text):
        await message.answer('🚫Кажется твой никнейм не подходит. Он должен содержать не более 15 символов и не может включать пробелы, а также символы / и @.🚫'
                             '\nПожалуйста, попробуй ещё раз.')

    elif user_loggin:
        await message.answer('🚫 Упс! Пользователь с таким именем уже существует. Пожалуйста, выберите другое имя или попробуйте снова. Если вам нужна помощь, просто дайте знать! 😊')
    else:
        await state.update_data(login = message.text)
        await state.set_state(Register.age)
        await message.answer('👤Введи свой возраст! Это поможет нам подобрать для тебя самые подходящие задания и сделать игру еще интереснее!')

@router.message(Register.age)
async def reg_age(message: Message, state: FSMContext):
    if not is_number(message.text):
        await message.answer('⚠️ Введите свой возраст цифрами. Пожалуйста, повторите попытку и убедитесь, что используете числа.')
    else:
        await state.update_data(age=message.text)
        await state.set_state(Register.referral)
        await message.answer('Если у вас есть никнейм друга, который вас пригласил - укажите его сейчас.\n'
                             '❗Если нет, просто напишите "нет".')

@router.message(Register.referral)
async def reg_referral(message: Message, state: FSMContext):
    referral_nickname = message.text
    if referral_nickname.lower() == 'нет':
        referral_nickname = 'нет'
    else:
        async with async_session() as session:
            ref_user = await session.scalar(select(User).where(User.name == referral_nickname))
            if not ref_user:
                await message.answer('🚫 Указанный никнейм не существует. Пожалуйста, попробуйте ещё раз или напишите "нет".')
                return
            else:
                ref_user.invited_count += 1
                ref_user.balls += 20
                session.add(ref_user)
                await session.commit()
                await message.answer(f'🎉 Вы указали партнёра {referral_nickname}, и ему начислены бонусы!')

    await state.update_data(referral_nickname=referral_nickname)
    await state.set_state(Register.number)
    await message.answer(
        '📱 Пожалуйста, отправь свой номер телефона для регистрации. Это поможет нам создать твою учетную запись. Спасибо!',
        reply_markup=kb.get_number)


'''@router.message(Register.whu)
async def reg_whu(message: Message, state: FSMContext):
    if message.text != 'Учитель' and message.text != 'Ученик':
        await message.answer('Выберите один из предложенных выриантов')
    else:
        await state.update_data(whu = message.text)
        await state.set_state(Register.number)
        await message.answer('📱 Пожалуйста, отправь свой номер телефона для регистрации. Это поможет нам создать твою учетную запись. Спасибо!', reply_markup=kb.get_number)
'''
@router.message(Register.number, F.contact)
async def reg_number(message: Message, state: FSMContext):

    await state.update_data(number=message.contact.phone_number)
    data = await state.get_data()
    global last_message
    last_message = await message.answer(f'🎉 Поздравляю! Регистрация успешно завершена. Теперь ты готов начать решать интересные задачи! Удачи!'
                                        f'',reply_markup=kb.main)
    cursor.execute(
        "INSERT INTO users (tg_id, name, age, count_otvet, number, premium, balls, solved_tasks, balance, count_otvet_x, balls_x, level, referral_nickname, invited_count, ban_time) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
        (data['tg_id'], data['login'], data['age'], 6, data['number'], 0, 0, 0, 0, 0, 0, 0,
         data.get('referral_nickname'), 0,0)
    )
    conn.commit()

    await state.clear()

@router.message(F.text == 'Личный кабинет')
async def lk(message: Message):
    user_id = message.from_user.id
    if any(user_id in pair for pair in active_games.keys()):
        await message.answer("⛔Вы не можете использовать другие команды во время соревнования⛔")
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
        new_message = await message.answer('Ого! Кажется, ты еще не в нашей команде!\n😉 Чтобы начать пользоваться ботом, тебе нужно пройти быструю регистрацию. \nЗаймёт всего минуту! 🚀\n/register')
    else:
        new_message = await message.answer('Вы в личном кабинете', reply_markup=kb.lk)
    user_messages[user_id] = [message.message_id, new_message.message_id]


@router.message(F.text == 'Ежедневные задания')
async def daily_tasks(message: Message):
    user_id = message.from_user.id
    if any(user_id in pair for pair in active_games.keys()):
        await message.answer("⛔Вы не можете использовать другие команды во время соревнования⛔")
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
        new_message = await message.answer('Ого❗️ Кажется, ты еще не в нашей команде❗️\n😉 Чтобы начать пользоваться ботом, тебе нужно пройти быструю регистрацию.\n Займёт всего минуту! 🚀\n/register')
    else:
        new_message = await message.answer('Выберите пункт', reply_markup=kb.zd)
    user_messages[user_id] = [message.message_id, new_message.message_id]


@router.message(F.text == 'Решать задачи')
async def daily_tasks_one(message: Message):
    user_id = message.from_user.id
    if any(user_id in pair for pair in active_games.keys()):
        await message.answer("⛔Вы не можете использовать другие команды во время соревнования⛔")
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

        new_message = await message.answer(f'🎯 Выберите предмет 🎯', reply_markup=await kb.materialcategorii())
    else:
        new_message = await message.answer(
            '🚫 Ваши попытки закончились 🚫\nПодождите немого для восстановления жизней\nЕсли хотите решать задачи без ограничений вы можете оформить подписку 😊',
            reply_markup=await kb.glavn())
    user_messages[user_id] = [message.message_id, new_message.message_id]


@router.callback_query(F.data.startswith('category_'))
async def maretialcotegori(callback: CallbackQuery):
    await callback.answer(f'Вы выбрали предмет')


    await callback.message.edit_text(
        "Выберите номер", reply_markup = await kb.materials(callback.data.split('_')[1]))


@router.callback_query(F.data.startswith('material_'))
async def materialcotegori(callback: CallbackQuery, state: FSMContext):
    user_id = callback.message.from_user.id
    data = await state.get_data()
    material_data = await rq.get_material(callback.data.split('_')[1])
    if material_data.materialcat == 2 and material_data.name == 'Номер 1-5':
        file_data = await rq.get_photo(callback.data.split('_')[1])
        file_data2 = await rq.get_photo(callback.data.split('_')[1])

        await state.update_data(number=material_data.materialcat)
        rand_file = []

        for file in file_data:
            rand_file.append((file.photo, file.answer, file.id))

        if len(rand_file) == 0:
            await callback.answer("🚫 Заданий нет для выбранного номера и категории 🚫")
            return
        if user_id in user_messages:
            for msg_id in user_messages[user_id]:
                try:
                    await callback.message.bot.delete_message(chat_id=callback.message.chat.id, message_id=msg_id)
                except Exception:
                    pass
            user_messages[user_id] = []
        await callback.message.delete()

        random_file = random.choice(rand_file)
        await state.update_data(vanswer=random_file[1])
        id_num = random_file[2]
        await state.set_state(Otvetil.answer)
        await callback.message.answer(f'Вы выбрали: {material_data.name} ✅\n'
                                      f'#{id_num} {material_data.description}\nВаше задание:',
                                      reply_markup=types.ReplyKeyboardRemove())
        await callback.message.answer_document(document=random_file[0])
        await callback.message.answer('Введите ответ:')
    else:
        photo_data = await rq.get_photo(callback.data.split('_')[1])
        photo_data2 = await rq.get_photo(callback.data.split('_')[1])
        await state.update_data(number=material_data.materialcat)
        rand_photo = []


        for photo in photo_data:
            rand_photo.append(photo.photo)

        if len(rand_photo) == 0:
            await callback.answer("🚫Заданий нет для выбранного номера и категории 🚫")
            return
        if user_id in user_messages:
            for msg_id in user_messages[user_id]:
                try:
                    await callback.message.bot.delete_message(chat_id=callback.message.chat.id, message_id=msg_id)
                except Exception:
                    pass
            user_messages[user_id] = []
        await callback.message.delete()
        randomphoto = random.choice(rand_photo)
        await callback.message.answer_photo(photo=randomphoto)
        for i in photo_data2:
            if randomphoto == i.photo:
                await state.update_data(vanswer=i.answer)
                id_num = i.id

        await state.set_state(Otvetil.answer)
        await callback.message.answer(f'Вы выбрали: {material_data.name} ✅\n'
                                      f'#{id_num} {material_data.description}\nВаше задание:',
                                      reply_markup=types.ReplyKeyboardRemove())
        await callback.message.answer('Введите ответ:')

@router.message(Otvetil.answer)
async def his_answer(message: Message, state: FSMContext):
    cursor.execute("SELECT count_otvet FROM users WHERE tg_id = ?", (message.from_user.id,))
    result = cursor.fetchone()
    count_otvet = float(result[0]) if result else 0
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
    await state.update_data(answer=message.text)
    data = await state.get_data()
    if data['vanswer'] == data['answer'] and count_otvet > 1:
        # Обновление при правильном ответе
        cursor.execute("SELECT balls, solved_tasks, balls_x FROM users WHERE tg_id = ?", (user_id,))
        result = cursor.fetchone()
        your_balls = int(result[2]) if result else 0
        solved_tasks = int(result[1]) if result else 0
        balls = float(result[0])
        solved_tasks += 1
        if your_balls > 0:
            balls += your_balls
        else:
            your_balls = 1
            balls += 1
        cursor.execute("UPDATE users SET balls = ?, solved_tasks = ? WHERE tg_id = ?", (balls, solved_tasks, user_id))
        conn.commit()

        new_message = await message.answer(
            f'🎉 Отлично! Верный ответ! 🎉\nВы получаете {your_balls}! Продолжайте в том же духе❗️',
            reply_markup=await kb.materials(data['number'])
        )
        user_messages[user_id] = [message.message_id, new_message.message_id]
        await state.clear()
    elif data['vanswer'] != data['answer'] and count_otvet > 1:
        cursor.execute("UPDATE users SET count_otvet = count_otvet - 1 WHERE tg_id = ?", (user_id,))
        conn.commit()
        new_message = await message.answer(
            f'😿 Упс! Ответ неверный. 😿\nУ вас осталось {count_otvet - 1} попыток. Не отчаивайтесь и пробуйте снова❗️',
            reply_markup=await kb.materials(data['number'])
        )
        user_messages[user_id] = [message.message_id, new_message.message_id]
        await state.clear()
        if user_id not in active_timers:
            active_timers[user_id] = asyncio.create_task(start_timer_for_attempts(user_id))
    else:
        cursor.execute("UPDATE users SET count_otvet = 0 WHERE tg_id = ?", (user_id,))
        conn.commit()

        new_message = await message.answer(
            '😿 Ответ не верный 😿\n'
            '🚫 Ваши попытки закончились.\nПодождите немого для востановления жизней\nЕсли хотите решать задачи без ограничений вы можете оформить подписку 😊',
            reply_markup=await kb.glavn()
        )
        user_messages[user_id] = [message.message_id, new_message.message_id]
        await state.clear()
        if user_id not in active_timers:
            active_timers[user_id] = asyncio.create_task(start_timer_for_attempts(user_id))

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
    await callback.answer('🕎 Вы перешли в главное меню 🕎')
    new_message = await callback.message.answer('🕎 Вы перешли в главное меню 🕎', reply_markup= kb.main)
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
    new_message = await message.answer('🕎 Вы перешли в главное меню 🕎', reply_markup= kb.main)
    user_messages[user_id] = [message.message_id, new_message.message_id]


@router.message(F.text == 'Поддержка и предложения 🤝')
async def support(message: Message,state: FSMContext):
    user_id = message.from_user.id
    if any(user_id in pair for pair in active_games.keys()):
        await message.answer("⛔ Вы не можете использовать другие команды во время соревнования ⛔")
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
        new_message = await message.answer('Ого❗️ Кажется, ты еще не в нашей команде❗️\n😉 Чтобы начать пользоваться ботом, тебе нужно пройти быструю регистрацию. Займёт всего минуту 🚀\n/register')
    else:
        new_message = await message.answer('💬 Пожалуйста, расскажите нам о вашей проблеме или предложении в одном сообщении.\nМы рады помочь и ценим ваш отзыв❗️')

        await state.set_state(Support.ansversupport)
    user_messages[user_id] = [new_message.message_id]


@router.message(Support.ansversupport)
async def supportansver(message: Message,state: FSMContext):
    await state.update_data(ansversupport=message.text)
    data = await state.get_data()
    await message.forward(supports_canal)
    await message.answer(
        f'Ваше сообщение:\n{data['ansversupport']}\n👤 Наш модератор вскоре свяжется с вами, чтобы помочь решить вашу проблему.\nСпасибо за ваше терпение 🤝'
        f'\n(Если вы хотите получить ответ лично, пожалуйста разрешите писать вам другим пользователям в телеграмме.')
    await state.clear()

@router.message(F.text == 'Таблица лидеров')
async def support(message: Message):
    user_id = message.from_user.id
    if any(user_id in pair for pair in active_games.keys()):
        await message.answer("💢 Вы не можете использовать другие команды во время соревнования 💢")
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
        new_message = await message.answer('Ого❗️ Кажется, ты еще не в нашей команде❗️\n😉 Чтобы начать пользоваться ботом, тебе нужно пройти быструю регистрацию. Займёт всего минуту❗️ 🚀\n/register')
    else:
        top_balls_user = await get_liders()
        msg = ''
        max_users_balls = 10
        id_count = 0
        for name_user, balls_usser in top_balls_user:
            id_count += 1
            if id_count <= max_users_balls:
                if id_count == 1:
                    msg += f'🥇 👤{name_user} -- {balls_usser} 🪙\n'
                elif id_count == 2:
                    msg += f'🥈 👤{name_user} -- {balls_usser} 🪙\n'
                elif id_count == 3:
                    msg += f'🥉 👤{name_user} -- {balls_usser} 🪙\n'
                elif id_count >= 4:
                    msg += f'№{id_count}) 👤{name_user} -- {balls_usser} 🪙\n'

            else:
                break
        new_message = await message.answer(f'Топ 10 пользователей:\n{msg}', reply_markup= kb.main)
    user_messages[user_id] = [message.message_id, new_message.message_id]

@router.message(F.text == 'Статистика')
async def stats(message: Message):
    user_id = message.from_user.id
    if any(user_id in pair for pair in active_games.keys()):
        await message.answer("💢 Вы не можете использовать другие команды во время соревнования 💢")
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
            new_message = await message.answer(
                'Ого❗️ Кажется, ты еще не в нашей команде❗️\n😉 Чтобы начать пользоваться ботом, тебе нужно пройти быструю регистрацию. \n Займёт всего минуту 🚀\n/register')
        else:
            cursor.execute("SELECT name, age, number, premium, balls, solved_tasks,level, count_otvet_x, balls_x, balance FROM users WHERE tg_id = ?",
                           (message.from_user.id,))
            result = cursor.fetchone()
            name = str(result[0])
            age = int(result[1])
            number = int(result[2])
            premium = int(result[3])
            balls = int(result[4])
            solved_tasks = int(result[5])
            level = str(result[6])
            count_otvet_x = str(result[7])
            balls_x = str(result[8])
            balance = str(result[9])
            conn.commit()
            your_premium = ''
            if premium == 0:
                your_premium = '🚫 Подписка не активирована.'
            elif premium == 1:
                your_premium = 'Подиска активна'
            new_message = await message.answer(f'Никнейм: {name}\n'
                                 f'Возраст: {age}\n'
                                 f'Телефон: {number}\n'
                                 f'Количество решенных задач: {solved_tasks}\n'
                                 f'Количество 🪙: {balls}\n'
                                 f'Уровень: {level}\n'
                                 f'X к востановлению жизни: {count_otvet_x}\n'
                                 f'X к увеличению 🪙: {balls_x}\n'
                                 f'Баланс: {balance}\n'
                                 f'{your_premium}', reply_markup=kb.lk)
        user_messages[user_id] = [message.message_id, new_message.message_id]


@router.message(Command('pay'))
async def send_payment_options(message: types.Message):
    user_id = message.from_user.id

    if any(user_id in pair for pair in active_games.keys()):
        await message.answer("💢 Вы не можете использовать другие команды во время соревнования 💢")
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
        new_message = await message.answer(
            'Ого❗️ Кажется, ты еще не в нашей команде❗️\n😉 Чтобы начать пользоваться ботом, тебе нужно пройти быструю регистрацию. \nЗаймёт всего минуту 🚀\n/register')
    else:
        new_message = await message.answer("Выберите сумму для пополнения:", reply_markup=kb.donat)
    user_messages[user_id] = [message.message_id, new_message.message_id]

@router.message(F.text == '💲')
async def send_payment_options(message: types.Message):
    user_id = message.from_user.id
    if any(user_id in pair for pair in active_games.keys()):
        await message.answer("💢 Вы не можете использовать другие команды во время соревнования 💢")
        return
    await message.delete()
    if user_id in user_messages:
        for msg_id in user_messages[user_id]:
            try:
                await message.bot.delete_message(chat_id=message.chat.id, message_id=msg_id)
            except Exception:
                pass
        user_messages[user_id] = []
    new_message = await message.answer("💳 Выберите сумму для пополнения 💳", reply_markup=kb.donat)
    user_messages[user_id] = [message.message_id, new_message.message_id]


@router.callback_query(lambda callback: callback.data.startswith("pay_"))
async def send_invoice(callback: types.CallbackQuery):
    try:
        # Получаем сумму из callback.data
        amount1 = int(callback.data.split("_")[1])
        print(f"Сумма для пополнения: {amount1}")

        # Проверяем, чтобы сумма была корректной
        if amount1 <= 0:
            await callback.answer("Сумма должна быть больше 0️⃣❕", show_alert=True)
            return

        # Подготовка цены в копейках
        prices = [
            LabeledPrice(label=f"Пополнение баланса ({amount1} руб)", amount=amount1 * 100)
        ]
        print(prices)
        # Удаляем предыдущее сообщение и отправляем invoice
        await callback.message.delete()
        await bot.send_invoice(
            chat_id=callback.message.chat.id,
            title="Пополнение баланса",
            description=f"Пополнение на {amount1} руб",
            payload=f"user_{callback.from_user.id}_{amount1}",  # Уникальный payload
            provider_token=PAYMENT_PROVIDER_TOKEN,  # Токен Юкассы
            currency="RUB",  # Валюта в формате ISO 4217
            prices=prices,
            start_parameter="pay",
        )
        await callback.answer()
    except Exception as e:
        print(f"Ошибка при отправке счета: {e}")
        await callback.answer("Не удалось создать счет. Попробуйте позже.", show_alert=True)

@router.pre_checkout_query()
async def process_pre_checkout_query(pre_checkout_query: PreCheckoutQuery):
    await bot.answer_pre_checkout_query(pre_checkout_query.id, ok=True)

@router.message(F.content_type == ContentType.SUCCESSFUL_PAYMENT)
async def successful_payment(message: types.Message):
    payment_info = message.successful_payment
    amount = payment_info.total_amount / 100
    if amount == 99:
        cursor.execute(
            "SELECT premium FROM users WHERE tg_id = ?",
            (message.from_user.id,))
        result = cursor.fetchone()
        premium_user = int(result[0])
        if premium_user == 0:
            cursor.execute("UPDATE users SET premium = 1 WHERE tg_id = ?",
                           (message.from_user.id,))
            conn.commit()
            # Планировщик задачи на обнуление премиума через 30 дней
            scheduler = AsyncIOScheduler()
            reset_time = datetime.now() + timedelta(days=30)
            scheduler.add_job(
                reset_premium,
                trigger=DateTrigger(run_date=reset_time),
                kwargs={"user_id": message.from_user.id},
            )
            scheduler.start()

            await message.answer(
                "🎉 Подписка оформлена  🎉\n❗Вы получили премиум на 1 месяц. Спасибо за поддержку❗"
            )
        else:
            cursor.execute("UPDATE users SET balance = balance + 99 WHERE tg_id = ?",
                           (message.from_user.id,))
            conn.commit()
            await message.answer(
                "У вас уже есть подписка, деньги зачислены вам на баланс 💲"
            )
    else:



        cursor.execute("UPDATE users SET balance = balance + ? WHERE tg_id = ?",
                       (amount, message.from_user.id,))
        conn.commit()
        await message.answer(f" 🎉 Оплата успешно проведена 🎉\nВаш баланс пополнен на {amount} руб. \nСпасибо за использование наших услуг❗")


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
        await message.answer("💢 Вы не можете использовать другие команды во время соревнования 💢")
        return

    await message.delete()

    new_message = await message.answer("Выберите количество жизней:", reply_markup=kb.donat_life)

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
        required_balance = {1: 9, 3: 19, 6: 28, 9: 35}.get(amount)

        if required_balance is None:
            await callback.answer("Ошибка: неверная сумма.", show_alert=True)
            return

        if balance >= required_balance:
            balance -= required_balance
            cursor.execute("UPDATE users SET balance = ?, count_otvet = count_otvet + ? WHERE tg_id = ?",
                           (balance, amount, callback.from_user.id,))
            conn.commit()
            await callback.answer(f"🎉 Оплата прошла успешно 🎉\nС вашего баланса списано {required_balance} руб.", show_alert=True)
        else:
            await callback.answer(f"❌ Недостаточно средств на балансе.\nНеобходимо {required_balance} руб.\nЧтобы пополнить баланс, воспользуйтесь командой\n/pay.", show_alert=True)
    except Exception as e:
        await callback.answer(f"Произошла ошибка: {e}", show_alert=True)

@router.message(F.text == 'Изменить способности')
async def ability(message: Message):
    user_id = message.from_user.id
    if any(user_id in pair for pair in active_games.keys()):
        await message.answer("💢 Вы не можете использовать другие команды во время соревнования 💢")
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
    new_message = await message.answer(f'Ваши характеристики:\n'
                                 f'\nКоличество жизней: {count_otvet}\n'
                                 f'Бонус к восстановлению жизни: {count_otvet_x}\n'
                                 f'Бонус к увеличению 🪙:{balls_x}\n'
                                 f'\nКоличество 🪙:{balls}'
                                 f'\nБаланс: {balance}\n'
                                 f'\nВыберите, что улучшить:\n'
                                 f'1. Восстановление жизни: Увеличьте количество жизней!\n'
                                 f'2. Увеличение 🪙: Получайте больше 🪙 за правильные ответы!\n\nВаш выбор?', reply_markup=kb.ability)
    user_messages[user_id] = [message.message_id, new_message.message_id]
    conn.commit()

@router.message(F.text == 'X к увеличению 🪙')
async def ability(message: Message,state: FSMContext):
    user_id = message.from_user.id
    if any(user_id in pair for pair in active_games.keys()):
        await message.answer("💢 Вы не можете использовать другие команды во время соревнования 💢")
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
        balls_x = float(result[0])
        upgrade_costs_balls = {
            0: (45, 1.2),
            1.2: (75, 1.4),
            1.4: (145, 1.8),
            1.8: (225, 2.0),
        }
        next_level_cost_balls, next_level_value_balls = upgrade_costs_balls.get(float(balls_x),
                                                              (0, 0))
        upgrade_costs_pay = {
            0: (9, 1.2),
            1.2: (15, 1.4),
            1.4: (29, 1.8),
            1.8: (45, 2.0),
        }
        next_level_cost_pay, next_level_value_pay = upgrade_costs_pay.get(float(balls_x),
                                                                                (0, 0))
        if next_level_cost_balls <= 0:
            new_message = await message.answer(
                f'На данный момент ваш X {balls_x} к востановлению 🪙\n'
                f'Вы достигли максимального уровня!\n',
                reply_markup=kb.pump)
        else:
            new_message = await message.answer(
                f'На данный момент у вас X {balls_x} к востановлению 🪙'
                f'\nСледующее улучшение: {next_level_value_pay}'
                f'\nСтоимость следующего улучшения за 🪙: {next_level_cost_balls}'
                f'\nСтоимость следующего улучшения за 💲: {next_level_cost_pay}'
                f'\n💳 Выберите валюту, за которую хотите улучшить способность.\n⚠️ Внимание: после выбора ваши 🪙 (донат рубли) будут немедленно списаны с баланса!',
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
        0: (45, 1.2),
        1.2: (75, 1.4),
        1.4: (145, 1.8),
        1.8: (225, 2.0),
    }
    next_level_cost_balls, next_level_value_balls = upgrade_costs_balls.get(float(balls_x),
                                                                            (0, 0))
    upgrade_costs_pay = {
        0: (9, 1.2),
        1.2: (15, 1.4),
        1.4: (29, 1.8),
        1.8: (45, 2.0),
    }
    next_level_cost_pay, next_level_value_pay = upgrade_costs_pay.get(float(balls_x),
                                                                      (0, 0))

    if message.text == 'За 🪙':
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
                f"Вы увеличили X к востановлению 🪙!\n"
                f"Теперь вы будете получать за каждый ответ {balls_x} 🪙.\n"
                f"Оставшиеся 🪙: {balls}", reply_markup=kb.ability
            )
        else:
            new_message = await message.answer(
                f"Недостаточно 🪙 для улучшения. У вас {balls} 🪙. "
                f"Стоимость следующего улучшения: {next_level_cost_balls} 🪙." if next_level_cost_balls > 0 else "🎯 Вы достигли максимального уровня! Поздравляем!\nДальше вас ждут новые возможности и достижения. 😊",
                reply_markup=kb.ability
            )
        user_messages[user_id] = [message.message_id, new_message.message_id]
        await state.clear()


    if message.text == 'За 💲':
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
                f"Вы увеличили X к восстановлению 🪙!\n"
                f"Теперь вы будете получать за каждый ответ {balls_x} 🪙.\n"
                f"Оставшийся баланс: {balance}", reply_markup=kb.ability
            )
        else:
            new_message = await message.answer(
                f"Недостаточно денег для улучшения. У вас {balance} рублей. "
                f"Стоимость следующей улучшения: {next_level_cost_pay} 🪙." if next_level_cost_pay > 0 else "🎯 Вы достигли максимального уровня! Поздравляем!\nДальше вас ждут новые возможности и достижения. 😊",
                reply_markup=kb.ability
            )
        user_messages[user_id] = [message.message_id, new_message.message_id]
        await state.clear()



@router.message(F.text == 'X к восстановлению жизни')
async def restoration_of_life(message: Message,state: FSMContext):
    user_id = message.from_user.id
    if any(user_id in pair for pair in active_games.keys()):
        await message.answer("💢 Вы не можете использовать другие команды во время соревнования 💢")
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
            0: (25, 1.25),
            1.25: (45, 1.5),
            1.5: (99, 2.0),
            2.0: (135, 2.5),
            2.5: (160, 3.0),

        }
        next_level_cost_balls1, next_level_value_balls1 = upgrade_costs_balls1.get(float(count_otvet_x),
                                                                                (0, 0))
        upgrade_costs_pay1 = {
            0: (9, 1.25),
            1.25: (15, 1.5),
            1.5: (29, 2.0),
            2.0: (35, 2.5),
            2.5: (51, 3.0),
        }
        next_level_cost_pay1, next_level_value_pay1 = upgrade_costs_pay1.get(float(count_otvet_x),
                                                                          (0, 0))
        if next_level_cost_balls1 <= 0:
            new_message = await message.answer(
                f'На данный момент у вас X {count_otvet_x} к востановлению 🪙\n'
                f'Это максимальный уровень\n',
                reply_markup=kb.pump)
        else:
            new_message = await message.answer(
                f'На данный момент у вас X {count_otvet_x} к востановлению жизней'
                f'\nСледующее улучшение: {next_level_value_pay1}'
                f'\nСтоимость следующего улучшения за 🪙: {next_level_cost_balls1}'
                f'\nСтоимость следующего улучшения за $: {next_level_cost_pay1}'
                f'\n💳 Выберите валюту, за которую хотите улучшить способность.\n⚠️ Внимание: после выбора ваши 🪙 (донат рубли) будут немедленно списаны с баланса!',
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
        0: (25, 1.25),
        1.25: (45, 1.5),
        1.5: (99, 2.0),
        2.0: (135, 2.5),
        2.5: (160, 3.0),
    }
    next_level_cost_balls1, next_level_value_balls1 = upgrade_costs_balls1.get(count_otvet_x,
                                                                            (0, 0))

    upgrade_costs_pay1 = {
        0: (9, 1.25),
        1.25: (15, 1.5),
        1.5: (29, 2.0),
        2.0: (35, 2.5),
        2.5: (51, 3.0),
    }
    next_level_cost_pay1, next_level_value_pay1 = upgrade_costs_pay1.get(count_otvet_x,
                                                                      (0, 0))
    if message.text == 'За 🪙':

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
                f"Вы повысили X к восстановлению жизни!\n"
                f"Теперь вы  получаете за каждый ответ {count_otvet_x} 🪙.\n"
                f"Оставшиеся 🪙: {balls}", reply_markup=kb.ability
            )
        else:
            new_message = await message.answer(
                f"Недостаточно 🪙 для улучшения. У вас {balls} 🪙. "
                f"Стоимость следующей улучшения: {next_level_cost_balls1} 🪙." if next_level_cost_balls1 > 0 else f"🎯 Вы достигли максимального уровня! Поздравляем!\nДальше вас ждут новые возможности и достижения. 😊", reply_markup=kb.ability
            )
        user_messages[user_id] = [message.message_id, new_message.message_id]
        await state.clear()

    if message.text == 'За $':
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
                f"Вы увеличили X к восстановлению 🪙!\n"
                f"Теперь вы  получаете за каждый ответ {count_otvet_x} 🪙.\n"
                f"Оставшийся баланс: {balance}", reply_markup=kb.ability
            )
        else:
            new_message = await message.answer(
                f"Недостаточно $ для улучшения. У вас {balance} рублей. "
                f"Стоимость следующего улучшения: {next_level_cost_pay1} 🪙." if next_level_cost_pay1 > 0 else "🎯 Вы достигли максимального уровня! Поздравляем!\nДальше вас ждут новые возможности и достижения. 😊",
                reply_markup=kb.ability
            )
        user_messages[user_id] = [message.message_id, new_message.message_id]
        await state.clear()



async def check_premium_arena(user_id):
    cursor.execute("SELECT premium, count_otvet FROM users WHERE tg_id = ?",
                   (user_id,))
    result = cursor.fetchone()
    premium = int(result[0])
    count_otvet = float(result[1])
    conn.commit()
    if premium == 1:
        return 1
    if count_otvet >= 2.0 and premium == 0:
        return 2
    else:
        return 0


waiting_queue = {}
active_games = {}
active_players = set()

@router.message(F.text == 'Арена')
async def arena(message: Message):
    user_id = message.from_user.id
    await message.delete()

    if user_id in active_players:
        await message.answer("💢 Вы не можете использовать другие команды во время соревнования 💢")
        return

    if user_id in user_messages:
        for msg_id in user_messages[user_id]:
            try:
                await message.bot.delete_message(chat_id=message.chat.id, message_id=msg_id)
            except Exception:
                pass
        user_messages[user_id] = []

    if await check_premium_arena(user_id) == 2:
        new_message = await message.answer(
            f'Выберите категорию материала',
            reply_markup=await kb.arenacatalog())
        cursor.execute("UPDATE users SET count_otvet = count_otvet - 2 WHERE tg_id = ?", (message.from_user.id,))
        conn.commit()
    elif await check_premium_arena(user_id) == 1:
        new_message = await message.answer(f'Выберите категорию материала', reply_markup=await kb.arenacatalog())
    else:
        new_message = await message.answer(
            f'🚫 У вас закончились попытки.\nЧтобы получить неограниченный доступ к арене, вы можете оформить подписку.',
            reply_markup=kb.main)
    user_messages[user_id] = [message.message_id, new_message.message_id]

@router.callback_query(F.data.startswith('arenacategory_'))
async def select_category(callback: CallbackQuery):
    user_id = callback.from_user.id
    category = callback.data.split('_')[1]

    if user_id in waiting_queue.get(category, []):
        await callback.message.answer("Вы не можете соревноваться с самим собой 🤔")
        print(waiting_queue.get(category, []))
        return

    if category not in waiting_queue:
        waiting_queue[category] = []

    if waiting_queue[category]:
        opponent_id = waiting_queue[category].pop(0)

        if (user_id, opponent_id) in active_games or (opponent_id, user_id) in active_games:
            await callback.message.answer("Ошибка: соперник уже находится в другой игре.")
            return

        active_games[(user_id, opponent_id)] = {
            "category": category,
            "tasks": [],
            "scores": {user_id: 0, opponent_id: 0},
        }
        active_players.add(user_id)
        active_players.add(opponent_id)

        await bot.send_message(user_id, f'🏆 Соперник найден!\nСоревнование начинается! Удачи!', reply_markup=kb.leave)
        await bot.send_message(opponent_id, f'🏆 Соперник найден!\nСоревнование начинается! Удачи!', reply_markup=kb.leave)
        await send_task(user_id, opponent_id, category)
    else:
        waiting_queue[category].append(user_id)
        await callback.message.edit_text(
            "⏳ Ищем для вас подходящего соперника...", reply_markup=await kb.leave_arena())

@router.message(F.text == 'Покинуть соревнование')
async def leave_competition(message: Message):
    user_id = message.from_user.id

    if user_id in active_players:
        game_to_exit = next(((user1, user2) for (user1, user2) in active_games if user_id in (user1, user2)), None)

        if game_to_exit:
            user1_id, user2_id = game_to_exit
            del active_games[game_to_exit]

            await message.answer("⛓️‍💥Вы вышли из игры.⛓️‍💥\nВам сняли 5 баллов", reply_markup=kb.main)
            cursor.execute("UPDATE users SET balls = balls - 5 WHERE tg_id = ?", (user_id,))
            opponent_id = user2_id if user_id == user1_id else user1_id
            await bot.send_message(opponent_id, "👤 Ваш соперник покинул игру.\n⛓️‍💥Игра завершена.⛓️‍💥", reply_markup=kb.main)

            active_players.discard(user1_id)
            active_players.discard(user2_id)
        else:
            await message.answer("❗️ Вы не участвуете в игре ❗️")
    else:
        await message.answer("❗️ Вы не находитесь в соревновании ❗️")

async def send_task(user1_id, user2_id, category):
    task = get_random_task(category)
    if not task:
        return
    active_games[(user1_id, user2_id)]["tasks"].append(task)
    try:
        await bot.send_photo(user1_id, task['question'], caption=f"#{task['id']} Ваша задача:")
        await bot.send_photo(user2_id, task['question'], caption=f"#{task['id']} Ваша задача:")
    except Exception as e:
        pass

def get_random_task(category):
    cursor.execute("SELECT id, photo, answer FROM photos WHERE materialcat = ? ORDER BY RANDOM() LIMIT 1;", (category,))
    result = cursor.fetchone()
    if result:
        return {"id": result[0], "question": result[1], "answer": result[2]}
    return None

@router.callback_query(F.data.startswith('leave_arena'))
async def leave_arena(callback: CallbackQuery):
    user_id = callback.from_user.id
    await callback.message.delete()
    removed = False
    for category, queue in waiting_queue.items():
        if user_id in queue:
            queue.remove(user_id)
            removed = True
            break

    if user_id in user_messages:
        for msg_id in user_messages[user_id]:
            try:
                await callback.message.bot.delete_message(chat_id=callback.message.chat.id, message_id=msg_id)
            except Exception as e:
                pass
        user_messages[user_id] = []

    new_message = await callback.message.answer('🚷 Поиск соперника прекращен 🚷', reply_markup=kb.zd)
    user_messages[user_id] = [callback.message.message_id, new_message.message_id]

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
            cursor.execute("UPDATE users SET solved_tasks = solved_tasks + 1 WHERE tg_id = ?", (user_id,))
            conn.commit()
            await message.answer("🎉 Верно! Вы получили 1 балл.")
            await bot.send_message(opponent_id, "Ваш соперник ответил правильно.")
            if len(game_data["tasks"]) >= 3:
                winner_id = max(game_data["scores"], key=game_data["scores"].get)
                cursor.execute("SELECT name FROM users WHERE tg_id = ?", (winner_id,))
                result = cursor.fetchone()
                name = str(result[0])
                scores = game_data["scores"]
                await bot.send_message(user1_id, f"Игра окончена! Победитель: {name}\nВерных ответов:{scores[winner_id]}.",reply_markup=await kb.main())
                await bot.send_message(user2_id, f"Игра окончена! Победитель: {name}\nВерных ответов:{scores[winner_id]}.",reply_markup=await kb.main())
                active_players.remove(user1_id)
                active_players.remove(user2_id)
                del active_games[(user1_id, user2_id)]
            else:
                await send_task(user1_id, user2_id, game_data["category"])
        else:
            await message.answer("Ответ неверный")
    else:
        await message.answer("Вы не можете отправлять сообщения во время соревнования.")

@router.message(F.text == "Поиск Учителя/Ученика")
async def profiles(message: types.Message):
    user_id = message.from_user.id
    if user_id in user_messages:
        for msg_id in user_messages[user_id]:
            try:
                await message.bot.delete_message(chat_id=message.chat.id, message_id=msg_id)
            except Exception:
                pass
        user_messages[user_id] = []
    new_message = await message.answer('Выберите один из пунктов 🖍', reply_markup=kb.form)
    user_messages[user_id] = [message.message_id, new_message.message_id]


class ProfileState(StatesGroup):
    waiting_for_name = State()
    waiting_for_name_tg = State()
    waiting_for_role = State()  # Ученик или учитель
    waiting_for_subject = State()  # Предмет подготовки
    waiting_for_description = State()
    waiting_for_photo = State()
    editing_profile = State()
    editing_name = State()
    editing_role = State()
    editing_description = State()
    editing_subject = State()
    editing_photo = State()

@router.message(F.text == "Моя анкета")
async def start_profile_creation(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    if user_id in user_messages:
        for msg_id in user_messages[user_id]:
            try:
                await message.bot.delete_message(chat_id=message.chat.id, message_id=msg_id)
            except Exception:
                pass
        user_messages[user_id] = []
    cursor.execute("SELECT * FROM profile_form WHERE user_id = ?", (user_id,))
    result = cursor.fetchone()

    if result:
        cursor.execute("""
                        SELECT id, name, role, subject, description, photo_id, likes, dislikes, is_active
                        FROM profile_form
                        WHERE user_id == ? 
                    """,(user_id,))
        profile = cursor.fetchone()
        conn.commit()
        if not profile:
            new_message = await message.answer("Произошла ошибка")
            return
        profile_id, name, role, subject, description, photo_id, likes, dislikes, is_active = profile
        status = "Анкета активна" if is_active == 1 else "Анкета не активна"
        text = (
            f"Ваша анкета:\n"
            f"👤 *{name}* ({role})\n"
            f"📚 Предмет: {subject}\n"
            f"ℹ Описание: {description}\n"
            f"❤️ Лайков: {likes}\n"
            f"💔 Дизлайков: {dislikes}\n"
            f"{status}"
        )

        new_message = await message.answer_photo(
            photo=photo_id,
            caption=text,
            reply_markup=kb.form_menu,
            parse_mode="Markdown"
        )



    else:
        new_message = await message.answer("Давайте начнем создание вашей анкеты❗️\nВведите ваше имя:")
        await state.set_state(ProfileState.waiting_for_name)
    user_messages[user_id] = [message.message_id, new_message.message_id]

@router.message(F.text == "Редактировать анкету")
async def edit_profile(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    if user_id in user_messages:
        for msg_id in user_messages[user_id]:
            try:
                await message.bot.delete_message(chat_id=message.chat.id, message_id=msg_id)
            except Exception:
                pass
        user_messages[user_id] = []
    cursor.execute("SELECT * FROM profile_form WHERE user_id = ?", (user_id,))
    result = cursor.fetchone()

    if not result:
        await message.answer("У вас нет анкеты. Сначала создайте её❗️")
        return


    new_message = await message.answer("Что вы хотите изменить в анкете?", reply_markup=kb.form_redact)
    await state.set_state(ProfileState.editing_profile)
    user_messages[user_id] = [message.message_id, new_message.message_id]

@router.message(ProfileState.editing_profile)
async def process_edit_choice(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    if user_id in user_messages:
        for msg_id in user_messages[user_id]:
            try:
                await message.bot.delete_message(chat_id=message.chat.id, message_id=msg_id)
            except Exception:
                pass
        user_messages[user_id] = []
    if message.text == "Имя":
        new_message = await message.answer("Введите новое имя:")
        await state.set_state(ProfileState.editing_name)
    elif message.text == "Роль":
        new_message = await message.answer("Выберите новую роль:", reply_markup=kb.iam)
        await state.set_state(ProfileState.editing_role)
    elif message.text == "Описание":
        new_message = await message.answer("Введите новое описание:")
        await state.set_state(ProfileState.editing_description)
    elif message.text == "Предмет":
        new_message = await message.answer("Введите новый предмет:", reply_markup = kb.form_tasks)
        await state.set_state(ProfileState.editing_subject)
    elif message.text == "Фото":
        new_message = await message.answer("Отправьте новое фото:")
        await state.set_state(ProfileState.editing_photo)
    elif message.text == "Готово":
        new_message = await message.answer("Изменения сохранены.", reply_markup=kb.form_redact)
        await start_profile_creation(message, state)
        await state.clear()
    else:
        new_message = await message.answer("Пожалуйста, выберите один из предложенных вариантов ❗️")
    user_messages[user_id] = [message.message_id, new_message.message_id]

@router.message(ProfileState.editing_name)
async def process_edit_name(message: types.Message, state: FSMContext):
    new_name = message.text
    user_id = message.from_user.id
    if user_id in user_messages:
        for msg_id in user_messages[user_id]:
            try:
                await message.bot.delete_message(chat_id=message.chat.id, message_id=msg_id)
            except Exception:
                pass
        user_messages[user_id] = []
    cursor.execute("UPDATE profile_form SET name = ? WHERE user_id = ?", (new_name, user_id))
    conn.commit()
    new_message = await message.answer("Имя успешно обновлено.", reply_markup=kb.form_redact)
    await state.set_state(ProfileState.editing_profile)
    user_messages[user_id] = [message.message_id, new_message.message_id]


@router.message(ProfileState.editing_role)
async def process_edit_role(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    if message.text not in ["Ученик", "Учитель", "Родитель"]:
        new_message = await message.answer("Пожалуйста, выберите из предложенных вариантов: Ученик или Учитель.", reply_markup=kb.iam)
        user_messages[user_id] = [message.message_id, new_message.message_id]
        return
    else:
        new_role = message.text
        if user_id in user_messages:
            for msg_id in user_messages[user_id]:
                try:
                    await message.bot.delete_message(chat_id=message.chat.id, message_id=msg_id)
                except Exception:
                    pass
            user_messages[user_id] = []
        cursor.execute("UPDATE profile_form SET role = ? WHERE user_id = ?", (new_role, user_id))
        conn.commit()
        new_message = await message.answer("Ваша роль обновлена.", reply_markup=kb.form_redact)
        await state.set_state(ProfileState.editing_profile)
        user_messages[user_id] = [message.message_id, new_message.message_id]

@router.message(ProfileState.editing_description)
async def process_edit_description(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    new_description = message.text
    if user_id in user_messages:
        for msg_id in user_messages[user_id]:
            try:
                await message.bot.delete_message(chat_id=message.chat.id, message_id=msg_id)
            except Exception:
                pass
        user_messages[user_id] = []
    cursor.execute("UPDATE profile_form SET description = ? WHERE user_id = ?", (new_description, user_id))
    conn.commit()
    new_message = await message.answer("Описание обновлено.", reply_markup=kb.form_redact)
    await state.set_state(ProfileState.editing_profile)
    user_messages[user_id] = [message.message_id, new_message.message_id]

@router.message(ProfileState.editing_subject)
async def process_edit_subject(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    if message.text not in ['Математика Профиль/База', 'Математика ОГЭ', "Информатика", "Русский", "Биология", "Английский язык"]:
        new_message = await message.answer("Пожалуйста, выберите из предложенных вариантов.", reply_markup = kb.form_tasks)
        user_messages[user_id] = [message.message_id, new_message.message_id]
        return
    if user_id in user_messages:
        for msg_id in user_messages[user_id]:
            try:
                await message.bot.delete_message(chat_id=message.chat.id, message_id=msg_id)
            except Exception:
                pass
        user_messages[user_id] = []
    new_subject = message.text
    cursor.execute("UPDATE profile_form SET subject = ? WHERE user_id = ?", (new_subject, user_id))
    conn.commit()
    new_message = await message.answer("Выбран новый предмет", reply_markup=kb.form_redact)
    await state.set_state(ProfileState.editing_profile)
    user_messages[user_id] = [message.message_id, new_message.message_id]

@router.message(ProfileState.editing_photo)
async def process_edit_photo(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    new_photo = message.photo[-1].file_id
    if user_id in user_messages:
        for msg_id in user_messages[user_id]:
            try:
                await message.bot.delete_message(chat_id=message.chat.id, message_id=msg_id)
            except Exception:
                pass
        user_messages[user_id] = []
    cursor.execute("UPDATE profile_form SET photo_id = ? WHERE user_id = ?", (new_photo, user_id))
    conn.commit()
    new_message = await message.answer("Фото обновлено.", reply_markup=kb.form_redact)
    await state.set_state(ProfileState.editing_profile)
    user_messages[user_id] = [message.message_id, new_message.message_id]

@router.message(ProfileState.waiting_for_name)
async def process_name(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    if user_id in user_messages:
        for msg_id in user_messages[user_id]:
            try:
                await message.bot.delete_message(chat_id=message.chat.id, message_id=msg_id)
            except Exception:
                pass
        user_messages[user_id] = []
    await state.update_data(name=message.text)
    new_message = await message.answer("Выберите вашу роль:", reply_markup=kb.iam)
    await state.set_state(ProfileState.waiting_for_name_tg)
    user_messages[user_id] = [message.message_id, new_message.message_id]


@router.message(ProfileState.waiting_for_name_tg)
async def process_name(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    if user_id in user_messages:
        for msg_id in user_messages[user_id]:
            try:
                await message.bot.delete_message(chat_id=message.chat.id, message_id=msg_id)
            except Exception:
                pass
        user_messages[user_id] = []
    if message.text not in ["Ученик", "Учитель", "Родитель"]:
        new_message = await message.answer("Пожалуйста, выберите из предложенных вариантов: Ученик или Учитель.", reply_markup=kb.iam)
        user_messages[user_id] = [message.message_id, new_message.message_id]
        return
    await state.update_data(role=message.text)
    new_message = await message.answer("Отправьте имя своего профиля(чтобы с вами моги связаться)\nбез @", reply_markup=ReplyKeyboardRemove())
    await state.set_state(ProfileState.waiting_for_role)
    user_messages[user_id] = [message.message_id, new_message.message_id]

@router.message(ProfileState.waiting_for_role)
async def process_role(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    if user_id in user_messages:
        for msg_id in user_messages[user_id]:
            try:
                await message.bot.delete_message(chat_id=message.chat.id, message_id=msg_id)
            except Exception:
                pass
        user_messages[user_id] = []
    await state.update_data(name_tg=message.text)
    new_message = await message.answer("Введите предмет, по которому вы обучаетесь или готовите:", reply_markup = kb.form_tasks)
    await state.set_state(ProfileState.waiting_for_subject)
    user_messages[user_id] = [message.message_id, new_message.message_id]

@router.message(ProfileState.waiting_for_subject)
async def process_subject(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    if user_id in user_messages:
        for msg_id in user_messages[user_id]:
            try:
                await message.bot.delete_message(chat_id=message.chat.id, message_id=msg_id)
            except Exception:
                pass
        user_messages[user_id] = []
    if message.text not in ['Математика Профиль/База', 'Математика ОГЭ', "Информатика", "Русский", "Биология", "Английский язык"]:
        new_message = await message.answer("Пожалуйста, выберите из предложенных вариантов.", reply_markup = kb.form_tasks)
        user_messages[user_id] = [message.message_id, new_message.message_id]
        return
    await state.update_data(subject=message.text)
    new_message = await message.answer("Расскажите немного о себе:", reply_markup=ReplyKeyboardRemove())
    await state.set_state(ProfileState.waiting_for_description)
    user_messages[user_id] = [message.message_id, new_message.message_id]

@router.message(ProfileState.waiting_for_description)
async def process_description(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    if user_id in user_messages:
        for msg_id in user_messages[user_id]:
            try:
                await message.bot.delete_message(chat_id=message.chat.id, message_id=msg_id)
            except Exception:
                pass
        user_messages[user_id] = []
    await state.update_data(description=message.text)
    new_message = await message.answer("Теперь отправьте ваше фото:")
    await state.set_state(ProfileState.waiting_for_photo)
    user_messages[user_id] = [message.message_id, new_message.message_id]

@router.message(ProfileState.waiting_for_photo, F.photo)
async def process_photo(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    if user_id in user_messages:
        for msg_id in user_messages[user_id]:
            try:
                await message.bot.delete_message(chat_id=message.chat.id, message_id=msg_id)
            except Exception:
                pass
        user_messages[user_id] = []
    photo_id = message.photo[-1].file_id
    user_data = await state.get_data()
    user = message.from_user.id
    cursor.execute("SELECT MAX(id) FROM profile_form")
    result = cursor.fetchone()
    max_id = int(result[0]) + 1
    cursor.execute("SELECT age FROM users WHERE tg_id = ?;", (user,))
    result = cursor.fetchone()
    age = int(result[0])
    cursor.execute("""
        INSERT INTO profile_form (id, user_id, name, name_tg, role, subject, description, photo_id, age, likes, is_active) 
        VALUES (?, ?,?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (max_id, message.from_user.id, user_data['name'],user_data['name_tg'], user_data['role'], user_data['subject'], user_data['description'], photo_id, int(age), 0, 1))
    conn.commit()

    new_message = await message.answer("Анкета успешно сохранена❗️ Другие пользователи могут её просмотреть.", reply_markup=kb.form)
    await state.clear()
    user_messages[user_id] = [message.message_id, new_message.message_id]

@router.message(F.text == "Удалить анкету из поиска")
async def deactivate_profile(message: types.Message):
    user_id = message.from_user.id
    cursor.execute("SELECT * FROM profile_form WHERE user_id = ?", (user_id,))
    result = cursor.fetchone()

    if not result:
        await message.answer("У вас нет анкеты. Сначала создайте её, займёт 5 минут❗️")
        return

    cursor.execute("UPDATE profile_form SET is_active = 0 WHERE user_id = ?", (user_id,))
    conn.commit()
    await start_profile_creation(message, None)


@router.message(F.text == "Добавить анкету в поиск")
async def activate_profile(message: types.Message):
    user_id = message.from_user.id
    cursor.execute("SELECT * FROM profile_form WHERE user_id = ?", (user_id,))
    result = cursor.fetchone()

    if not result:
        await message.answer("У вас нет анкеты. Сначала создайте её❗️")
        return

    cursor.execute("UPDATE profile_form SET is_active = 1 WHERE user_id = ?", (user_id,))
    conn.commit()
    await start_profile_creation(message, None)


@router.message(F.text == "Начать поиск")
async def view_profiles(message: types.Message, state: FSMContext):
    await show_next_profile(message, message.from_user.id, state)


async def show_next_profile(message: types.Message, user_id: int, state: FSMContext = None):
    cursor.execute("SELECT role FROM profile_form WHERE user_id = ?", (user_id,))
    result = cursor.fetchone()

    if not result:
        await message.answer("Сначала создайте свою анкету, чтобы просматривать других пользователей.")
        return

    user_role = result[0]

    if user_role == "Учитель":
        query = """
            SELECT id, name, role, subject, description, photo_id, likes, dislikes
            FROM profile_form
            WHERE role IN ('Ученик', 'Родитель') AND user_id != ? AND is_active = 1
            ORDER BY RANDOM()
            LIMIT 1
        """
    elif user_role == "Ученик":
        query = """
            SELECT id, name, role, subject, description, photo_id, likes, dislikes
            FROM profile_form
            WHERE role = 'Учитель' AND user_id != ? AND is_active = 1
            ORDER BY RANDOM()
            LIMIT 1
        """
    else:
        await message.answer("Ваша роль не позволяет просматривать другие анкеты.")
        return

    cursor.execute(query, (user_id,))
    profile = cursor.fetchone()

    if not profile:
        await message.answer("Подходящих анкет больше нет.")
        return
    profile_id, name, role, subject, description, photo_id, likes, dislikes = profile

    text = (
        f"👤 *{name}* ({role})\n"
        f"📚 Предмет: {subject}\n"
        f"ℹ Описание: {description}\n"
        f"❤️ Лайков: {likes}\n"
        f"💔 Дизлайков: {dislikes}"
    )

    await message.answer_photo(
        photo=photo_id,
        caption=text,
        reply_markup=kb.get_profile_keyboard(profile_id),
        parse_mode="Markdown"
    )


@router.callback_query(F.data == "skip")
async def skip_profile(callback: CallbackQuery):
    await callback.message.delete()
    await show_next_profile(callback.message, callback.from_user.id)


@router.callback_query(F.data.startswith("like_"))
async def like_profile(callback: CallbackQuery):
    profile_id = int(callback.data.split("_")[1])
    user_id = callback.from_user.id

    cursor.execute("SELECT action FROM votes WHERE user_id = ? AND profile_id = ?", (user_id, profile_id))
    vote = cursor.fetchone()

    if vote:
        await callback.answer("Вы уже голосовали за эту анкету.")
        return

    cursor.execute("UPDATE profile_form SET likes = likes + 1 WHERE id = ?", (profile_id,))
    cursor.execute("INSERT INTO votes (user_id, profile_id, action) VALUES (?, ?, 'like')", (user_id, profile_id))
    conn.commit()

    await callback.answer("Вы поставили лайк!")
    await callback.message.delete()
    await show_next_profile(callback.message, callback.from_user.id)


@router.callback_query(F.data.startswith("dislike_"))
async def dislike_profile(callback: CallbackQuery):
    profile_id = int(callback.data.split("_")[1])
    user_id = callback.from_user.id
    cursor.execute("SELECT action FROM votes WHERE user_id = ? AND profile_id = ?", (user_id, profile_id))
    vote = cursor.fetchone()

    if vote:
        await callback.answer("Вы уже голосовали за эту анкету.")
        return
    cursor.execute("UPDATE profile_form SET dislikes = dislikes + 1 WHERE id = ?", (profile_id,))
    cursor.execute("INSERT INTO votes (user_id, profile_id, action) VALUES (?, ?, 'dislike')", (user_id, profile_id))
    conn.commit()

    await callback.answer("Вы поставили дизлайк.")
    await callback.message.delete()
    await show_next_profile(callback.message, callback.from_user.id)


@router.callback_query(F.data.startswith("contact_"))
async def contact_profile(callback: CallbackQuery):
    profile_id = int(callback.data.split("_")[1])
    await callback.message.delete()
    cursor.execute("SELECT user_id, name_tg FROM profile_form WHERE id = ?", (profile_id,))
    profile = cursor.fetchone()

    if not profile:
        await callback.answer("Анкета не найдена.")
        return

    owner_id = profile[0]
    user_name_tg = profile[1]
    username = callback.from_user.username
    contact_info = f"@{username}" if username else f"ID: {callback.from_user.id}"

    await callback.bot.send_message(
        owner_id,
        f"С вами хочет связаться пользователь {contact_info}!"
    )
    await callback.answer("Связываемся с пользователем...")
    await callback.message.answer(f"Контакт для связи: @{user_name_tg}",
                                  reply_markup=await kb.continue_button())

@router.callback_query(F.data == "continue_profiles")
async def continue_profiles(callback: CallbackQuery):
    user_id = callback.from_user.id
    await callback.message.delete()
    await show_next_profile(callback.message, user_id)


@router.message(F.text == 'Понравившиеся анкеты')
async def my_like_form(message: types.Message):
    user_id = message.from_user.id
    cursor.execute("SELECT profile_id FROM votes WHERE user_id = ? AND action = 'like'", (user_id,))
    liked_profiles = cursor.fetchall()

    if not liked_profiles:
        await message.answer("У вас нет понравившихся анкет.")
        return
    liked_profile_ids = [profile[0] for profile in liked_profiles]
    def get_profile_info(profile_id):
        cursor.execute("""
            SELECT id, name, role, subject, description, photo_id, likes, dislikes
            FROM profile_form
            WHERE id = ? AND user_id != ? AND is_active = 1
        """, (profile_id, user_id))
        return cursor.fetchone()
    cursor.fetchone()
    current_index = 0
    profile = get_profile_info(liked_profile_ids[current_index])

    if not profile:
        await message.answer("Не удалось найти информацию по выбранной анкете.")
        return

    profile_info = (
        f"👤 *{profile[1]}* ({profile[2]})\n"
        f"📚 Предмет: {profile[3]}\n"
        f"ℹ Описание: {profile[4]}\n"
        f"❤️ Лайков: {profile[6]}\n"
        f"💔 Дизлайков: {profile[7]}"
    )
    like_form_k = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="Следующая", callback_data=f"next_{current_index}"),
                InlineKeyboardButton(text="Назад", callback_data=f"back_{current_index}")],
        ]
    )
    await message.answer_photo(
        photo=profile[5],
        caption=profile_info,
        reply_markup=like_form_k,
        parse_mode="Markdown"
    )


@router.callback_query(lambda c: c.data.startswith("next_") or c.data.startswith("back_"))
async def handle_profile_navigation(callback_query: types.CallbackQuery):
    user_id = callback_query.from_user.id
    data = callback_query.data.split('_')
    action = data[0]
    index = int(data[1])
    cursor.execute("SELECT profile_id FROM votes WHERE user_id = ? AND action = 'like'", (user_id,))
    liked_profiles = cursor.fetchall()
    liked_profile_ids = [profile[0] for profile in liked_profiles]

    if action == "next":
        index = (index + 1) % len(liked_profile_ids)
    elif action == "back":
        index = (index - 1) % len(liked_profile_ids)
    profile = get_profile_info(liked_profile_ids[index])

    if not profile:
        await callback_query.answer("Не удалось найти информацию по выбранной анкете.")
        return

    profile_info = (
        f"👤 *{profile[1]}* ({profile[2]})\n"
        f"📚 Предмет: {profile[3]}\n"
        f"ℹ Описание: {profile[4]}\n"
        f"❤️ Лайков: {profile[6]}\n"
        f"💔 Дизлайков: {profile[7]}"
    )
    like_form_k = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="Следующая", callback_data=f"next_{index}"),
                InlineKeyboardButton(text="Назад", callback_data=f"back_{index}")],
        ]
    )
    media = types.InputMediaPhoto(
        media=profile[5],  # Ссылка на фото
        caption=profile_info,
        parse_mode="Markdown"
    )

    # Обновляем сообщение с фото
    new_message = await callback_query.message.edit_media(
        media=media,
        reply_markup=like_form_k
    )
    await callback_query.answer()
    user_messages[user_id] = [callback_query.message.message_id, new_message.message_id]

def get_profile_info(profile_id):
    cursor.execute("""
        SELECT id, name, role, subject, description, photo_id, likes, dislikes
        FROM profile_form
        WHERE id = ? AND is_active = 1
    """, (profile_id,))
    return cursor.fetchone()


@router.message(F.text == 'Вернуться назад🔙')
async def back_button(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    if any(user_id in pair for pair in active_games.keys()):
        await message.answer("💢 Вы не можете использовать другие команды во время соревнования 💢")
        return
    user_data = await state.get_data()
    previous_state = user_data.get("previous_state")
    if previous_state == "start_profile_creation":
        # Если он был в процессе создания анкеты, возвращаем на это состояние
        new_message = await message.answer("Вы вернулись к созданию анкеты❗️", reply_markup=kb.form)
        await state.set_state(ProfileState.waiting_for_name)  # Ставим состояние, в котором он был
    elif previous_state == "profiles":
        # Если он был в поиске анкеты
        new_message = await message.answer("Вы вернулись к поиску анкеты❗️", reply_markup=kb.form)
        # Устанавливаем другое состояние (если нужно)
        # await state.set_state(Поиск состояния)
    else:
        new_message = await message.answer("🕎 Вы перешли в главное меню 🕎", reply_markup=kb.main)
    if user_id in user_messages:
        for msg_id in user_messages[user_id]:
            try:
                await message.bot.delete_message(chat_id=message.chat.id, message_id=msg_id)
            except Exception:
                pass
        user_messages[user_id] = []

    user_messages[user_id] = [message.message_id, new_message.message_id]



