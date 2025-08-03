from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery

BACK_KB = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="Вернуться в меню", callback_data='back')],
    ]
)

SKOTS_BACK = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="Вернуться к насройкам", callback_data='back_to_settings')],
    ]
)

BACK_SETTINGS_KB = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="Оставить заявку", callback_data='apply'),
            InlineKeyboardButton(text="🔙 Назад", callback_data="go_back")
            ] ,
    ]
)

AGE_KB = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="2-3 года", callback_data="2-3 года"),
            InlineKeyboardButton(text="3-4 лет", callback_data="3-4 года"),
        ],
        [
            InlineKeyboardButton(text="4-5 лет", callback_data="4-5 лет"),
            InlineKeyboardButton(text="5-7 лет", callback_data="5-7 лет"),
        ],
        [InlineKeyboardButton(text="🔙 Назад", callback_data="go_back")] 
    ]
)


SHIFT_KB = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="Утро 09:00-13:30", callback_data="Утро"),
            InlineKeyboardButton(text="Вечер 13:30-18:00", callback_data="Вечер"),
        ],
        [InlineKeyboardButton(text="Полный день 09:00-18:00", callback_data="Полный день")],  
        [InlineKeyboardButton(text="🔙 Назад", callback_data="go_back")]     
    ]
)


START_KB = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="Оставить заявку", callback_data='apply'),
            InlineKeyboardButton(text="Наличие мест", callback_data='сheck')
        ],        
        [
            InlineKeyboardButton(text="Расписание и оплата", callback_data='schedule'),
            InlineKeyboardButton(text="Занятия и кружки", callback_data='additional')
        ],
        [InlineKeyboardButton(text="О нас", callback_data='about')],
    ]
)


ADMIN_KB = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="Наличие мест", callback_data='settings')],
        [InlineKeyboardButton(text="Администраторы", callback_data='get_staff')],
    ]
)


BOOL_KB = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="✅ Да", callback_data='True'),
            InlineKeyboardButton(text="❌ Нет", callback_data='False')
        ],
        [InlineKeyboardButton(text="🔙 Назад", callback_data="go_back")]  
    ]
)

STAFF_KB = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="✅ Добавить", callback_data='add_staff'),
            InlineKeyboardButton(text="❌ Удалить", callback_data='rem_staff')
        ],
        [InlineKeyboardButton(text="🔙 Назад", callback_data="go_back")]  
    ]
)

