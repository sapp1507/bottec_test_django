from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from bot.keyboards import faq as kb
from bot.keyboards import user as user_kb
from bot.states.faq import FaqStates
from faq.models import FAQItem

router = Router()


@router.callback_query(F.data.startswith('faq_page'))
async def get_faqs(callback: CallbackQuery):
    params = callback.data.split('_')
    page = 1
    if len(params) == 3:
        page = int(callback.data.split('_')[2])
    await callback.message.answer(
        'Ответы на часто задаваемые вопросы,\n\n Выберите категорию:',
        reply_markup=await kb.get_faq_category_keyboard(page)
    )
    await callback.message.delete()


@router.callback_query(F.data.startswith('add_faq'))
async def add_faq(callback: CallbackQuery, state: FSMContext):

    await callback.message.answer(
        'Введите свой вопрос...',
    )
    await state.set_state(FaqStates.waiting_for_faq_question)
    await callback.message.delete()


@router.message(FaqStates.waiting_for_faq_question)
async def get_faq_question(message: Message, state: FSMContext):
    question = message.text.strip()
    await state.clear()
    await FAQItem.objects.acreate(
        question=question,
    )
    await message.answer(
        text='Вопрос сохранен, в ближайшее время на него будет ответ.',
        reply_markup=user_kb.main_keyboard
    )


@router.callback_query(F.data.startswith('faq_category'))
async def get_faq_items(callback: CallbackQuery):
    params = callback.data.split('_')
    category_id = int(callback.data.split('_')[2])
    page = 1
    if len(params) == 4:
        page = int(callback.data.split('_')[3])
    await callback.message.answer(
        text='Вопросы:',
        reply_markup=await kb.get_faq_items_keyboard(category_id, page)
    )
    await callback.message.delete()


@router.callback_query(F.data.startswith('faq_item'))
async def get_faq_item(callback: CallbackQuery):
    item_id = int(callback.data.split('_')[2])
    item = await FAQItem.objects.aget(id=item_id)
    await callback.message.answer(
        text=item.answer,
        reply_markup=await kb.get_faq_items_keyboard(item.category_id, page=1)
    )
    await callback.message.delete()

