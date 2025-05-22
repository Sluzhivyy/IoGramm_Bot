from aiogram.types import (CallbackQuery, InlineKeyboardButton,InlineKeyboardMarkup, Message, PhotoSize, WebAppInfo)
from datetime import datetime, date, timedelta

def veb_site():
    keyboard = InlineKeyboardMarkup()
    web_app_button = InlineKeyboardButton("Открыть публичную кадастровую карту", web_app=WebAppInfo(url="https://lk1map.roscadastres.com/map/kaliningradskaya-oblast/kaliningrad"))
    keyboard.add(web_app_button)



# Функции для создания клавиатур
def Info_keyboard():
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text = "Начать заполнение формы", callback_data='form')]
        ]
    )
    return keyboard

def create_menu_keyboard():
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text='Заполнить форму', callback_data='form')],
            [InlineKeyboardButton(text='Информация о функционале', callback_data='info')]
        ]
    )
    return keyboard

def create_work_keyboard():
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text='Техплан жилой дом', callback_data='Техплан жилой дом')],
            [InlineKeyboardButton(text='Техплан гараж', callback_data='Техплан гараж')],
            [InlineKeyboardButton(text='Техплан постройка', callback_data='Техплан постройка')],
            [InlineKeyboardButton(text='Вернуться в главное меню', callback_data='GoBack')]
        ]
    )
    return keyboard

def create_date_keyboard():
    today = date.today()
    tomorrow = today + timedelta(days=1)
    dates = [today + timedelta(days=i) for i in range(2, 6)]

    buttons = [
        [InlineKeyboardButton(text='Без выезда', callback_data='Без выезда')],
        [InlineKeyboardButton(text='Сегодня', callback_data=f'date:{today.isoformat()}'),
        InlineKeyboardButton(text='Завтра', callback_data=f'date:{tomorrow.isoformat()}')]
    ]

    # Добавляем кнопки с датами в два ряда
    for i in range(0, len(dates), 2):
        row = []
        if i < len(dates):
            row.append(InlineKeyboardButton(text=f'{dates[i].strftime("%d.%m.%y")} ({dates[i].strftime("%a")[:2].capitalize()})', callback_data=f'date:{dates[i].isoformat()}'))
        if i + 1 < len(dates):
            row.append(InlineKeyboardButton(text=f'{dates[i + 1].strftime("%d.%m.%y")} ({dates[i + 1].strftime("%a")[:2].capitalize()})', callback_data=f'date:{dates[i + 1].isoformat()}'))
        buttons.append(row)

    # Добавляем кнопку для возврата в главное меню
    buttons.append([InlineKeyboardButton(text='В главное меню', callback_data='menu')])

    # Создаем клавиатуру
    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard


def create_time_keyboard():
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text='Не важно', callback_data='Не важно')],
            [InlineKeyboardButton(text='Первая половина дня', callback_data='Первая половина дня')],
            [InlineKeyboardButton(text='Вторая половина дня', callback_data='Вторая половина дня')],
            [InlineKeyboardButton(text='Утро (первой заявкой)', callback_data='Утро (первой заявкой)')],

        ]
    )
    return keyboard

def create_ground_keyboard():
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text='Вернуться в главное меню', callback_data='menu')]
        ]
    )
    return keyboard

def create_phon_keyboard():
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text='Вернуться в главное меню', callback_data='menu')]
        ]
    )
    return keyboard

def create_task_keyboard():
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text='Вернуться в главное меню', callback_data='menu')]
        ]
    )
    return keyboard

def create_publish_keyboard():
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text='Опубликовать заявку', callback_data='publish')],
            [InlineKeyboardButton(text='Отмена', callback_data='cancel')]
        ]
    )
    return keyboard