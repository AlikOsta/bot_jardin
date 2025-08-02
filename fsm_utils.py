from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State
from db import all_slots
from hendlers import *


STATE_STACK_KEY = "state_stack"

async def push_state(state: FSMContext, new_state: State):
    data = await state.get_data()
    stack = data.get(STATE_STACK_KEY, [])
    stack.append(new_state)
    await state.update_data(**{STATE_STACK_KEY: stack})
    await state.set_state(new_state)


async def pop_state(state: FSMContext) -> State | None:
    data = await state.get_data()
    stack = data.get(STATE_STACK_KEY, [])
    if len(stack) <= 1:
        return None  
    stack.pop()
    prev = stack[-1]
    await state.update_data(**{STATE_STACK_KEY: stack})
    await state.set_state(prev)
    return prev


async def go_back(callback: CallbackQuery, state: FSMContext):
    from bot import VisitForm, ShiftSetup, GetSlots, AddStaff, RemStaff
    prev_state = await pop_state(state)

    if not prev_state:
        await render_start(callback)
        await state.clear()
        return

    if prev_state == VisitForm.age:
        await render_age(callback)
    elif prev_state == VisitForm.shift:
        await render_shift(callback)
    elif prev_state == VisitForm.notes:
        await render_notes(callback)

    if prev_state == ShiftSetup.age:
        slots_list = await all_slots()
        await render_settings_age(callback, slots_list)
    elif prev_state == ShiftSetup.shift:
        await render_shift(callback)
    elif prev_state == ShiftSetup.places:
        await render_settings_slots(callback)

    if prev_state == GetSlots.age:
        await render_age(callback)
    elif prev_state == GetSlots.shift:
        await render_shift(callback)

    if prev_state == AddStaff.username:
        await render_get_staff(callback)
    
    if prev_state == RemStaff.username:
        await render_get_staff(callback)