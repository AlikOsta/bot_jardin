import asyncio
import os
from aiogram import Bot, Dispatcher
from aiogram.types import Message
from aiogram.filters import Command
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import CallbackQuery
from aiogram import F
from dotenv import load_dotenv
from db import set_availability, get_availability, get_user, add_user, get_is_staff, set_is_staff, all_staff, get_user_id
from kb import AGE_KB, SHIFT_KB, START_KB, BACK_KB, ADMIN_KB, BOOL_KB, STAFF_KB, BACK_BTN


load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_CHAT_ID = os.getenv("ADMIN_CHAT_ID")


bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(storage=MemoryStorage())


@dp.callback_query(F.data == "back")
async def go_back(callback: CallbackQuery):
    text = "Привет.\n Я помогу тебе записаться в детский садик."
    await callback.message.edit_text(text=text, reply_markup=START_KB)
    await callback.answer()


@dp.message(Command("start"))
async def cmd_start(message: Message, state: FSMContext):
    await state.clear()
    user = await get_user(message.from_user.id)
    if not user:
        await add_user(
            id_telegram=message.from_user.id,
            first_name=message.from_user.first_name,
            last_name=message.from_user.last_name,
            username=message.from_user.username,
            is_staff=False
        )
    text = "Привет.\n Я помогу тебе записаться в детский садик."
    await message.answer(text=text, reply_markup=START_KB)


@dp.message(Command("settings"))
async def cmd_start(message: Message, state: FSMContext):
    await state.clear()
    is_staff = await get_is_staff(message.from_user.id)
    if is_staff:
        text = "Настройки для админа"
        await message.answer(text=text, reply_markup=ADMIN_KB)


@dp.callback_query(F.data == "about")
async def show_about(callback: CallbackQuery):
    text = "Это наш детский сад. Здесь весело и интересно!"
    await callback.message.edit_text(text=text, reply_markup=BACK_KB)
    await callback.answer()


@dp.callback_query(F.data == "schedule")
async def show_schedule(callback: CallbackQuery):
    text = "Расписание и оплата"
    await callback.message.edit_text(text=text, reply_markup=BACK_KB)
    await callback.answer() 


@dp.callback_query(F.data == "additional")
async def show_additional(callback: CallbackQuery):
    text = "Дополнительные занятия и кружки"
    await callback.message.edit_text(text=text, reply_markup=BACK_KB)
    await callback.answer()


class VisitForm(StatesGroup):
    age = State()
    shift = State()
    notes = State()

@dp.callback_query(F.data == "apply")
async def process_age(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await state.clear()
    text = "Сколько лет ребёнку?"
    await callback.message.edit_text(text=text, reply_markup=AGE_KB)
    await state.set_state(VisitForm.age)


@dp.callback_query(VisitForm.age)
async def process_shift(callback: CallbackQuery, state: FSMContext):
    age = callback.data
    await state.update_data(age=age)
    await callback.answer()
    text = "Какую смену вы хотите?"
    await callback.message.edit_text(text=text, reply_markup=SHIFT_KB)
    await state.set_state(VisitForm.shift)


@dp.callback_query(VisitForm.shift)
async def process_notes(callback: CallbackQuery, state: FSMContext):
    shift = callback.data
    await state.update_data(shift=shift, previous=VisitForm.shift.state)
    await callback.answer()
    text = "Есть ли аллергия или особенности?"
    await callback.message.edit_text(text=text)
    await state.set_state(VisitForm.notes)


@dp.message(VisitForm.notes)
async def print_data(message: Message, state: FSMContext):
    await state.update_data(notes=message.text)
    data = await state.get_data()
    if await get_availability(data['age'], data['shift']):
        await post_admin(message, data)
        text = "Спасибо за заявку! Администратор свяжится с вами в близжайшее время!"
    else:
        text = "В данный момент свободныхмест нет!"
    await message.answer(text=text, reply_markup=BACK_KB)
    await state.clear()


async def post_admin(message: Message, data):
    text = (
        f"Пользователь {message.from_user.first_name} {message.from_user.last_name},\n"
        f"Телеграм для связи @{message.from_user.username},\n"
        f"Ребенку {data['age']},\n"
        f"Смена {data['shift']},\n"
        f"Аллергия или особенности: {data['notes']}."
    )
    await bot.send_message(ADMIN_CHAT_ID, text)
    

class ShiftSetup(StatesGroup):
    age = State()
    shift = State()
    places = State()


@dp.callback_query(F.data == "settings")
async def get_age(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    text = "Давайте настроим наличее мест для детей.\nВыберете возростную группу."
    await callback.message.edit_text(text=text, reply_markup=AGE_KB)
    await state.set_state(ShiftSetup.age)


@dp.callback_query(ShiftSetup.age)
async def get_shift(callback: CallbackQuery, state: FSMContext):
    age = callback.data
    await state.update_data(age=age)
    await callback.answer()
    text = "Какую смену нужно изменить?"
    await callback.message.edit_text(text=text, reply_markup=SHIFT_KB)
    await state.set_state(ShiftSetup.shift)


@dp.callback_query(ShiftSetup.shift)
async def get_places(callback: CallbackQuery, state: FSMContext):
    shift = callback.data
    await state.update_data(shift=shift)
    await callback.answer()
    text = "Есть ли места?"
    await callback.message.edit_text(text=text, reply_markup=BOOL_KB)
    await state.set_state(ShiftSetup.places)


@dp.callback_query(ShiftSetup.places)
async def process_shift(callback: CallbackQuery, state: FSMContext):
    raw_value = callback.data.strip() 
    places = raw_value == "True"
    await state.update_data(places=places)
    data = await state.get_data()
    await set_availability(data["age"], data["shift"], data["places"])
    await callback.answer()
    text = "Изменения внесены успешно!"
    await callback.message.edit_text(text=text)
    await state.clear()


class GetSlots(StatesGroup):
    age = State()
    shift = State()


@dp.callback_query(F.data == "сheck")
async def get_slots_age(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    text = "Давайте проверим наличее свободных мест.\nВыберете возростную группу."
    await callback.message.edit_text(text=text, reply_markup=AGE_KB)
    await state.set_state(GetSlots.age)


@dp.callback_query(GetSlots.age)
async def get_slots_shift(callback: CallbackQuery, state: FSMContext):
    age = callback.data
    await state.update_data(age=age)
    await callback.answer()
    text = "Какую смену нужно изменить?"
    await callback.message.edit_text(text=text, reply_markup=SHIFT_KB)
    await state.set_state(GetSlots.shift)


@dp.callback_query(GetSlots.shift)
async def show_get_slots(callback: CallbackQuery, state: FSMContext):
    shift = callback.data
    await state.update_data(shift=shift)
    await callback.answer()
    data = await state.get_data()
    if await get_availability(data["age"], data["shift"]):
        text = "Свободные места есть. Оставьте заявку и администратор свяжится свами!"
    else:
        text = "В данный момент свободныхмест нет!"
    await callback.message.edit_text(text=text, reply_markup=BACK_KB)
    await state.clear()


@dp.callback_query(F.data == "get_staff")
async def show_staff(callback: CallbackQuery):
    staff_list = await all_staff()
    text = "Список адмираторов:\n\n"
    for row in staff_list:
        user_id, first_name, last_name, username = row
        text += f"• {first_name} {last_name or ''} (@{username})\n"
    await callback.message.edit_text(text=text, reply_markup=STAFF_KB)


class AddStaff(StatesGroup):
    username = State()


@dp.callback_query(F.data == "add_staff")
async def get_staff(callback: CallbackQuery, state: FSMContext):
    print("add staff")
    await callback.answer()
    text = "Пришли username пользователя"
    await callback.message.edit_text(text=text)
    await state.set_state(AddStaff.username)


@dp.message(AddStaff.username)
async def add_staff(message: Message, state: FSMContext):
    username = message.text.strip().lstrip("@")
    await state.update_data(username=username)

    user_id = await get_user_id(username)
    if user_id:
        await set_is_staff(user_id, True)
        text = f"Пользователь @{username} Добавлен в администраторы"
    else:
        text = f"Пользователь @{username} не разегестрирован!"
    await message.answer(text=text)
    await state.clear()


class RemStaff(StatesGroup):
    username = State()


@dp.callback_query(F.data == "rem_staff")
async def get_staff(callback: CallbackQuery, state: FSMContext):
    print("rem staff")
    await callback.answer()
    text = "Пришли username администратора"
    await callback.message.edit_text(text=text)
    await state.set_state(RemStaff.username)


@dp.message(RemStaff.username)
async def add_staff(message: Message, state: FSMContext):
    username = message.text.strip().lstrip("@")
    await state.update_data(username=username)

    user_id = await get_user_id(username)
    if user_id:
        await set_is_staff(user_id, False)
        text = f"Администратор @{username} удален."
    else:
        text = f"Пользователь @{username} не разегестрирован!"
    await message.answer(text=text)
    await state.clear()


async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
