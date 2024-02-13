from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove, KeyboardButtonPollType
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from typing import Tuple

from aiogram.types import KeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder


def get_keyboard(
        *btns: str,
        placeholder: str = None,
        request_contact: int = None,
        request_location: int = None,
        sizes: Tuple[int, ...] = (2,), ):

    '''
    Parameters request_contact and request_location must be as indexes of btns args for buttons you need.
    Example:
    get_keyboard(
            "Меню",
            "О магазине",
            "Варианты оплаты",
            "Варианты доставки",
            "Отправить номер телефона",
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


del_keyboard = ReplyKeyboardRemove()

# start_kb = ReplyKeyboardMarkup(
#     keyboard=[
#         [
#             KeyboardButton(text='Меню'),
#             KeyboardButton(text='Про нас'),
#         ],
#         [
#             KeyboardButton(text='Варіанти доставки'),
#             KeyboardButton(text='Варіанти сплати')
#         ]
#     ],
#     resize_keyboard=True,
#     input_field_placeholder="Що вас цікавить?"
# )
#
# start_kb_2 = ReplyKeyboardBuilder()
# start_kb_2.add(
#     KeyboardButton(text='Меню'),
#     KeyboardButton(text='Про магазин'),
#     KeyboardButton(text='Варіанти доставки'),
#     KeyboardButton(text='Варіанти сплати')
# )
# start_kb_2.adjust(2, 2)
#
# start_kb_3 = ReplyKeyboardBuilder()
# start_kb_3.attach(start_kb_2)
# start_kb_3.row(KeyboardButton(text='Залишити відгук'))

# test_kb = ReplyKeyboardMarkup(
#     keyboard=[
#         [
#             KeyboardButton(text='Створити опитування', request_poll=KeyboardButtonPollType())
#         ],
#         [
#             KeyboardButton(text='Відправити номер: ☎️', request_contact=True),
#             KeyboardButton(text='Відправити локацію: 📍', request_location=True)
#         ]
#     ],
#     resize_keyboard=True
# )
