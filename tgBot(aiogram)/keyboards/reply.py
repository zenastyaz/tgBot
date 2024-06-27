from aiogram.types import KeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove
from aiogram.utils.keyboard import ReplyKeyboardBuilder


def get_keyboard(
    *btns: str,
    placeholder: str = None,
    request_contact: int = None,
    request_location: int = None,
    sizes: tuple[int] = (2,),
):
    '''
    get_keyboard(
            "Меню",
            "О магазине",
            "Варианты оплаты",
            "Варианты доставки",
            "Отправить номер телефона"
            placeholder="Что вас интересует?",
            request_contact=4,
            sizes=(2, 2, 1)
        )
    '''

    keyboard = ReplyKeyboardBuilder()

    for index, text in enumerate(btns, start=0):

        if request_contact and request_contact == index:
            keyboard.add(KeyboardButton(text=text, request_contact=True))

        elif request_location and request_location == index:
            keyboard.add(KeyboardButton(text=text, request_location=True))
        else:

            keyboard.add(KeyboardButton(text=text))

    return keyboard.adjust(*sizes).as_markup(
        resize_keyboard=True, input_field_placeholder=placeholder)


del_kb = ReplyKeyboardRemove()


# btn = ReplyKeyboardMarkup(
#     keyboard=[
#         [KeyboardButton(text='Просмотр меню 🍸')],
#         [KeyboardButton(text='Сделать заказ 📝'), KeyboardButton(text='Просмотр профиля 👤'),
#         KeyboardButton(text='Варианты оплаты')],
#         [KeyboardButton(text='Сайт 🌐'), KeyboardButton(text='О нас ℹ️')],
#     ],
#     resize_keyboard=True,
#     input_field_placeholder='Выберите опцию...'
# )
#
# del_kb = ReplyKeyboardRemove
