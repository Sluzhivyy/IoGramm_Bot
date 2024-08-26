from aiogram.types import (CallbackQuery, InlineKeyboardButton,InlineKeyboardMarkup, Message, PhotoSize)
from datetime import datetime, date, timedelta




# Функция для создания клавиатуры меню
def create_menu_keyboard():
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text='Заполнить форму', callback_data='form')],
            [InlineKeyboardButton(text='Информация о функционале', callback_data='info')]
        ]
    )
    return keyboard


#Клавиатура для выбора типа работы
def create_work_keyboard():
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text='Техплан жилой дом', callback_data='Техплан жилой дом')],
            [InlineKeyboardButton(text='Техплан гараж', callback_data='Техплан гараж')],
            [InlineKeyboardButton(text='Техплан постройка ', callback_data='Техплан постройка ')],
            [InlineKeyboardButton(text='Вернуться в главное меню', callback_data='GoBack')]
        ]
    )
    return keyboard
#Клавиатура выбора даты
def create_date_keyboard():
    today = date.today()
    tomorrow = today + timedelta(days=1)
    dates = [today + timedelta(days=i) for i in range(2, 6)]
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
        [InlineKeyboardButton(text='Без выезда', callback_data='Без выезда')],
        [InlineKeyboardButton(text='Сегодня', callback_data=f'date:{today.isoformat()}')],
        [InlineKeyboardButton(text='Завтра', callback_data=f'date:{tomorrow.isoformat()}')],
        [InlineKeyboardButton(text=f'{d.strftime("%d.%m.%y")} ({d.strftime("%a")[:2].capitalize()})',callback_data=f'date:{d.isoformat()}') for d in dates],
        [InlineKeyboardButton(text='В главное меню', callback_data='menu')]
        ]
    )
    return keyboard

#Клавиатура выбора времени
def create_time_keyboard():
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text='Не важно', callback_data='Не важно')],
            [InlineKeyboardButton(text='Первая половина дня', callback_data='Первая половина дня')],
            [InlineKeyboardButton(text='Вторая половина дня', callback_data='Вторая половина дня')],
            [InlineKeyboardButton(text='Утро (первой заявкой)', callback_data='Утро (первой заявкой)')],
            [InlineKeyboardButton(text='Отменить ввод', callback_data='Отменить ввод')],
            [InlineKeyboardButton(text='Назад', callback_data='Назад')]
        ]
    )
    return keyboard

# Клавиатура выбора варианта для земельного участка
def create_ground_keyboard():
    keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text='Ввести кадастровый позже', callback_data='Later')],
                [InlineKeyboardButton(text='Назад', callback_data='Back')],
                [InlineKeyboardButton(text='Отменить ввод', callback_data='menu')]
            ]
        )
    return keyboard
# Клавиатура для выбора варианта задачи
def create_task_keyboard():
    keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text='Назад', callback_data='Back')],
                [InlineKeyboardButton(text='Ввести позже', callback_data='Later')],
                [InlineKeyboardButton(text='Отменить ввод', callback_data='menu')]

            ]
        )
    return keyboard