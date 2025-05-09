from aiogram.fsm.state import StatesGroup, State


class OrderStates(StatesGroup):
    waiting_for_delivery_address = State()
    waiting_for_phone_number = State()