from aiogram.types import InputMediaPhoto
from sqlalchemy.ext.asyncio import AsyncSession

from utils.paginator import Paginator

from database.requests import (
    orm_get_banner,
    orm_get_categories,
    orm_get_cocktails,
    orm_delete_from_cart,
    orm_reduce_product_in_cart,
    orm_add_to_cart,
    orm_get_user_carts,
    orm_add_order)

from keyboards.inline import (
    get_user_main_btns,
    get_user_catalog_btns,
    get_cocktails_btns,
    get_user_cart,
    get_table_btns,
    get_order_btns,
    end_pay_btns)


async def main_menu(session, level, menu_name):
    banner = await orm_get_banner(session, menu_name)
    image = InputMediaPhoto(media=banner.image, caption=banner.description)
    kbds = get_user_main_btns(level=level)
    return image, kbds


async def catalog(session, level, menu_name):
    banner = await orm_get_banner(session, menu_name)
    image = InputMediaPhoto(media=banner.image, caption=banner.description)
    categories = await orm_get_categories(session)
    kbds = get_user_catalog_btns(level=level, categories=categories)
    return image, kbds


def pages(paginator: Paginator):
    btns = dict()
    if paginator.has_previous():
        btns["◀ Пред."] = "previous"

    if paginator.has_next():
        btns["След. ▶"] = "next"

    return btns


async def cocktails(session, level, category, page):
    cocktails = await orm_get_cocktails(session, category_id=category)
    paginator = Paginator(cocktails, page=page)
    cocktail = paginator.get_page()[0]
    image = InputMediaPhoto(
        media=cocktail.image_url,
        caption=f'<strong>{cocktail.name}</strong>\n{cocktail.compound}\nСтоимость: {cocktail.price}€\n\
        <strong>Коктейль {paginator.page} из {paginator.pages}</strong>')

    pagination_btns = pages(paginator)

    kbds = get_cocktails_btns(level=level, category=category, page=page,
                              pagination_btns=pagination_btns, cocktail_id=cocktail.id)

    return image, kbds


async def carts(session, level, menu_name, page, user_id, cocktail_id):
    if menu_name == "delete":
        await orm_delete_from_cart(session, user_id, cocktail_id)
        if page > 1:
            page -= 1
    elif menu_name == "decrement":
        is_cart = await orm_reduce_product_in_cart(session, user_id, cocktail_id)
        if page > 1 and not is_cart:
            page -= 1
    elif menu_name == "increment":
        await orm_add_to_cart(session, user_id, cocktail_id)

    carts = await orm_get_user_carts(session, user_id)
    if not carts:
        banner = await orm_get_banner(session, "cart")
        image = InputMediaPhoto(media=banner.image, caption=f"<strong>{banner.description}</strong>")
        kbds = get_user_cart(level=level, page=None, pagination_btns=None, cocktail_id=None)
    else:
        paginator = Paginator(carts, page=page)
        cart = paginator.get_page()[0]
        cart_price = round(cart.quantity * cart.cocktail.price, 2)
        total_price = round(
            sum(cart.quantity * cart.cocktail.price for cart in carts), 2
        )
        image = InputMediaPhoto(
            media=cart.cocktail.image_url,
            caption=f"<strong>{cart.cocktail.name}</strong>\n{cart.cocktail.price}€ x {cart.quantity} = {cart_price}€\
                    \nКоктейль {paginator.page} из {paginator.pages} в корзине.\n\
                    Общая стоимость коктейлей в корзине {total_price}€",
        )

        pagination_btns = pages(paginator)

        kbds = get_user_cart(
            level=level,
            page=page,
            pagination_btns=pagination_btns,
            cocktail_id=cart.cocktail.id,
        )

    return image, kbds


async def table(level, menu_name):
    if menu_name == 'table':
        kbds = get_table_btns(level=level)
        return kbds


async def order(session, level, menu_name, user_id, table_number):
    if menu_name == 'order':
        carts = await orm_get_user_carts(session, user_id)
        print(f"User with id {user_id} exists:")
        if carts:
            description = '\n'.join([f"<strong>{cart.cocktail.name}</strong>\n{cart.cocktail.price}€ x {cart.quantity} "
                                     f"= {round(cart.quantity * cart.cocktail.price, 2)}€\n- - - - - - -  - - - - -\n"
                                     for cart in carts])
            total_price = round(sum(cart.quantity * cart.cocktail.price for cart in carts), 2)
            message_text = (f"Вы ввели номер стола: <strong>{table_number}</strong>\n\n"
                            f"Общая стоимость коктейлей в чеке: <strong>{total_price}€</strong>\n\n"
                            f"{description}")
            banner = await orm_get_banner(session, "payment")
            image = InputMediaPhoto(media=banner.image, caption=message_text)
            kbds = get_order_btns(level=level)

            for cart in carts:
                await orm_add_order(session, table_number=table_number, user_id=user_id,
                                    quantity=cart.quantity, cocktail_id=cart.cocktail_id)
            return image, kbds


async def pay(session, menu_name):
    if menu_name == 'pay2':
        banner = await orm_get_banner(session, "main")
        image = InputMediaPhoto(media=banner.image, caption=f"Ожидайте ваш заказ")
        kbds = end_pay_btns()
        return image, kbds


async def get_menu_content(session: AsyncSession, level: int, menu_name: str, category: int | None = None,
                           page: int | None = None, cocktail_id: int | None = None, user_id: int | None = None,
                           table_number: int | None = None):
    if level == 0:
        return await main_menu(session, level, menu_name)
    elif level == 1:
        return await catalog(session, level, menu_name)
    elif level == 2:
        return await cocktails(session, level, category, page)
    elif level == 3:
        return await carts(session, level, menu_name, page, user_id, cocktail_id)
    elif level == 4:
        return None, await table(level, menu_name)
    elif level == 5:
        return await order(session, level, menu_name, user_id, table_number)
    elif level == 6:
        return await pay(session, menu_name)
