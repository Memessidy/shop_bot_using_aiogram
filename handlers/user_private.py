from aiogram import types, Router, F
from aiogram.filters import CommandStart, Command, or_f
from sqlalchemy.ext.asyncio import AsyncSession

from database.orm_query import orm_get_products
from filters.chat_types import ChatTypeFilter
from aiogram.utils.formatting import as_list, as_marked_section, Bold
from kbds.reply import get_keyboard

user_private_router = Router()
user_private_router.message.filter(ChatTypeFilter(['private']))


@user_private_router.message(CommandStart())
async def start_cmd(message: types.Message):
    await message.answer(
        "Вітаю, я віртуальний помічник!",
        reply_markup=get_keyboard(
            "Меню",
            "Про магазин",
            "Варіанти оплати",
            "Варіанти доставки",
            placeholder="Що вас цікавить??",
            sizes=(2, 2)
        ),
    )


@user_private_router.message(or_f((Command('menu')), (F.text.lower() == "меню")))
async def menu_cmd(message: types.Message, session: AsyncSession):
    await message.answer('Ось меню: ')
    for product in await orm_get_products(session):
        await message.answer_photo(
            product.image,
            caption=f"<strong>{product.name}</strong>\n"
                    f"{product.description}\n"
                    f"Ціна: {round(product.price, 2)}")


@user_private_router.message(F.text.lower() == 'про магазин')
@user_private_router.message(Command('about'))
async def about_cmd(message: types.Message):
    await message.answer('Тут продається щось')


@user_private_router.message((F.text.lower().contains('оплат')) | (F.text.lower() == 'варіати оплати'))
@user_private_router.message(Command('payment'))
async def payments_cmd(message: types.Message):
    text = as_marked_section(
        Bold("Варіанти сплати:"),
        "Картою в боті",
        "При отриманні",
        "В закладі",
        marker='✅'
    )
    await message.answer(text.as_html())


@user_private_router.message((F.text.lower().contains('доставк')) | (F.text.lower() == 'варіати доставки'))
@user_private_router.message(Command('shipping'))
async def shipping_cmd(message: types.Message):
    text = as_list(
        as_marked_section(
            Bold("Варіанти доставки заказу:"),
            "Кур'єром",
            "Самовивіз",
            "Забронювати місце",
            marker='✅'
        ),
        as_marked_section(
            Bold("Неможливо"),
            "Пошта",
            "Голуб",
            marker='❌'
        ),
        sep='\n-----------------------------------------\n'
    )
    await message.answer(text.as_html())

# @user_private_router.message(F.contact)
# async def get_contact(message: types.Message):
#     await message.answer(f"номер отриманий!")
#     await message.answer(str(message.contact))
#     await message.answer(str(message.contact.phone_number))
#
#
# @user_private_router.message(F.location)
# async def get_location(message: types.Message):
#     await message.answer(f"локація отримана!")
#     await message.answer(str(message.location))
