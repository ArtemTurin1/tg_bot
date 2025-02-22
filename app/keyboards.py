from gc import callbacks
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from app.database.requests import get_materialcategoriis, get_materialcategoriis_item

main = ReplyKeyboardMarkup(keyboard = [[KeyboardButton(text='Личный кабинет'),
                                        KeyboardButton(text = 'Поиск Учителя/Ученика')],
                                       [KeyboardButton(text = 'Ежедневные задания')],
                                        [KeyboardButton(text='Таблица лидеров'),
                                        KeyboardButton(text='Поддержка и предложения 🤝')]],
                           resize_keyboard=True,
                           input_field_placeholder='Выберите пункт...')

form = ReplyKeyboardMarkup(keyboard = [[KeyboardButton(text='Начать поиск'),
                                        KeyboardButton(text = 'Моя анкета')],
                                        [KeyboardButton(text = 'Понравившиеся анкеты'),
                                         KeyboardButton(text = 'Вернуться назад🔙')],
                                       ],
                           resize_keyboard=True,
                           input_field_placeholder='Выберите пункт...')

form_menu = ReplyKeyboardMarkup(keyboard=[
            [KeyboardButton(text = "Редактировать анкету")],
            [KeyboardButton(text = "Удалить анкету из поиска"), KeyboardButton(text = "Добавить анкету в поиск")],
            [KeyboardButton(text = "Вернуться назад🔙")]
        ],
                           resize_keyboard=True,
                           input_field_placeholder='Выберите пункт...')

lk = ReplyKeyboardMarkup(keyboard = [[KeyboardButton(text='Статистика'),
                                       KeyboardButton(text = 'Изменить способности')],
                                     [KeyboardButton(text = 'Вернуться назад🔙')]],
                           resize_keyboard=True,
                           input_field_placeholder='Выберите пункт...')

get_number = ReplyKeyboardMarkup(keyboard =[[KeyboardButton(text='Отправить контакт', request_contact=True)]],
                                 resize_keyboard=True)

iam = ReplyKeyboardMarkup(keyboard = [[KeyboardButton(text='Учитель')],
                                       [KeyboardButton(text = 'Ученик')]],
                           resize_keyboard=True,
                           input_field_placeholder='Выберите пункт...')

zd = ReplyKeyboardMarkup(keyboard = [[KeyboardButton(text='Решать задачи'),
                                       KeyboardButton(text = 'Арена')],
                                     [KeyboardButton(text='Добавить задание')]],
                           resize_keyboard=True,
                           input_field_placeholder='Выберите пункт...')

ability = ReplyKeyboardMarkup(keyboard = [[KeyboardButton(text='X к восстановлению жизни')],
                                       [KeyboardButton(text = 'X к увеличению 🪙')],
                                        [KeyboardButton(text = 'Жизни'),
                                         KeyboardButton(text = '💲')],
                                          [KeyboardButton(text = 'Вернуться назад🔙')]],
                           resize_keyboard=True,
                           input_field_placeholder='Выберите пункт...')
pump = ReplyKeyboardMarkup(keyboard = [[KeyboardButton(text='За 🪙'),
                                       KeyboardButton(text = 'За 💲')],
                                       [KeyboardButton(text = 'Вернуться назад🔙')]],
                           resize_keyboard=True,
                           input_field_placeholder='Выберите пункт...')
leave = ReplyKeyboardMarkup(keyboard = [[KeyboardButton(text='Покинуть соревнование')]],
                           resize_keyboard=True,
                           input_field_placeholder='Выберите пункт...')
donat = InlineKeyboardMarkup(
    inline_keyboard=[

            #InlineKeyboardButton(text="Пополнить 9 руб", callback_data="pay_9"),
            #InlineKeyboardButton(text="Пополнить 19 руб", callback_data="pay_19")],
        #InlineKeyboardButton(text="Пополнить 150 руб", callback_data="pay_150"),
            #InlineKeyboardButton(text="Пополнить 100 руб", callback_data="pay_100")],
            [InlineKeyboardButton(text="Оформить подписку 1000 рублей", callback_data="pay_1000")]
    ]
)



donat_life = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="1 жизни", callback_data="payl_1"),
            InlineKeyboardButton(text="3 жизней", callback_data="payl_3")],
            [InlineKeyboardButton(text="6 жизней", callback_data="payl_6"),
            InlineKeyboardButton(text="9 жизней", callback_data="payl_9"),
        ]
    ]
)

add_tasks = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Математика Профиль", callback_data="task_mathp")],
        [InlineKeyboardButton(text="Математика ОГЭ", callback_data="task_matho")]
    ])

form_tasks = ReplyKeyboardMarkup(keyboard=[
        [KeyboardButton(text="Математика Профиль/База", callback_data="form_mathp"),
        KeyboardButton(text="Математика ОГЭ", callback_data="form_matho")],
        [KeyboardButton(text="Информатика", callback_data="form_mathp"),
        KeyboardButton(text="Русский", callback_data="form_matho")],
        [KeyboardButton(text="Биология", callback_data="form_mathp"),
        KeyboardButton(text="Английский язык", callback_data="form_matho")],
    ],
    resize_keyboard=True,
    input_field_placeholder='Выберите пункт...'
)

form_redact = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text = "Имя"), KeyboardButton(text = "Роль")],
            [KeyboardButton(text = "Описание"), KeyboardButton(text = "Предмет")],
            [KeyboardButton(text = "Фото"), KeyboardButton(text = "Готово")]
        ],
        resize_keyboard=True
    )

async def add_materialcategorii():
    all_materialcategoriis = await get_materialcategoriis()
    keyboard = InlineKeyboardBuilder()
    for category in all_materialcategoriis:
        keyboard.add(InlineKeyboardButton(text=category.name, callback_data=f'task_{category.id}'))
    keyboard.add(InlineKeyboardButton(text='На главную', callback_data='to_main'))
    return keyboard.adjust(2).as_markup()

async def add_materials(materialcat_id):
    all_items = await get_materialcategoriis_item(materialcat_id)
    keyboard = InlineKeyboardBuilder()
    for material in all_items:
        keyboard.add(InlineKeyboardButton(text=material.name, callback_data=f'addmaterial_{material.id}'))
    keyboard.add(InlineKeyboardButton(text='На главную', callback_data='to_main'))
    return keyboard.adjust(3).as_markup()

async def materialcategorii():
    all_materialcategoriis = await get_materialcategoriis()
    keyboard = InlineKeyboardBuilder()
    for category in all_materialcategoriis:
        keyboard.add(InlineKeyboardButton(text=category.name, callback_data=f'category_{category.id}'))
    keyboard.add(InlineKeyboardButton(text='На главную', callback_data='to_main'))
    return keyboard.adjust(2).as_markup()

async def arenacatalog():
    all_arenacatalog = await get_materialcategoriis()
    keyboard = InlineKeyboardBuilder()
    for category in all_arenacatalog:
        keyboard.add(InlineKeyboardButton(text=category.name, callback_data=f'arenacategory_{category.id}'))
    keyboard.add(InlineKeyboardButton(text='На главную', callback_data='to_main'))
    return keyboard.adjust(2).as_markup()

async def materials(materialcat_id):
    all_items = await get_materialcategoriis_item(materialcat_id)
    keyboard = InlineKeyboardBuilder()
    for material in all_items:
        keyboard.add(InlineKeyboardButton(text=material.name, callback_data=f'material_{material.id}'))
    keyboard.add(InlineKeyboardButton(text='На главную', callback_data='to_main'))
    return keyboard.adjust(3).as_markup()

async def glavn():
    keyboard = InlineKeyboardBuilder()
    keyboard.add(InlineKeyboardButton(text='На главную', callback_data='to_main'))
    return keyboard.adjust(2).as_markup()

async def leave_arena():
    keyboard = InlineKeyboardBuilder()
    keyboard.add(InlineKeyboardButton(text='Прекратить поиск', callback_data='leave_arena'))
    return keyboard.adjust(2).as_markup()

def get_profile_keyboard(profile_id):
    keyboard = InlineKeyboardBuilder()
    keyboard.add(
        InlineKeyboardButton(text="👍 Лайк", callback_data=f"like_{profile_id}"),
        InlineKeyboardButton(text="👎 Дизлайк", callback_data=f"dislike_{profile_id}"),
        InlineKeyboardButton(text="➡ Пропустить", callback_data="skip"),
        InlineKeyboardButton(text="📞 Связаться", callback_data=f"contact_{profile_id}")
    )
    return keyboard.adjust(2).as_markup()


async def continue_button():
    keyboard = InlineKeyboardBuilder()
    keyboard.add(InlineKeyboardButton(text='Продолжить просмотр', callback_data='continue_profiles'))
    return keyboard.adjust(2).as_markup()



