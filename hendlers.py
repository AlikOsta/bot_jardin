from aiogram.types import CallbackQuery
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram import types
from aiogram.enums import ParseMode
from kb import AGE_KB, SHIFT_KB, START_KB, BACK_KB, ADMIN_KB, BOOL_KB, STAFF_KB, BACK_SETTINGS_KB


async def render_start(target: Message | CallbackQuery):
    text = "Привет.\nЯ помогу тебе записаться в детский садик."
    
    if isinstance(target, CallbackQuery):
        await target.message.edit_text(text=text, reply_markup=START_KB)
    else:
        await target.answer(text=text, reply_markup=START_KB)


async def render_settings(message: Message):
    text = "Настройки для админа"
    await message.answer(text=text, reply_markup=ADMIN_KB)


async def render_about(callback: CallbackQuery):
    text = "Это наш детский сад. Здесь весело и интересно!"
    await callback.message.edit_text(text=text, reply_markup=BACK_KB)


async def render_schedule(callback: CallbackQuery):
    text = "Расписание и оплата"
    await callback.message.edit_text(text=text, reply_markup=BACK_KB)


async def render_additional(callback: CallbackQuery):
    text = "Дополнительные занятия и кружки"
    await callback.message.edit_text(text=text, reply_markup=BACK_KB)
    

async def render_age(callback: CallbackQuery):
    text = "Сколько лет ребёнку?"
    await callback.message.edit_text(text=text, reply_markup=AGE_KB)


async def render_shift(callback: CallbackQuery):
    text = "Выберете смену:"
    await callback.message.edit_text(text=text, reply_markup=SHIFT_KB)


async def render_notes(callback: CallbackQuery):
    text = "Есть ли аллергия или особенности?"
    await callback.message.edit_text(text=text)


async def post_admin(message: Message, data, bot, ADMIN_CHAT_ID):
    text = (
        f"Пользователь {message.from_user.first_name} {message.from_user.last_name},\n"
        f"Телеграм для связи @{message.from_user.username},\n"
        f"Ребенку {data['age']},\n"
        f"Смена {data['shift']},\n"
        f"Аллергия или особенности: {data['notes']}."
    )
    await bot.send_message(ADMIN_CHAT_ID, text)


async def render_settings_age(callback: CallbackQuery, slots_list):
    lines = ["Возраст  | Смена          | Статус"]
    lines.append("─" * len(lines[0]))

    for age_group, shift, available in slots_list:
        status = "✅" if available else "❌"
        lines.append(
            f"{age_group.ljust(8)} | {shift.ljust(14)} | {status}"
        )

    table = "\n".join(lines)
    text = ("<pre>" + table + "</pre>")
    text += "\n\nВыберите возрастную группу:"
    await callback.message.edit_text( text=text, parse_mode=ParseMode.HTML, reply_markup=AGE_KB)


async def render_settings_slots(callback: CallbackQuery):
    text = "Есть ли места?"
    await callback.message.edit_text(text=text, reply_markup=BOOL_KB)


async def render_success(callback: CallbackQuery):
    text = "Изменения внесены успешно!"
    await callback.message.edit_text(text=text, reply_markup=BACK_SETTINGS_KB)


async def render_show_get_slots(callback: CallbackQuery):
    text = "Свободные места есть. Оставьте заявку и администратор свяжится свами!"
    await callback.message.edit_text(text=text, reply_markup=BACK_KB)


async def render_not_slots(target: Message | CallbackQuery):
    text = "В данный момент свободныхмест нет!"
    if isinstance(target, CallbackQuery):
        await target.message.edit_text(text=text, reply_markup=BACK_KB)
    else:
        await target.answer(text=text, reply_markup=BACK_KB)
    

async def render_staff_list(callback: CallbackQuery, staff_list):
    text = "Список адмираторов:\n\n"
    for row in staff_list:
        user_id, first_name, last_name, username = row
        text += f"• {first_name} {last_name or ''} (@{username})\n"
    await callback.message.edit_text(text=text, reply_markup=STAFF_KB)


async def render_get_staff(callback: CallbackQuery):
    text = "Пришлите @username пользователя"
    await callback.message.edit_text(text=text)


async def render_get_user_id_success(message: Message, username:str):
    text = f"Пользователь @{username} добавлен в администраторы"
    await message.answer(text=text)


async def render_add_staff_success(message: Message, username:str):
    text = f"Администратор @{username} удален."
    await message.answer(text=text)


async def render_add_staff_fall(message: Message, username:str):
    text = f"Пользователь @{username} не разегестрирован!"
    await message.answer(text=text)

async def render_visit_form_success(message: Message):
    text = "Спасибо за заявку! Администратор свяжится с вами в близжайшее время!"
    await message.answer(text=text, reply_markup=BACK_KB)

