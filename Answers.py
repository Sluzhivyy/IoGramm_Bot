# Это форма заполнения заявки
import uuid
from datetime import datetime, date
from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command, CommandStart, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import default_state, State, StatesGroup
from aiogram.types import (CallbackQuery, InlineKeyboardButton,InlineKeyboardMarkup, Message, PhotoSize)
user_dict: dict[int, dict[str, str | int | bool]] = {}
class FSMForm(StatesGroup):
    #-----------------Генерируемые данные-------------------------------------
    fill_TicketId = uuid.uuid4()
    fill_CreationDate =  datetime.now()
    #----------------------------Вписываемые данные------------------------------
    fill_TicketAuthor = State()
    upload_photo = State()
    fill_VisitDate = State()
    fill_VisitTime = State()
@dp.message(commands=['start'])
async def process_start_command(message: types.Message):
    await message.answer(
        text='Чтобы перейти к заполнению анкеты - нажмите кнопку Start',
        reply_markup=generate_start_keyboard()
    )


@dp.message(commands=['cancel'])
async def process_cancel_command(message: types.Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state is None:
        await message.answer(
            text='Вы еще ничего не заполнили\n\n'
                'Чтобы перейти к заполнению анкеты - нажмите кнопку Start',
            reply_markup=generate_start_keyboard()
        )
    else:
        await state.finish()
        await message.answer(
            text='Вы отменили заполнение анкеты\n\n'
                'Чтобы снова перейти к заполнению анкеты - нажмите кнопку Start',
            reply_markup=generate_start_keyboard()
        )


@dp.message(commands=['info'])
async def process_info_command(message: types.Message):
    await message.answer(
        text='Это бот, который позволяет быстро и удобно заполнять формы\n\n'
            'Для начала работы нажмите кнопку Start',
        reply_markup=generate_start_keyboard()
    )


def generate_start_keyboard():
    start = InlineKeyboardButton(text='Start', callback_data='Start')
    cancel = InlineKeyboardButton(text='Cancel', callback_data='Cancel')
    info = InlineKeyboardButton(text='Info', callback_data='Info')
    keyboard = InlineKeyboardMarkup(inline_keyboard=[[start, cancel], [info]])
    return keyboard


@dp.callback_query(lambda c: c.data == 'Start')
async def process_start_button(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.answer(text='Введите дату в формате yyyy-mm-dd', reply_markup=generate_date_keyboard())
    await state.set_state(FSMForm.VisitDate)


def generate_date_keyboard():
    dates = [date.today() + datetime.timedelta(days=i) for i in range(1, 5)]
    keyboard = InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(text=str(d), callback_data=str(d)) for d in dates
    ]])
    return keyboard


@dp.callback_query(lambda c: c.data.isdigit())
async def process_date_sent(callback: types.CallbackQuery, state: FSMContext):
    date_str = callback.data
    try:
        input_date = date.fromisoformat(date_str)
        if input_date >= date.today() and input_date < date.today() + datetime.timedelta(days=100):
            await state.update_data(VisitDate=date_str)
            await callback.message.answer(text='Введите имя')
            await state.set_state(FSMForm.Name)
        else:
            await callback.message.answer(text='Неверная дата. Пожалуйста, введите дату в формате yyyy-mm-dd, не ранее сегодняшнего дня и не позднее 100 дней от сегодняшнего.')
    except ValueError:
        await callback.message.answer(text='Неверный формат даты. Пожалуйста, введите дату в формате yyyy-mm-dd.')

        # Генерация клавиатуры с кнопками частей дня
def generate_date_keyboard():
    FirstPart = InlineKeyboardButton(text='Первая половина дня\n(До 12:00)', callback_data='FirstPart')
    SecondPart = InlineKeyboardButton(text='Вторая половина дня\n(После 12:00)', callback_data='SecondPart')
    Morning = InlineKeyboardButton(text='Утро', callback_data='Morning')
    Day = InlineKeyboardButton(text='Днем', callback_data='Day')
    Evening = InlineKeyboardButton(text='Вечер', callback_data='Evening')

    # Добавляем кнопки для ввода времени
    hours = [InlineKeyboardButton(text=f'{i:02}', callback_data=f'Hour_{i}') for i in range(24)]
    minutes = [InlineKeyboardButton(text=f'{i:02}', callback_data=f'Minute_{i}') for i in range(60)]

    # Разбиваем кнопки на группы по 5 для удобства
    hours_keyboard = [hours[i:i+5] for i in range(0, len(hours), 5)]
    minutes_keyboard = [minutes[i:i+5] for i in range(0, len(minutes), 5)]

    # Создаем клавиатуру
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [FirstPart, SecondPart],
        [Morning, Day, Evening],
        # Добавляем разделы для ввода времени
        [InlineKeyboardButton(text='Часы', callback_data='Hour')],
        *hours_keyboard,  # Разбиваем список кнопок на отдельные ряды
        [InlineKeyboardButton(text='Минуты', callback_data='Minute')],
        *minutes_keyboard
    ])

    return keyboard

# Обработка отправки фото
@dp.message(StateFilter(FSMForm.upload_photo), content_types=types.ContentType.PHOTO)
async def process_photo_sent(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    user_dict[user_id]['Photo'] = message.photo[-1].file_id


    await message.answer(text='Анкета успешно заполнена!')
    await state.finish()

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)