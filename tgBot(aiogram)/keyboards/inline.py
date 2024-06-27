from aiogram.filters.callback_data import CallbackData
from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder


class MenuCallback(CallbackData, prefix="menu"):
    level: int
    menu_name: str
    category: int | None = None
    page: int = 1
    cocktail_id: int | None = None
    table_number: int | None = None


def get_user_main_btns(*, level: int, sizes: tuple[int] = (2, 1, 2)):
    keyboard = InlineKeyboardBuilder()
    btns = {
        "Меню 🍸": "catalog",
        "Корзина 🛒": "cart",
        "Зарезервировать стол 📆": "booking",
        "Оплата 💶": "payment",
        "Сайт 🌐": "site",
        "О нас ℹ️": "about",
    }
    for text, menu_name in btns.items():
        if menu_name == "catalog":
            keyboard.add(InlineKeyboardButton(text=text,
                                              callback_data=MenuCallback(level=level+1, menu_name=menu_name).pack()))
        elif menu_name == "cart":
            keyboard.add(InlineKeyboardButton(text=text,
                                              callback_data=MenuCallback(level=3, menu_name=menu_name).pack()))
        elif menu_name == "booking":
            keyboard.add(InlineKeyboardButton(text=text,
                                              callback_data=MenuCallback(level=4, menu_name=menu_name).pack()))
        else:
            keyboard.add(InlineKeyboardButton(text=text,
                                              callback_data=MenuCallback(level=level, menu_name=menu_name).pack()))
    return keyboard.adjust(*sizes).as_markup()


def get_user_catalog_btns(*, level: int, categories: list, sizes: tuple[int] = (2,)):
    keyboard = InlineKeyboardBuilder()
    keyboard.add(InlineKeyboardButton(text='Назад', callback_data=MenuCallback(level=level-1, menu_name='main').pack()))
    keyboard.add(InlineKeyboardButton(text='Корзина 🛒', callback_data=MenuCallback(level=3, menu_name='cart').pack()))
    for c in categories:
        keyboard.add(InlineKeyboardButton(text=c.name,
                     callback_data=MenuCallback(level=level+1, menu_name=c.name, category=c.id).pack()))
    return keyboard.adjust(*sizes).as_markup()


def get_cocktails_btns(*, level: int, category: int, page: int, pagination_btns: dict, cocktail_id: int,
                       sizes: tuple[int] = (2,)):
    keyboard = InlineKeyboardBuilder()
    keyboard.add(InlineKeyboardButton(text='Назад',
                 callback_data=MenuCallback(level=level - 1, menu_name='catalog').pack()))
    keyboard.add(InlineKeyboardButton(text='Корзина 🛒',
                 callback_data=MenuCallback(level=3, menu_name='cart').pack()))
    keyboard.add(InlineKeyboardButton(text='Купить 💶',
                 callback_data=MenuCallback(level=level, menu_name='add_to_cart', cocktail_id=cocktail_id).pack()))
    keyboard.adjust(*sizes)

    row = []
    for text, menu_name in pagination_btns.items():
        if menu_name == 'next':
            row.append(InlineKeyboardButton(text=text,
                       callback_data=MenuCallback(
                           level=level,
                           menu_name=menu_name,
                           category=category,
                           page=page + 1).pack()))

        elif menu_name == 'previous':
            row.append(InlineKeyboardButton(text=text,
                       callback_data=MenuCallback(
                           level=level,
                           menu_name=menu_name,
                           category=category,
                           page=page - 1).pack()))
    return keyboard.row(*row).as_markup()


def get_user_cart(*, level: int, page: int | None, pagination_btns: dict | None, cocktail_id: int | None,
                  sizes: tuple[int] = (3,)):
    keyboard = InlineKeyboardBuilder()
    if page:
        keyboard.add(InlineKeyboardButton(text='Удалить', callback_data=MenuCallback(
            level=level, menu_name='delete', cocktail_id=cocktail_id, page=page).pack()))
        keyboard.add(InlineKeyboardButton(text='-1', callback_data=MenuCallback(
            level=level, menu_name='decrement', cocktail_id=cocktail_id, page=page).pack()))
        keyboard.add(InlineKeyboardButton(text='+1', callback_data=MenuCallback(
            level=level, menu_name='increment', cocktail_id=cocktail_id, page=page).pack()))
        keyboard.adjust(*sizes)

        row = []
        for text, menu_name in pagination_btns.items():
            if menu_name == "next":
                row.append(InlineKeyboardButton(text=text, callback_data=MenuCallback(
                    level=level, menu_name=menu_name, page=page + 1).pack()))
            elif menu_name == "previous":
                row.append(InlineKeyboardButton(text=text, callback_data=MenuCallback(
                    level=level, menu_name=menu_name, page=page - 1).pack()))
        keyboard.row(*row)

        row2 = [
            InlineKeyboardButton(text='На главную 🏠', callback_data=MenuCallback(level=0, menu_name='main').pack()),
            InlineKeyboardButton(text='Заказать', callback_data=MenuCallback(level=4, menu_name='table').pack()),
        ]
        return keyboard.row(*row2).as_markup()
    else:
        keyboard.add(
            InlineKeyboardButton(text='На главную 🏠', callback_data=MenuCallback(level=0, menu_name='main').pack()))
        return keyboard.adjust(*sizes).as_markup()


def get_table_btns(*, level: int, sizes: tuple[int] = (5,)):
    keyboard = InlineKeyboardBuilder()
    for table_number in range(1, 6):
        keyboard.add(
            InlineKeyboardButton(text=f'Стол {table_number}', callback_data=MenuCallback(
                level=5, table_number=table_number, menu_name='order').pack())),
    keyboard.add(
        InlineKeyboardButton(text='Назад', callback_data=MenuCallback(level=level-1, menu_name='cart').pack())),
    return keyboard.adjust(*sizes).as_markup()


def get_order_btns(*, level: int, sizes: tuple[int] = (2,)):
    keyboard = InlineKeyboardBuilder()
    keyboard.add(
        InlineKeyboardButton(text='Оплата в боте', callback_data=MenuCallback(level=level, menu_name='pay').pack())),
    keyboard.add(
        InlineKeyboardButton(text='Оплата на месте', callback_data=MenuCallback(level=6, menu_name='pay2').pack())),
    return keyboard.adjust(*sizes).as_markup()


def end_pay_btns(*, sizes: tuple[int] = (1,)):
    keyboard = InlineKeyboardBuilder()
    keyboard.add(
        InlineKeyboardButton(text='На главную 🏠', callback_data=MenuCallback(level=0, menu_name='main').pack())),
    return keyboard.adjust(*sizes).as_markup()


def get_callback_btns(*, btns: dict[str, str], sizes: tuple[int] = (2,)):
    keyboard = InlineKeyboardBuilder()
    for text, data in btns.items():
        keyboard.add(InlineKeyboardButton(text=text, callback_data=data))
    return keyboard.adjust(*sizes).as_markup()
