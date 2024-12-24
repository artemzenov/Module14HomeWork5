from aiogram import Bot
from aiogram import Dispatcher
from aiogram import executor
from aiogram import types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import State
from aiogram.dispatcher.filters.state import StatesGroup
from aiogram.types import ReplyKeyboardMarkup
from aiogram.types import KeyboardButton
from aiogram.types import InlineKeyboardMarkup
from aiogram.types import InlineKeyboardButton
import asyncio
from crud_functions import initiate_db
from crud_functions import get_all_products
from crud_functions import is_included
from crud_functions import add_user


class UserState(StatesGroup):
    age = State()
    growth = State()
    weight = State()
    gender = State()
    activity = State()


class RegistrationState(StatesGroup):
    username = State()
    email = State()
    age = State()
    balance = 1000


initiate_db()

api = ''
bot = Bot(token=api)
dp = Dispatcher(bot, storage=MemoryStorage())

kb_start = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
but_calc = KeyboardButton(text='Рассчитать')
but_info = KeyboardButton(text='Информация')
but_buy = KeyboardButton(text='Купить')
but_reg = KeyboardButton(text='Регистрация')
kb_start.row(but_calc, but_info)
kb_start.row(but_buy, but_reg)

kb_gender = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
but_man = KeyboardButton(text='М')
but_woman = KeyboardButton(text='Ж')
kb_gender.row(but_man, but_woman)

kb_activity = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
but_activity_1 = KeyboardButton(text='1')
but_activity_2 = KeyboardButton(text='2')
but_activity_3 = KeyboardButton(text='3')
but_activity_4 = KeyboardButton(text='4')
but_activity_5 = KeyboardButton(text='5')
kb_activity.row(but_activity_1, but_activity_2, but_activity_3,but_activity_4, but_activity_5)

kb_inline = InlineKeyboardMarkup()
button_inline_calories = InlineKeyboardButton(text='Рассчитать норму калорий', callback_data='calories')
button_inline_formulas = InlineKeyboardButton(text='Формула расчета', callback_data='formulas')
kb_inline.row(button_inline_calories, button_inline_formulas)

kb_buy = InlineKeyboardMarkup()
but_inline_product1 = InlineKeyboardButton(text='Product1', callback_data='product_buying')
but_inline_product2 = InlineKeyboardButton(text='Product2', callback_data='product_buying')
but_inline_product3 = InlineKeyboardButton(text='Product3', callback_data='product_buying')
but_inline_product4 = InlineKeyboardButton(text='Product4', callback_data='product_buying')
kb_buy.row(but_inline_product1, but_inline_product2, but_inline_product3, but_inline_product4)


@dp.message_handler(commands=['start'])
async def start(message):
    await message.answer(f'Привет, {message.from_user["first_name"]}! '
                         f'Я бот помогающий твоему здоровью.', reply_markup=kb_start)


@dp.callback_query_handler(text='formulas')
async def get_formulas(call):
    await call.message.answer('Для мужчины: (10 x вес (кг) + 6.25 x рост (см) – 5 x возраст (г) + 5) x A')
    await call.message.answer('Для женщины: (10 x вес (кг) + 6.25 x рост (см) – 5 x возраст (г) – 161) x A')
    await call.answer()


@dp.message_handler(text=['Рассчитать'])
async def main_menu(message):
    await message.answer('Выберите опцию:', reply_markup=kb_inline)


@dp.callback_query_handler(text='calories')
async def set_gender(call):
    await call.message.answer('Выберите свой пол:', reply_markup=kb_gender)
    await call.answer()
    await UserState.gender.set()


@dp.message_handler(state=UserState.gender)
async def set_activity(message, state):
    await state.update_data(gender=message.text.lower())
    await message.answer('Введите свой уровень активности:\n'
                         '1 - Минимальная активность\n'
                         '2 - Слабая активность\n'
                         '3 - Средняя активность\n'
                         '4 - Высокая активность\n'
                         '5 - Экстра активность', reply_markup=kb_activity)
    await UserState.activity.set()


@dp.message_handler(state=UserState.activity)
async def set_age(message, state):
    await state.update_data(activity=message.text)
    await message.answer('Введите свой возраст:')
    await UserState.age.set()


@dp.message_handler(state=UserState.age)
async def set_growth(message, state):
    await state.update_data(age=int(message.text))
    await message.answer('Введите свой рост:')
    await UserState.growth.set()


@dp.message_handler(state=UserState.growth)
async def set_weight(message, state):
    await state.update_data(growth=int(message.text))
    await message.answer('Введите свой вес:')
    await UserState.weight.set()


@dp.message_handler(state=UserState.weight)
async def send_calories(message, state):
    await state.update_data(weight=int(message.text))
    data = await state.get_data()
    level_activity = {'1': 1.2, '2': 1.375, '3': 1.55,
                      '4': 1.725, '5': 1.9}
    if data['gender'] == 'м':
        result = ((10*data['weight'] + 6.25*data['growth'] - 5*data['age'] + 5) *
                  level_activity.setdefault(data['activity'], level_activity['1']))
    elif data['gender'] == 'ж':
        result = ((10*data['weight'] + 6.25*data['growth'] - 5*data['age'] - 161) *
                  level_activity.setdefault(data['activity'], level_activity['1']))
    else:
        result = None
    if result:
        await message.answer(f'Ваша норма калорий: {round(result, 2)}')
    else:
        await message.answer('Произошла ошибка. Повторите попытку. Введите команду /start')

    await state.finish()


@dp.message_handler(text='Купить')
async def get_buying_list(message):
    for i_product in get_all_products():
        await message.answer(f'Название: {i_product[1]} | Описание: {i_product[2]} | Цена: {i_product[3]}')
        with open(i_product[4], 'rb') as photo:
            await message.answer_photo(photo)
    await message.answer('Выберите продукт для покупки:', reply_markup=kb_buy)


@dp.callback_query_handler(text='product_buying')
async def send_confirm_message(call):
    await call.message.answer('Вы успешно приобрели продукт!')
    await call.answer()


@dp.message_handler(text=['Регистрация'])
async def sign_up(message):
    await message.answer('Введите имя пользователя (только латинский алфавит):')
    await RegistrationState.username.set()


@dp.message_handler(state=RegistrationState.username)
async def set_username(message, state):
    if is_included(message.text):
        await message.answer('Пользователь существует, введите другое имя')
        await RegistrationState.username.set()
    else:
        await state.update_data(username=message.text)
        await message.answer('Введите свой email:')
        await RegistrationState.email.set()


@dp.message_handler(state=RegistrationState.email)
async def set_email(message, state):
    await state.update_data(email=message.text)
    await message.answer('Введите свой возраст:')
    await RegistrationState.age.set()


@dp.message_handler(state=RegistrationState.age)
async def set_age(message, state):
    await state.update_data(age=int(message.text))
    user_info = await state.get_data()
    print(user_info)
    add_user(
        user_info['username'],
        user_info['email'],
        user_info['age'],
        RegistrationState.balance)
    await state.finish()
    await message.answer('Регистрация прошла успешно')


@dp.message_handler()
async def all_messages(message):
    await message.answer('Введите команду /start, чтобы начать общение.')


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
