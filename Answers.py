# Это форма заполнения заявки
import uuid
from __main__ import dp
from datetime import datetime, date
from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command, CommandStart, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import default_state, State, StatesGroup
from aiogram.types import (CallbackQuery, InlineKeyboardButton,InlineKeyboardMarkup, Message, PhotoSize)
user_dict: dict[int, dict[str, str | int | bool]] = {}
class FSMForm(StatesGroup):
    fill_TicketId = uuid.uuid3()
    fill_CreationDate =  datetime.now()
    fill_TicketAuthor = State()
    fill_VisitDate = State()
    fill_VisitTime = State()
    fill_GroundNum = State()
    fill_Task = State()
    fill_Price = State()
    fill_Advance = State()
    fill_PhoneNum1 = State()
    fill_PhoneNum2 = State()
    fill_Source = State()
    fill_Link = State()
    upload_photo = State()
    upload = State()



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
    await state.update_data(VisitDate=message.text)

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
            await callback.message.answer(text='Введите имя заказчика')
            await state.set_state(FSMForm.Name)
            await state.update_data(Name=message.text)
        else:
            await callback.message.answer(text='Неверная дата. Пожалуйста, введите дату в формате yyyy-mm-dd, не ранее сегодняшнего дня и не позднее 100 дней от сегодняшнего.')
    except ValueError:
        await callback.message.answer(text='Неверный формат даты. Пожалуйста, введите дату в формате yyyy-mm-dd.')
@dp.message(StateFilter(FSMForm.fill_TicketAuthor))
async def warning_not_name(message: Message):
    await message.answer(
        text='То, что вы отправили не похоже на имя\n\n'
            'Пожалуйста, введите ваше имя\n\n'
            'Если вы хотите прервать заполнение анкеты - '
            'отправьте команду /cancel'
    )
@dp.message(StateFilter(FSMForm.fill_VisitTime))
async def Visit_Time():
    FirstPart = InlineKeyboardButton(text='Первая половина дня\n(До 12:00)', callback_data='FirstPart')
    SecondPart = InlineKeyboardButton(text='Вторая половина дня\n(После 12:00)', callback_data='SecondPart')
    Morning = InlineKeyboardButton(text='Утро', callback_data='Morning')
    Day = InlineKeyboardButton(text='День', callback_data='Day')
    Evening = InlineKeyboardButton(text='Вечер', callback_data='Evening')

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [FirstPart, SecondPart],
        [Morning, Day, Evening],
    ])
    await state.update_data(VisitTime=message.text)
    return keyboard




@dp.message_handler(StateFilter(FSMForm.fill_GroundNum, FSMForm.fill_Task, FSMForm.fill_Price))
async def Price_(message: types.Message, state: FSMContext):
    if state == FSMForm.fill_GroundNum:
        text = 'Введите кадастровый номер (ориентира или земельного участка)'
        await state.update_data(GroundNum=message.text)
    elif state == FSMForm.fill_Task:
        text = 'Введите суть заявки'
        await state.update_data(Task=message.text)
    elif state == FSMForm.fill_Price:
        text = 'Введите стоимость заявки'
        await state.update_data(Price=message.text)
        return

    await message.answer(text)

@dp.message(StateFilter(FSMForm.fill_Advance))
async def Advance(message: types.Message, state: FSMContext):
    await message.answer('Предоплата?', reply_markup=await Advance_keyboard(state))
    await state.update_data(Advance=message.text)

async def Advance_keyboard(state: FSMContext):
    Half = InlineKeyboardButton(text='Половина на выезде', callback_data='Half')
    Already = InlineKeyboardButton(text='Уже оплачен', callback_data='Already')
    Office = InlineKeyboardButton(text='Полную сумму  в офисе', callback_data='Office')
    Another = InlineKeyboardButton(text='Иное', callback_data='Another')
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [Half, Already],
        [Office, Another],
    ])
    return keyboard

@dp.message(StateFilter(FSMForm.fill_PhoneNum1))
async def PhoneNum1(message: types.Message, state: FSMContext):
    await message.answer('Контакт заказчика и пояснение',)
    await state.update_data(Phone1=message.text)

@dp.message_handler(StateFilter(FSMForm.fill_PhoneNum2))
async def Phone2_quest(message: types.Message, state: FSMContext):
    await message.answer('Будет ли второй контакт?', reply_markup=await Phone2_Answer(state))
    await state.set_state(FSMForm.fill_PhoneNum2)

@dp.callback_query_handler(StateFilter(FSMForm.fill_PhoneNum2))
async def Phone2_answer(call: types.CallbackQuery, state: FSMContext):
    await call.answer()

    if call.data == 'Yes':
        await call.message.edit_text('Напишите второй контакт с пояснением')
        await state.update_data(Phone2=message.text)
    else :
        await state.update_data(Phone2='-')

async def Phone2_Answer(state: FSMContext):
    Yes = InlineKeyboardButton(text='Да', callback_data='Yes')
    No = InlineKeyboardButton(text='Нет', callback_data='No')
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [Yes, No],
    ])
    return keyboard

@dp.message(StateFilter(FSMForm.fill_Source))
async def Source_Answer(message: types.Message, state: FSMContext):
    await message.answer('Выберите источник заявки',reply_markup=await Source_question(state))
    await state.update_data(Source=message.text)
async def Source_question(state: FSMContext):
    MyselfAvio = InlineKeyboardButton(text='Я Авито', callback_data='MyselfAvio')
    MyselfSarafan = InlineKeyboardButton(text='Я Сарафан', callback_data='MyselfSarafan')
    AvitoUser = InlineKeyboardButton(text='Авито пользователь', callback_data='AvitoUser')
    SarafanUser = InlineKeyboardButton(text='Сарафан пользователь', callback_data='SarafanUser')
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [MyselfAvio,MyselfSarafan],
        [AvitoUser,SarafanUser],
    ])
    return keyboard
@dp.message(StateFilter(FSMForm.fill_Link))
async def process_photo_sent(message: types.Message, state: FSMContext):
    await message.answer('Введите ссылку на карту')
    await state.update_data(Link=message.text)

@dp.message(StateFilter(FSMForm.upload_photo),
            F.photo[-1].as_('largest_photo'))
async def process_photo_sent(message: Message,
                            state: FSMContext,
                            largest_photo: PhotoSize):
    await state.update_data(
        photo_unique_id=largest_photo.file_unique_id,
        photo_id=largest_photo.file_id
    )

@dp.message(StateFilter(FSMForm.upload))
async def show_data(message: types.Message, state: FSMContext):
    if message.from_user.id in user_dict:
        await message.answer_photo(
            photo=user_dict[message.from_user.id]['photo_id'],
            caption=f'Имя: {user_dict[message.from_user.id]["Name"]}\n'
                    f'День визита: {user_dict[message.from_user.id]["VisitDate"]}\n'
                    f'Время визита: {user_dict[message.from_user.id]["VisitTime"]}\n'
                    f'Кадастровый номер: {user_dict[message.from_user.id]["GroundNum"]}\n'
                    f'Суть заявки: {user_dict[message.from_user.id]["Task"]}\n'
                    f'Стоимость: {user_dict[message.from_user.id]["Price"]}\n'
                    f'Предоплата: {user_dict[message.from_user.id]["Advance"]}\n'
                    f'Телефон: {user_dict[message.from_user.id]["Phone1"]}\n'
                    f'Второй телефон: {user_dict[message.from_user.id]["Phone2"]}\n'
                    f'Источник заявки: {user_dict[message.from_user.id]["Source"]}\n'
                    f'Ссылка на карту: {user_dict[message.from_user.id]["Link"]}\n'
        )
    else:

        await message.answer(
            text='Вы еще не заполняли анкету. Чтобы приступить - '
            'отправьте команду /start'
        )
        await state.clear()
@dp.message(StateFilter(default_state))
async def send_echo(message: Message):
    await message.reply(text='Извините, я вас не понимаю')


