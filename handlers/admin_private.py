from aiogram import F, Router, types
from aiogram.filters import Command, StateFilter, or_f
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from sqlalchemy.ext.asyncio import AsyncSession
from database.orm_query import orm_add_product, orm_get_products, orm_delete_product, orm_get_product, \
    orm_update_product
from filters.chat_types import ChatTypeFilter, IsAdmin
from kbds.inline import get_callback_btns
from kbds.reply import get_keyboard

admin_router = Router()
admin_router.message.filter(ChatTypeFilter(["private"]), IsAdmin())

ADMIN_KB = get_keyboard(
    "Добавити товар",
    "Асортимент",
    placeholder="Виберіть дію: ",
    sizes=(2,)
)


# Код для машини станів (FSM)

class AddProduct(StatesGroup):
    # Кроки станів
    name = State()
    description = State()
    price = State()
    image = State()

    product_for_change = None

    texts = {
        'AddProduct:name': 'Введіть назву:',
        'AddProduct:description': 'Введіть опис:',
        'AddProduct:price': 'Введіть вартість:',
        'AddProduct:image': 'Останній стейт! ...',
    }


@admin_router.message(Command("admin"))
async def admin_features(message: types.Message):
    await message.answer("Що хочете зробити?", reply_markup=ADMIN_KB)


@admin_router.message(F.text == "Асортимент")
async def starring_at_product(message: types.Message, session: AsyncSession):
    await message.answer("ОК, ось список товарів: 🛒")
    for product in await orm_get_products(session):
        await message.answer_photo(
            product.image,
            caption=f"<strong>{product.name}</strong>\n"
                    f"{product.description}\n"
                    f"Ціна: {round(product.price, 2)}",
            reply_markup=get_callback_btns(btns={
                'Видалити': f'delete_{product.id}',
                'Змінити': f'change_{product.id}',
            }))


@admin_router.callback_query(F.data.startswith("delete_"))
async def delete_product(callback: types.CallbackQuery, session: AsyncSession):
    product_id = callback.data.split("_")[-1]
    await orm_delete_product(session, int(product_id))

    await callback.answer("Товар видалено!")
    await callback.message.answer("Товар видалено!")


@admin_router.callback_query(StateFilter(None), F.data.startswith("change_"))
async def delete_product_callback(callback: types.CallbackQuery, state: FSMContext, session: AsyncSession):
    product_id = callback.data.split("_")[-1]
    product_for_change = await orm_get_product(session, int(product_id))

    AddProduct.product_for_change = product_for_change
    await callback.answer()
    await callback.message.answer("Введіть назву товару", reply_markup=types.ReplyKeyboardRemove())
    await state.set_state(AddProduct.name)


# Ставимось у стан очікування введення name
@admin_router.message(StateFilter(None), F.text == "Добавити товар")
async def add_product(message: types.Message, state: FSMContext):
    await message.answer(
        "Введіть назву товару:", reply_markup=types.ReplyKeyboardRemove()
    )
    await state.set_state(AddProduct.name)


# Хендлер скасування та скидання стану повинен завжди бути саме тут,
# Після того, як ми тільки перейшли в стан номер 1 (першочерговий порядок фільтрів)
@admin_router.message(StateFilter('*'), Command("скасувати"))
@admin_router.message(StateFilter('*'), F.text.casefold() == "скасувати")
async def cancel_handler(message: types.Message, state: FSMContext) -> None:
    current_state = await state.get_state()
    if current_state is None:
        return

    if AddProduct.product_for_change:
        AddProduct.product_for_change = None

    await state.clear()
    await message.answer("Дії скасовані", reply_markup=ADMIN_KB)


# Вернутся на шаг назад (на прошлое состояние)
@admin_router.message(StateFilter('*'), Command("назад"))
@admin_router.message(StateFilter('*'), F.text.casefold() == "назад")
async def back_step_handler(message: types.Message, state: FSMContext) -> None:
    current_state = await state.get_state()

    if current_state == AddProduct.name:
        await message.answer('Попереднього кроку не існує, введіть назву товару або напишіть "скасувати"')
        return

    previous = None
    for step in AddProduct.__all_states__:
        if step.state == current_state:
            await state.set_state(previous)
            await message.answer(f"Добре, ви повернулися до попереднього кроку \n {AddProduct.texts[previous.state]}")
            return
        previous = step


# Ми отримуємо дані для стану name, а потім змінюємо стан на description
@admin_router.message(AddProduct.name, or_f(F.text, F.text == '.'))
async def add_name(message: types.Message, state: FSMContext):
    if message.text == '.':
        await state.update_data(name=AddProduct.product_for_change.name)
    else:
        if len(message.text) >= 100:
            await message.answer("Назва товару не повинна перевищувати 100 символів. \n Введіть знову.")
            return

        await state.update_data(name=message.text)
    await message.answer("Будь ласка, введіть опис товару")
    await state.set_state(AddProduct.description)


# Хендлер для перехоплення некоректних введень для стану name
@admin_router.message(AddProduct.name)
async def add_name2(message: types.Message, state: FSMContext):
    await message.answer("Ви ввели недопустимі дані. Будь ласка, введіть текст назви товару")


# Ми отримуємо дані для стану description, а потім змінюємо стан на price
@admin_router.message(AddProduct.description, or_f(F.text, F.text == '.'))
async def add_description(message: types.Message, state: FSMContext):
    if message.text == '.':
        await state.update_data(name=AddProduct.product_for_change.description)
    else:
        await state.update_data(description=message.text)
    await message.answer("Будь ласка, введіть вартість товару")
    await state.set_state(AddProduct.price)


# Хендлер для перехоплення некоректних введень для стану description
@admin_router.message(AddProduct.description)
async def add_description2(message: types.Message, state: FSMContext):
    await message.answer("Ви ввели недопустимі дані. Будь ласка, введіть текст опису товару")


# Ми отримуємо дані для стану ціни (price), а потім змінюємо стан на зображення (image)
@admin_router.message(AddProduct.price, or_f(F.text, F.text == '.'))
async def add_price(message: types.Message, state: FSMContext):
    if message.text == '.':
        await state.update_data(price=AddProduct.product_for_change.price)
    else:
        try:
            float(message.text)
        except ValueError:
            await message.answer("Будь ласка, введіть правильне значення ціни")
            return

        await state.update_data(price=message.text)
    await message.answer("Завантажте зображення товару")
    await state.set_state(AddProduct.image)


# Хендлер для перехоплення некоректного введення для стану ціни (price).
@admin_router.message(AddProduct.price)
async def add_price2(message: types.Message, state: FSMContext):
    await message.answer("Ви ввели недопустимі дані. Будь ласка, введіть коштовність товару")


# Ми отримуємо дані для стану зображення (image), а потім виходимо з FSM
@admin_router.message(AddProduct.image, or_f(F.photo, F.text == '.'))
async def add_image(message: types.Message, state: FSMContext, session: AsyncSession):

    if message.text and message.text == '.':
        await state.update_data(image=AddProduct.product_for_change.image)
    else:
        await state.update_data(image=message.photo[-1].file_id)

    data = await state.get_data()
    try:
        if AddProduct.product_for_change:
            await orm_update_product(session, AddProduct.product_for_change.id, data)
        else:
            await orm_add_product(session, data)
        await message.answer("Товар додано", reply_markup=ADMIN_KB)
        await state.clear()
    except Exception as e:
        await message.answer(f"Знайдена помилка: {e}!", reply_markup=ADMIN_KB)
        await state.clear()
    AddProduct.product_for_change = None


@admin_router.message(AddProduct.image)
async def add_image2(message: types.Message, state: FSMContext):
    await message.answer("Відправте фото")
