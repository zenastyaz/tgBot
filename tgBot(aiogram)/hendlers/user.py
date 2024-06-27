from aiogram import types, Router, F
from aiogram.exceptions import TelegramBadRequest
from aiogram.types import Message, CallbackQuery, LabeledPrice
from aiogram.filters import CommandStart
from sqlalchemy.ext.asyncio import AsyncSession
from keyboards.reply import get_keyboard, del_kb
from keyboards.inline import MenuCallback
from filters.chat_types import ChatTypes
from hendlers.menu_processing import get_menu_content
from database.requests import orm_add_user, orm_add_to_cart, orm_get_user_carts

user_router = Router()
user_router.message.filter(ChatTypes(['private']))


@user_router.message(CommandStart())
async def start(message: Message, session: AsyncSession):
    user = message.from_user
    await orm_add_user(
        session,
        user_id=user.id,
        first_name=user.first_name,
        last_name=user.last_name,
        username=user.username,
    )
    await message.answer(f"Добро пожаловать, {message.from_user.first_name}!")
    media, reply_markup = await get_menu_content(session, level=0, menu_name='main')
    await message.answer_photo(media.media, caption=media.caption, reply_markup=reply_markup)


async def add_to_cart(callback: types.CallbackQuery, callback_data: MenuCallback, session: AsyncSession):
    user = callback.from_user
    await orm_add_to_cart(session, user_id=user.id, cocktail_id=callback_data.cocktail_id)
    await callback.answer("Коктейль добавлен в корзину.")


@user_router.callback_query(MenuCallback.filter())
async def menu_user(callback: CallbackQuery, callback_data: MenuCallback, session: AsyncSession):
    if callback_data.menu_name == 'add_to_cart':
        await add_to_cart(callback, callback_data, session)
        return
    if callback_data.menu_name == 'pay':
        carts = await orm_get_user_carts(session, callback.from_user.id)
        if carts:
            total_price = round(sum(cart.quantity * cart.cocktail.price for cart in carts), 2)
            await send_invoice(callback, callback.from_user.id, total_price)
        return
    if callback_data.menu_name == 'booking':
        await callback.message.answer('\nНажмите на кнопку, чтобы отправить номер ⬇️', reply_markup=get_keyboard(
            '', 'Отправить номер 📲', request_contact=1, sizes=(2,)))
        return
    result = await get_menu_content(
        session,
        level=callback_data.level,
        menu_name=callback_data.menu_name,
        category=callback_data.category,
        page=callback_data.page,
        cocktail_id=callback_data.cocktail_id,
        user_id=callback.from_user.id,
        table_number=callback_data.table_number,
    )

    if result is not None:
        media, reply_markup = result
        if media:
            await callback.message.edit_media(media=media, reply_markup=reply_markup)
        else:
            await callback.message.edit_reply_markup(reply_markup=reply_markup)
    await callback.answer()


async def send_invoice(callback: CallbackQuery, user_id: int, total_price: float):
    prices = [
        LabeledPrice(label='Total', amount=int(total_price * 100))
    ]

    provider_token = "TEST:abcdefghij1234567890"

    try:
        await callback.bot.send_invoice(
            chat_id=user_id,
            title="Оплата заказа",
            description="Оплата за коктейли",
            payload="test_payload",
            provider_token=provider_token,
            currency="EUR",
            prices=prices,
            start_parameter="test-payment",
        )
    except TelegramBadRequest as e:
        await callback.message.answer(f"Произошла ошибка при отправке счета: {e}")


@user_router.message(F.contact)
async def get_contact(message: Message):
    await message.answer('Номер получен')
    # await message.answer(str(message.contact))
    await message.answer(f"Спасибо! Вы отправили номер телефона: {message.contact.phone_number}", reply_markup=del_kb)

