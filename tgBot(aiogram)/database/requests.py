from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete
from sqlalchemy.orm import joinedload

from database.engine import async_session
from database.models import User, Category, Cocktail, Banner, Cart, Order, Table


# ########################### Banner ######################################

async def orm_get_banners(session: AsyncSession):
    query = select(Banner)
    result = await session.execute(query)
    return result.scalars().all()


async def orm_add_banner(session: AsyncSession, data: dict):
    new_cocktail = Banner(
        name=data['name'],
        image=data['image'],
        description=data['description'],
    )
    session.add(new_cocktail)
    await session.commit()


async def orm_update_banner(session: AsyncSession, banner_id: int, data: dict):
    query = update(Banner).where(Banner.id == banner_id).values(
        name=data['name'],
        description=data['description'],
        image=data['image'],
    )
    await session.execute(query)
    await session.commit()


async def orm_get_banner(session: AsyncSession, page: str):
    query = select(Banner).where(Banner.name == page)
    result = await session.execute(query)
    return result.scalar()


async def orm_get_info_pages(session: AsyncSession):
    query = select(Banner)
    result = await session.execute(query)
    return result.scalars().all()


# ########################### Category ######################################

async def orm_get_categories(session: AsyncSession):
    query = select(Category)
    result = await session.execute(query)
    return result.scalars().all()


async def orm_add_category(session: AsyncSession, data: dict):
    new_category = Category(
        name=data['name']
    )
    session.add(new_category)
    await session.commit()


async def orm_delete_category(session: AsyncSession, category_id: int):
    query = delete(Category).where(Category.id == category_id)
    await session.execute(query)
    await session.commit()


# ########################### Cocktail ######################################

async def orm_get_cocktails(session: AsyncSession, category_id):
    query = select(Cocktail).where(Cocktail.category_id == int(category_id))
    result = await session.execute(query)
    return result.scalars().all()


async def orm_get_cocktail(session: AsyncSession, cocktail_id: int):
    query = select(Cocktail).where(Cocktail.id == cocktail_id)
    result = await session.execute(query)
    return result.scalar()


async def orm_add_cocktail(session: AsyncSession, data: dict):
    new_cocktail = Cocktail(
        name=data['name'],
        compound=data['compound'],
        price=float(data['price']),
        image_url=data['image_url'],
        category_id=int(data['category_id']),
    )
    session.add(new_cocktail)
    await session.commit()


async def orm_update_cocktail(session: AsyncSession, cocktail_id: int, data):
    query = update(Cocktail).where(Cocktail.id == cocktail_id).values(
        name=data['name'],
        compound=data['compound'],
        price=float(data['price']),
        image_url=data['image_url'],
        category_id=data['category_id'],
    )
    await session.execute(query)
    await session.commit()


async def orm_delete_cocktail(session: AsyncSession, cocktail_id: int):
    query = delete(Cocktail).where(Cocktail.id == cocktail_id)
    await session.execute(query)
    await session.commit()


# ########################### User ######################################

async def orm_add_user(session: AsyncSession, user_id: int, first_name: str | None = None, last_name: str | None = None,
                       username: str | None = None):
    query = select(User).where(User.user_id == user_id)
    result = await session.execute(query)
    if result.first() is None:
        session.add(User(user_id=user_id, first_name=first_name, last_name=last_name, username=username))
        await session.commit()


# ########################### Cart ######################################

async def orm_add_to_cart(session: AsyncSession, user_id: int, cocktail_id: int):
    query = select(Cart).where(Cart.user_id == user_id, Cart.cocktail_id == cocktail_id)
    cart = await session.execute(query)
    cart = cart.scalar()
    if cart:
        cart.quantity += 1
        await session.commit()
        return cart
    else:
        session.add(Cart(user_id=user_id, cocktail_id=cocktail_id, quantity=1))
        await session.commit()


async def orm_get_user_carts(session: AsyncSession, user_id):
    query = select(Cart).filter(Cart.user_id == user_id).options(joinedload(Cart.cocktail))
    result = await session.execute(query)
    return result.scalars().all()


async def orm_delete_from_cart(session: AsyncSession, user_id: int, cocktail_id: int):
    query = delete(Cart).where(Cart.user_id == user_id, Cart.cocktail_id == cocktail_id)
    await session.execute(query)
    await session.commit()


async def orm_reduce_product_in_cart(session: AsyncSession, user_id: int, cocktail_id: int):
    query = select(Cart).where(Cart.user_id == user_id, Cart.cocktail_id == cocktail_id)
    cart = await session.execute(query)
    cart = cart.scalar()

    if not cart:
        return
    if cart.quantity > 1:
        cart.quantity -= 1
        await session.commit()
        return True
    else:
        await orm_delete_from_cart(session, user_id, cocktail_id)
        await session.commit()
        return False


# ########################### Order ######################################

async def orm_get_order(session: AsyncSession, user_id):
    query = select(Order).where(Order.user_id == int(user_id))
    result = await session.execute(query)
    return result.scalars().all()


async def orm_add_order(session: AsyncSession, table_number: int, user_id: int, cocktail_id: int, quantity: int):
    new_order = Order(
        table_number=table_number,
        user_id=user_id,
        cocktail_id=cocktail_id,
        quantity=quantity,
    )
    session.add(new_order)
    await session.commit()


# ########################### Table ######################################

async def orm_get_tables(session: AsyncSession):
    query = select(Table)
    result = await session.execute(query)
    return result.scalars().all()

