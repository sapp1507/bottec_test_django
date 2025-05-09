from aiogram.fsm.state import State, StatesGroup


class OrderStates(StatesGroup):
    waiting_for_delivery_address = State()
    waiting_for_phone_number = State()