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
from db import set_availability, get_availability, get_user, add_user, get_is_staff, set_is_staff, all_staff, get_user_id

from fsm_utils import push_state, go_back
from hendlers import *
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_CHAT_ID = os.getenv("ADMIN_CHAT_ID")


bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(storage=MemoryStorage())


@dp.callback_query(F.data == "back")
async def back(callback: CallbackQuery):
    await render_start(callback)


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
    await render_start(message)


@dp.message(Command("settings"))
async def cmd_start(message: Message, state: FSMContext):
    await state.clear()
    is_staff = await get_is_staff(message.from_user.id)
    if is_staff:
        await render_settings(message)


@dp.callback_query(F.data == "about")
async def show_about(callback: CallbackQuery):
    await render_about(callback)


@dp.callback_query(F.data == "schedule")
async def show_schedule(callback: CallbackQuery):
    await render_schedule(callback)


@dp.callback_query(F.data == "additional")
async def show_additional(callback: CallbackQuery):
    await render_additional(callback)


class VisitForm(StatesGroup):
    age = State()
    shift = State()
    notes = State()


@dp.callback_query(F.data == "apply")
async def process_age(callback: CallbackQuery, state: FSMContext):
    if callback.data == "go_back":
        await go_back(callback, state)
        return  
    await push_state(state, VisitForm.age)
    await render_age(callback, state)
    

@dp.callback_query(VisitForm.age)
async def process_shift(callback: CallbackQuery, state: FSMContext):
    if callback.data == "go_back":
        await go_back(callback, state)
        return  
    age = callback.data
    await state.update_data(age=age)
    await push_state(state, VisitForm.shift)
    await render_shift(callback, state)
    

@dp.callback_query(VisitForm.shift)
async def process_notes(callback: CallbackQuery, state: FSMContext):
    if callback.data == "go_back":
        await go_back(callback, state)
        return  

    shift = callback.data
    await state.update_data(shift=shift)
    await push_state(state, VisitForm.notes)
    await render_notes(callback, state)
    

@dp.message(VisitForm.notes)
async def print_data(message: Message, state: FSMContext):
    await state.update_data(notes=message.text)
    data = await state.get_data()
    if await get_availability(data['age'], data['shift']):
        await post_admin(message, data, bot, ADMIN_CHAT_ID)
        await render_visit_form_success(message)
    else:
        await render_not_slots(message)
    await state.clear()

    

class ShiftSetup(StatesGroup):
    age = State()
    shift = State()
    places = State()


@dp.callback_query(F.data == "settings")
async def get_age(callback: CallbackQuery, state: FSMContext):
    await render_settings_age(callback)
    await state.set_state(ShiftSetup.age)


@dp.callback_query(ShiftSetup.age)
async def get_shift(callback: CallbackQuery, state: FSMContext):
    age = callback.data
    await state.update_data(age=age)
    await render_shift(callback)
    await state.set_state(ShiftSetup.shift)


@dp.callback_query(ShiftSetup.shift)
async def get_places(callback: CallbackQuery, state: FSMContext):    
    shift = callback.data
    await state.update_data(shift=shift)
    await render_settings_slots(callback)
    await state.set_state(ShiftSetup.places)


@dp.callback_query(ShiftSetup.places)
async def process_shift(callback: CallbackQuery, state: FSMContext):
    raw_value = callback.data.strip() 
    places = raw_value == "True"
    await state.update_data(places=places)
    data = await state.get_data()
    await set_availability(data["age"], data["shift"], data["places"])
    await render_success(callback) 
    await state.clear()


class GetSlots(StatesGroup):
    age = State()
    shift = State()


@dp.callback_query(F.data == "сheck")
async def get_slots_age(callback: CallbackQuery, state: FSMContext):
    await render_slots_age(callback)
    await state.set_state(GetSlots.age)


@dp.callback_query(GetSlots.age)
async def get_slots_shift(callback: CallbackQuery, state: FSMContext):
    age = callback.data
    await state.update_data(age=age)
    await render_slots_shift(callback)
    await state.set_state(GetSlots.shift)


@dp.callback_query(GetSlots.shift)
async def show_get_slots(callback: CallbackQuery, state: FSMContext):
    shift = callback.data
    await state.update_data(shift=shift)
    data = await state.get_data()
    if await get_availability(data["age"], data["shift"]):
        await render_show_get_slots(callback)
    else:
        await render_not_slots(callback)
    await state.clear()


@dp.callback_query(F.data == "get_staff")
async def show_staff(callback: CallbackQuery):
    staff_list = await all_staff()
    await render_staff_list(callback, staff_list)


class AddStaff(StatesGroup):
    username = State()


@dp.callback_query(F.data == "add_staff")
async def get_staff(callback: CallbackQuery, state: FSMContext):
    await render_get_staff(callback)
    await state.set_state(AddStaff.username)


@dp.message(AddStaff.username)
async def add_staff(message: Message, state: FSMContext):
    username = message.text.strip().lstrip("@")
    await state.update_data(username=username)
    user_id = await get_user_id(username)
    if user_id:
        await set_is_staff(user_id, True)
        await render_get_user_id_success(message, username)
    else:
        await render_get_user_id_fall(message, username)
    await state.clear()


class RemStaff(StatesGroup):
    username = State()


@dp.callback_query(F.data == "rem_staff")
async def get_staff(callback: CallbackQuery, state: FSMContext):
    await render_get_staff(callback)
    await state.set_state(RemStaff.username)


@dp.message(RemStaff.username)
async def add_staff(message: Message, state: FSMContext):
    username = message.text.strip().lstrip("@")
    await state.update_data(username=username)

    user_id = await get_user_id(username)
    if user_id:
        await set_is_staff(user_id, False)
        await render_add_staff_success(message, username)
    else:
        await render_add_staff_fall(message, username)
    await state.clear()


async def main():
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
