from aiogram import F, Router, types
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command, StateFilter, or_f
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State

from sqlalchemy.ext.asyncio import AsyncSession

from filters.chat_types import ChatTypes, IsAdmin

from database.requests import (orm_get_categories, orm_add_category, orm_get_cocktail, orm_delete_cocktail,
                               orm_delete_category, orm_add_cocktail, orm_update_cocktail, orm_get_cocktails,
                               orm_get_banners, orm_add_banner, orm_update_banner)

from keyboards.reply import get_keyboard
from keyboards.inline import get_callback_btns


admin_router = Router()
admin_router.message.filter(ChatTypes(["private"]), IsAdmin())


ADMIN_KB = get_keyboard(
    "Mеню",
    "Добавить коктейль",
    "Изменить коктейль",
    "Удалить коктейль",
    'Добавить категорию',
    'Удалить категорию',
    'Добавить баннер',
    'Изменить баннер',
    placeholder='Выберите опцию...',
    sizes=(3,),
)


@admin_router.message(Command('admin'))
async def admin(message: Message):
    await message.answer("Что хотите сделать?", reply_markup=ADMIN_KB)


@admin_router.message(F.text == 'Mеню')
async def menu_handler(message: Message, session: AsyncSession):
    categories = await orm_get_categories(session)
    btns = {category.name: f'category_{category.id}' for category in categories}
    await message.answer("Выберите категорию", reply_markup=get_callback_btns(btns=btns))


@admin_router.callback_query(F.data.startswith('category_'))
async def category_menu(callback: types.CallbackQuery, session: AsyncSession):
    category_id = callback.data.split('_')[-1]
    for cocktail in await orm_get_cocktails(session, int(category_id)):
        await callback.message.answer_photo(
            cocktail.image_url,
            caption=f'<strong>{cocktail.name}</strong>\n{cocktail.compound}\nСтоимость: {cocktail.price}€',
            reply_markup=get_callback_btns(
                btns={'Удалить': f'delete_{cocktail.id}', 'Изменить': f'update_{cocktail.id}'}, sizes=(2,)))
    await callback.answer()


# ########################### Category ######################################

class AddCategory(StatesGroup):
    name = State()


@admin_router.message(StateFilter(None), F.text == 'Добавить категорию')
async def add_category(message: Message, state: FSMContext):
    await message.answer('Введите название категории', reply_markup=get_keyboard(
        'Отмена',
        sizes=(1,)
    ))
    await state.set_state(AddCategory.name)


@admin_router.message(AddCategory.name, F.text)
async def add_category_name(message: Message, state: FSMContext, session: AsyncSession):
    await state.update_data(name=message.text)
    data = await state.get_data()
    await orm_add_category(session, data)
    await message.answer('Категория добавлена', reply_markup=ADMIN_KB)
    await state.clear()


@admin_router.message(F.text == 'Удалить категорию')
async def delete_category(message: Message, session: AsyncSession):
    for category in await orm_get_categories(session):
        await message.answer(f'{category.name}', reply_markup=get_callback_btns(btns={
            'Удалить': f'del_{category.id}',
        }))


@admin_router.callback_query(F.data.startswith('del_'))
async def cmd_delete_category(callback: types.CallbackQuery, session: AsyncSession):
    category_id = callback.data.split('_')[-1]
    await orm_delete_category(session, int(category_id))
    await callback.answer('Категория удалена')
    await callback.message.answer('Категория удалена')


# ########################### Banner ######################################

class AddBanner(StatesGroup):
    name = State()
    description = State()
    image = State()

    banner_for_update = None


@admin_router.message(StateFilter(None), F.text == 'Изменить баннер')
async def banner(message: Message, state: FSMContext, session: AsyncSession):
    banners = await orm_get_banners(session)
    btns = {banner.name: banner.name for banner in banners}
    await message.answer('Выберите баннер для изменения', reply_markup=get_callback_btns(btns=btns))
    await state.set_state(AddBanner.name)


@admin_router.message(StateFilter(None), F.text == 'Добавить баннер')
async def add_banner(message: types.Message, state: FSMContext):
    await message.answer(
        "Введите название banner", reply_markup=types.ReplyKeyboardRemove()
    )
    await state.set_state(AddBanner.name)


@admin_router.callback_query(AddBanner.name)
async def banner_name(callback: types.CallbackQuery, state: FSMContext, session: AsyncSession):
    banner_names = [banner.name for banner in await orm_get_banners(session)]
    if callback.data in banner_names:
        AddBanner.banner_for_update = next(b for b in await orm_get_banners(session) if b.name == callback.data)
        await callback.answer()
        await state.update_data(name=callback.data)
        await callback.message.answer('Теперь введите описание баннера.')
        await state.set_state(AddBanner.description)
    else:
        await callback.message.answer('Выберите катеорию из кнопок.')
        await callback.answer()


@admin_router.message(AddBanner.name, F.text)
async def add_name(message: types.Message, state: FSMContext):
    if message.text == "." and AddBanner.banner_for_update:
        await state.update_data(name=AddBanner.banner_for_update.name)
    else:
        if 4 >= len(message.text) >= 150:
            await message.answer(
                "Название товара не должно превышать 150 символов\nили быть менее 5ти символов. \n Введите заново"
            )
            return
        await state.update_data(name=message.text)
        await message.answer("Введите описание товара")
        await state.set_state(AddBanner.description)


@admin_router.message(AddBanner.name)
async def error_banner_name(message: types.Message, state: FSMContext):
    await message.answer('Выберите катеорию из кнопок.')


@admin_router.message(AddBanner.description, F.text)
async def update_banner_description(message: Message, state: FSMContext):
    if message.text == '.' and AddBanner.banner_for_update:
        await state.update_data(description=AddBanner.banner_for_update.description)
    else:
        await state.update_data(description=message.text)
    await message.answer('Отправьте фото баннера')
    await state.set_state(AddBanner.image)


@admin_router.message(AddBanner.description)
async def error_banner_description(message: types.Message, state: FSMContext):
    await message.answer('Ввведите описание баннера')


@admin_router.message(AddBanner.image, or_f(F.photo, F.text == "."))
async def add_banner2(message: Message, state: FSMContext, session: AsyncSession):
    if message.text and message.text == '.' and AddBanner.banner_for_update:
        await state.update_data(image=AddBanner.banner_for_update.image)
    elif message.photo:
        await state.update_data(image=message.photo[-1].file_id)
    else:
        await message.answer("Отправьте фото баннера")
        return
    data = await state.get_data()
    try:
        if AddBanner.banner_for_update:
            await orm_update_banner(session, AddBanner.banner_for_update.id, data)
            await message.answer("Баннер изменен", reply_markup=ADMIN_KB)
            await state.clear()
        else:
            await orm_add_banner(session, data)
            await message.answer("Баннер добавлен", reply_markup=ADMIN_KB)
            await state.clear()

    except Exception as e:
        await message.answer(
            f"Ошибка: \n{str(e)}\nОбратись к программеру, он опять денег хочет",
            reply_markup=ADMIN_KB,
        )
        await state.clear()


@admin_router.message(AddBanner.image)
async def error_banner_image(message: types.Message, state: FSMContext):
    await message.answer('Отправьте фото баннера')


# ########################### Cocktail ######################################

class AddCocktail(StatesGroup):
    name = State()
    compound = State()
    price = State()
    image_url = State()
    category_id = State()

    cocktail_for_update = None

    texts = {
        'AddCocktail:name': 'Введите название коктейля заново:',
        'AddCocktail:compound': 'Введите компонеты коктейля заново:',
        'AddCocktail:price': 'Введите стоимость коктейля заново:',
        'AddCocktail:image_url': 'Добавте фото заново:',
    }


@admin_router.message(F.text.casefold() == 'назад')
async def chanel_handler(message: Message, state: FSMContext):
    current_state = await state.get_state()
    previous = None
    for step in AddCocktail.__all_states__:
        if step.state == current_state:
            await state.set_state(previous)
            await message.answer(f' \n {AddCocktail.texts[previous.state]}')
            return
        previous = step


@admin_router.message(StateFilter('*'), F.text.casefold() == 'отмена')
async def chanel_handler(message: Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state is None:
        return
    if AddCocktail.cocktail_for_update:
        AddCocktail.cocktail_for_update = None
    await state.clear()
    await message.answer('Действия отменены', reply_markup=ADMIN_KB)


@admin_router.message(StateFilter(None), F.text == 'Добавить коктейль')
async def add_cocktail(message: Message, state: FSMContext):
    await message.answer('Введите название коктейля', reply_markup=get_keyboard(
        'Отмена',
        sizes=(1,)
    ))
    await state.set_state(AddCocktail.name)


# @admin_router.message(StateFilter(None), F.text == 'Изменить коктейль')
# async def add_cocktail(message: Message, state: FSMContext, session: AsyncSession):
#     cocktail_id = await data.replace('update_', '')
#     cocktail_for_update = await orm_get_cocktail(session, int(cocktail_id))
#     AddCocktail.cocktail_for_update = cocktail_for_update
#     await message.answer('Введите название коктейля', reply_markup=get_keyboard(
#         'Отмена',
#         sizes=(1,)
#     ))
#     await state.set_state(AddCocktail.name)


@admin_router.message(AddCocktail.name, F.text.isupper())
async def add_cocktail_name(message: Message, state: FSMContext):
    if message.text == '.' and AddCocktail.cocktail_for_update:
        await state.update_data(name=AddCocktail.cocktail_for_update.name)
    else:
        if 4 >= len(message.text) >= 150:
            await message.answer(
                "Название товара не должно превышать 150 символов\nили быть менее 5ти символов. \n Введите заново")
            return
        await state.update_data(name=message.text)
    await message.answer('Введите компоненты коктейля', reply_markup=get_keyboard(
        'Назад', 'Отмена', sizes=(2,)))
    await state.set_state(AddCocktail.compound)


@admin_router.message(AddCocktail.name)
async def error_add_name(message: types.Message, state: FSMContext):
    await message.answer("Некоректный ввод. Только большие буквы.\nВведите заново")


@admin_router.message(AddCocktail.compound, F.text)
async def add_cocktail_compound(message: Message, state: FSMContext):
    if message.text == '.' and AddCocktail.cocktail_for_update:
        await state.update_data(compound=AddCocktail.cocktail_for_update.compound)
    else:
        await state.update_data(compound=message.text)
    await message.answer('Введите стоимость', reply_markup=get_keyboard(
        'Назад', 'Отмена',
        sizes=(2,)))
    await state.set_state(AddCocktail.price)


@admin_router.message(AddCocktail.compound)
async def error_add_compound(message: types.Message, state: FSMContext):
    await message.answer("Некоректный ввод.\nВведите заново")


@admin_router.message(AddCocktail.price, F.text)
async def add_cocktail_price(message: Message, state: FSMContext, session: AsyncSession):
    if message.text == '.' and AddCocktail.cocktail_for_update:
        await state.update_data(price=AddCocktail.cocktail_for_update.price)
    else:
        if message.text == float:
            await message.answer("Некоректный ввод.Только числа\nВведите заново")
        await state.update_data(price=message.text)

    categories = await orm_get_categories(session)
    btns = {category.name: str(category.id) for category in categories}
    await message.answer('Выберите категорию', reply_markup=get_callback_btns(btns=btns))
    await state.set_state(AddCocktail.category_id)


@admin_router.message(AddCocktail.price)
async def error_add_price(message: types.Message, state: FSMContext):
    await message.answer("Некоректный ввод.Только числа\nВведите заново")


@admin_router.callback_query(AddCocktail.category_id)
async def add_cocktail_category(callback: CallbackQuery, state: FSMContext, session: AsyncSession):
    if int(callback.data) in [category.id for category in await orm_get_categories(session)]:
        await callback.answer()
        await state.update_data(category_id=callback.data)
        await callback.message.answer('Добавьте ссылку на фото')
        await state.set_state(AddCocktail.image_url)
    else:
        await callback.message.answer('Выберите катеорию из кнопок.')
        await callback.answer()


@admin_router.message(AddCocktail.category_id)
async def error_add_category(message: types.Message, state: FSMContext):
    await message.answer("Некоректный ввод.Выберите катеорию из кнопок.\nВведите заново")


@admin_router.message(AddCocktail.image_url, F.text)
async def add_cocktail_image(message: Message, state: FSMContext, session: AsyncSession):
    if message.text == '.' and AddCocktail.cocktail_for_update:
        await state.update_data(image_url=AddCocktail.cocktail_for_update.image_url)
    else:
        await state.update_data(image_url=message.text)
    data = await state.get_data()
    try:
        if AddCocktail.cocktail_for_update:
            await orm_update_cocktail(session, AddCocktail.cocktail_for_update.id, data)
            await message.answer("Коктейль изменен", reply_markup=ADMIN_KB)
            await state.clear()
        else:
            await orm_add_cocktail(session, data)
        await message.answer('Коктейль добавлен', reply_markup=ADMIN_KB)
        await state.clear()
    except Exception as e:
        await message.answer(f'Ошибка: \n{str(e)}', reply_markup=ADMIN_KB)
        await state.clear()
    AddCocktail.cocktail_for_update = None


@admin_router.message(AddCocktail.image_url)
async def error_add_image(message: types.Message, state: FSMContext):
    await message.answer("Некоректный ввод.\nВведите заново")


@admin_router.callback_query(StateFilter(None), F.data.startswith('update_'))
async def delete_cocktail(callback: types.CallbackQuery, state: FSMContext, session: AsyncSession):
    cocktail_id = callback.data.replace('update_', '')
    cocktail_for_update = await orm_get_cocktail(session, int(cocktail_id))
    AddCocktail.cocktail_for_update = cocktail_for_update
    await callback.answer('Коктейль обновляется!')
    await callback.message.answer('Введите название коктейля', reply_markup=types.ReplyKeyboardRemove())
    await state.set_state(AddCocktail.name)


@admin_router.callback_query(F.data.startswith('delete_'))
async def delete_cocktail(callback: CallbackQuery, session: AsyncSession):
    cocktail_id = callback.data.split('_')[-1]
    await orm_delete_cocktail(session, int(cocktail_id))
    await callback.answer('Коктейль удален!')
    await callback.message.answer('Коктейль удален.')

