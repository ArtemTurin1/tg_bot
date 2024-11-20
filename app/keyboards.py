from gc import callbacks
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from app.database.requests import get_materialcategoriis, get_materialcategoriis_item

main = ReplyKeyboardMarkup(keyboard = [[KeyboardButton(text='Мой персонаж', callback_data='LK'),
                                        KeyboardButton(text = 'Ежедневные задания', callback_data='zadania')],
                                        [KeyboardButton(text='Игра')],
                                        [KeyboardButton(text='Таблица лидеров'),
                                        KeyboardButton(text='Поддержка и предложения')]],
                           resize_keyboard=True,
                           input_field_placeholder='Выберите пункт...')

lk = ReplyKeyboardMarkup(keyboard = [[KeyboardButton(text='Статистика персонажа', callback_data='stats'),
                                       KeyboardButton(text = 'Прокачать способности', callback_data='myteacher')],
                                     [KeyboardButton(text = 'Вернуться в главное меню', callback_data='to_main')]],
                           resize_keyboard=True,
                           input_field_placeholder='Выберите пункт...')

get_number = ReplyKeyboardMarkup(keyboard =[[KeyboardButton(text='Отправить контакт', request_contact=True)]],
                                 resize_keyboard=True)

iam = ReplyKeyboardMarkup(keyboard = [[KeyboardButton(text='Учитель', callback_data='stats')],
                                       [KeyboardButton(text = 'Ученик', callback_data='myteacher')]],
                           resize_keyboard=True,
                           input_field_placeholder='Выберите пункт...')

zd = ReplyKeyboardMarkup(keyboard = [[KeyboardButton(text='Решать задачи', callback_data='stats')],
                                       [KeyboardButton(text = 'Арена', callback_data='myteacher')]],
                           resize_keyboard=True,
                           input_field_placeholder='Выберите пункт...')

ability = ReplyKeyboardMarkup(keyboard = [[KeyboardButton(text='X к востановлению жизни', callback_data='Xzizn')],
                                       [KeyboardButton(text = 'X к увеличению баллов', callback_data='myteacher')],
                                        [KeyboardButton(text = 'Жизни', callback_data='myteacher'),
                                         KeyboardButton(text = 'Донат', callback_data='myteacher')],
                                          [KeyboardButton(text = 'Вернуться назад', callback_data='to_main')]],
                           resize_keyboard=True,
                           input_field_placeholder='Выберите пункт...')
pump = ReplyKeyboardMarkup(keyboard = [[KeyboardButton(text='За баллы', callback_data='stats'),
                                       KeyboardButton(text = 'За донат', callback_data='zadonat')],
                                       [KeyboardButton(text = 'Вернуться назад', callback_data='to_main')]],
                           resize_keyboard=True,
                           input_field_placeholder='Выберите пункт...')
donat = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="Пополнить 100 руб", callback_data="pay_100"),
            InlineKeyboardButton(text="Пополнить 200 руб", callback_data="pay_200")
        ]
    ]
)
async def materialcategorii():
    all_materialcategoriis = await get_materialcategoriis()
    keyboard = InlineKeyboardBuilder()
    for category in all_materialcategoriis:
        keyboard.add(InlineKeyboardButton(text=category.name, callback_data=f'category_{category.id}'))
    keyboard.add(InlineKeyboardButton(text='На главную', callback_data='to_main'))
    return keyboard.adjust(2).as_markup()

async def materials(materialcat_id):
    all_items = await get_materialcategoriis_item(materialcat_id)
    keyboard = InlineKeyboardBuilder()
    for material in all_items:
        keyboard.add(InlineKeyboardButton(text=material.name, callback_data=f'material_{material.id}'))
    keyboard.add(InlineKeyboardButton(text='На главную', callback_data='to_main'))
    return keyboard.adjust(2).as_markup()

async def glavn():
    keyboard = InlineKeyboardBuilder()
    keyboard.add(InlineKeyboardButton(text='На главную', callback_data='to_main'))
    return keyboard.adjust(2).as_markup()