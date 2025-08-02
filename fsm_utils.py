from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State


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
    from bot import VisitForm 
    from hendlers import render_age, render_notes, render_shift, render_start
    prev_state = await pop_state(state)

    if not prev_state:
        await state.clear()
        await render_start(callback)
        return

    if prev_state == VisitForm.age:
        await render_age(callback, state)
    elif prev_state == VisitForm.shift:
        await render_shift(callback, state)
    elif prev_state == VisitForm.notes:
        await render_notes(callback, state)