from aiogram.fsm.state import StatesGroup, State


class FaqStates(StatesGroup):
    waiting_for_faq_question = State()
