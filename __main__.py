import uuid
from datetime import datetime, date, timedelta
from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command, CommandStart, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import default_state, State, StatesGroup
from aiogram.types import (CallbackQuery, InlineKeyboardButton,InlineKeyboardMarkup, Message, PhotoSize)
from aiogram.fsm.storage.memory import MemoryStorage
from keyboards import *
from env import BOT_TOKEN
import locale
storage = MemoryStorage()
bot = Bot(BOT_TOKEN)
dp = Dispatcher(storage=storage)
locale.setlocale(locale.LC_ALL, 'ru_RU')
user_dict: dict[int, dict[str, str | int]] = {}

# Определяем состояния для FSM
class FSMForm(StatesGroup):
    menu = State()
    work_type = State()
    fill_VisitDate = State()
    fill_VisitTime = State()
    fill_GroundNum = State()
    fill_PhoneNum = State()
    fill_Task = State()
    fill_Price = State()
    fill_Source = State()
    upload = State()

# Обработчик команды /start
@dp.message(CommandStart())
async def process_start_command(message: Message):
    await message.answer(
        text='Для получения информации - '
            'отправьте команду /info \n'
            'Для перехода в меню, отправьте команду /menu'
    )

# Обработчик команды /cancel
@dp.message(Command(commands='cancel'))
async def process_cancel_command(message: Message, state: FSMContext):
    await message.answer(
        text='Отмена ввода. Вы вернулись в главное меню.'
    )
    await state.clear()

# Обработчик команды /info
@dp.message(Command(commands='info'))
async def process_info_command(message: Message):
    await message.answer(
        text='Это бот, который позволяет быстро и удобно заполнять формы'
    )


# Обработчик команды /menu
@dp.message(Command(commands='menu'))
async def process_menu(message: Message, state: FSMContext):
    await state.set_state(FSMForm.menu)
    await message.answer(text='Вы находитесь в меню, выберите нужную вам опцию', reply_markup=create_menu_keyboard())

# Обработчик сообщений в меню
@dp.message(StateFilter(FSMForm.menu))
async def p_menu(message: Message, state: FSMContext):
    await message.answer(text='Вы находитесь в меню, выберите нужную вам опцию', reply_markup=create_menu_keyboard())

# --- Хендлеры для выбора опций в меню ---
@dp.callback_query(lambda c: c.data == 'form')
async def form_handler(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text(text='Выбери вид работ или введи свой:', reply_markup=create_work_keyboard())
    await state.set_state(FSMForm.work_type)

@dp.callback_query(lambda c: c.data == 'info')
async def info_handler(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text('Это бот, который позволяет быстро и удобно заполнять формы')

    await state.set_state(FSMForm.menu)
    await callback.message.answer(
        text='Вы находитесь в меню, выберите нужную вам опцию',
        reply_markup=create_menu_keyboard()
    )

# --- Хендлеры для выбора типа работ ---
@dp.message(StateFilter(FSMForm.work_type))
async def work_type_handler(message: Message, state: FSMContext):
    await message.edit_text(text='Выбери вид работ или введи свой:', reply_markup=create_work_keyboard())

@dp.callback_query(StateFilter(FSMForm.work_type), F.data.in_(['Техплан жилой дом','Техплан гараж','Техплан постройка',]))
async def work_type_press_handler(callback: CallbackQuery, state: FSMContext):
    await state.update_data(WorkType=callback.data)
    await callback.message.edit_text(text='Выбери дату выезда или введи свою (дд.мм.гггг)',reply_markup=create_date_keyboard())
    await state.set_state(FSMForm.fill_VisitDate)

@dp.callback_query(StateFilter(FSMForm.work_type), F.data == 'GoBack')
async def go_back_handler(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await state.set_state(FSMForm.menu)
    await callback.message.edit_text(
        text='Вы находитесь в меню, выберите нужную вам опцию',
        reply_markup=create_menu_keyboard()
    )

# --- Хендлеры для ввода даты выезда ---
@dp.message(StateFilter(FSMForm.fill_VisitDate))
async def fill_visit_date_handler(message: Message, state: FSMContext):

    await message.answer(
        text='Выбери дату выезда или введи свою (дд.мм.гггг)',reply_markup=create_date_keyboard())

@dp.callback_query(StateFilter(FSMForm.fill_VisitDate), F.data.startswith('date:'))
async def visit_date_press_handler(callback: CallbackQuery, state: FSMContext):
    date_str = callback.data.split(':')[1]
    try:
        input_date = date.fromisoformat(date_str)
        if input_date >= date.today() and input_date < date.today() + timedelta(days=100):
            await state.update_data(VisitDate=input_date)
            await callback.message.edit_text(f'Вы выбрали дату: {input_date.strftime("%d.%m.%y")}')
            await state.set_state(FSMForm.fill_VisitTime)
            await callback.message.edit_text('Выбери время выезда или введи в формате чч:мм',reply_markup = create_time_keyboard())
        else:
            await callback.message.answer('Неверная дата. Пожалуйста, выберите дату в пределах ближайших 100 дней.')
    except ValueError:
        await callback.message.answer('Неверный формат даты.')

@dp.callback_query(StateFilter(FSMForm.fill_VisitDate), F.data == 'Без выезда')
async def without_time_handler(callback: CallbackQuery, state: FSMContext):
    await state.update_data(VisitDate='Без выезда')
    await state.set_state(FSMForm.fill_VisitTime)
    await callback.message.edit_text('Выбери время выезда или введи в формате чч:мм',reply_markup = create_time_keyboard())

@dp.callback_query(StateFilter(FSMForm.fill_VisitDate), F.data == 'menu')
async def return_to_menu_handler(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.edit_text(
        text='Вы находитесь в меню, выберите нужную вам опцию',
        reply_markup=create_menu_keyboard()
    )
    await state.set_state(FSMForm.menu)


# --- Хендлеры для ввода времени выезда ---
@dp.message(StateFilter(FSMForm.fill_VisitTime))
async def fill_visit_time_handler(message: Message, state: FSMContext):
    try:
        hour, minute = map(int, message.text.split(':'))
        if 0 <= hour <= 23 and 0 <= minute <= 59:
            await state.update_data(VisitTime=f'{hour:02}:{minute:02}')
            await message.answer(text='Введите кадастровый номер объекта работ (или ориентира, или земельного участка на котором находится объект работ, или кадастрового квартала, если ориентира нет)',reply_markup = create_ground_keyboard())
            await state.set_state(FSMForm.fill_GroundNum)
            await message.edit_text(
                text='Введи кадастровый номер объекта работ (или ориентира, или земельного участка на котором находится объект работ, или кадастрового квартала, если ориентира нет)',reply_markup = create_ground_keyboard())
        else:
            await message.answer('Неверный формат времени. Пожалуйста, введите время в формате чч:мм.')
    except ValueError:
        await message.answer('Неверный формат времени. Пожалуйста, введите время в формате чч:мм.')

@dp.callback_query(StateFilter(FSMForm.fill_VisitTime), F.data.in_(['Не важно', 'Первая половина дня', 'Вторая половина дня','Утро (первой заявкой)']))
async def visit_time_press_handler(callback: CallbackQuery, state: FSMContext):
    time_str = callback.data
    await state.update_data(VisitTime=time_str)
    await callback.message.edit_text(text='Введите кадастровый номер объекта недвижимости в отношении которого будут проводится работы (или участка на котором объект недвижимости расположен или ориентира)',reply_markup = create_ground_keyboard())
    await state.set_state(FSMForm.fill_GroundNum)

@dp.callback_query(StateFilter(FSMForm.fill_VisitTime), F.data == 'Отменить ввод')
async def return_to_menu_handler(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.edit_text(
        text='Вы находитесь в меню, выберите нужную вам опцию',
        reply_markup=create_menu_keyboard()
    )
    await state.set_state(FSMForm.menu)

@dp.callback_query(StateFilter(FSMForm.fill_VisitTime), F.data == 'Назад')
async def go_back_handler(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text('Выбери дату выезда или введи свою (дд.мм.гггг)',reply_markup = create_time_keyboard())
    await state.set_state(FSMForm.fill_VisitDate)


# --- Хендлеры для ввода кадастрового номера ---
@dp.message(FSMForm.fill_GroundNum)
async def fill_ground_num_handler(message: Message, state: FSMContext):
    await state.update_data(GroundNum=message.text)
    await message.answer(text='Введите кадастровый номер объекта работ (или ориентира, или земельного участка на котором находится объект работ, или кадастрового квартала, если ориентира нет)',reply_markup = create_ground_keyboard())

@dp.callback_query(StateFilter(FSMForm.fill_GroundNum), F.data == 'Later')
async def choise_later_handler(callback: CallbackQuery, state: FSMContext):
    await state.set_state(FSMForm.fill_PhoneNum)
    await callback.message.edit_text(text='Введи контактные данные (номера телефонов, имена контактов)',reply_markup = create_phon_keyboard())

@dp.callback_query(StateFilter(FSMForm.fill_GroundNum), F.data == 'Back')
async def back_to_prev_handler(callback: CallbackQuery, state: FSMContext):
    await state.set_state(FSMForm.fill_VisitTime)
    await callback.message.edit_text(text='Введите время или введите выезда в формате чч:мм',reply_markup = create_time_keyboard())

@dp.callback_query(StateFilter(FSMForm.fill_GroundNum), F.data == 'menu')
async def return_to_menu_handler(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.edit_text(text='Вы находитесь в меню, выберите нужную вам опцию', reply_markup=create_menu_keyboard())
    await state.set_state(FSMForm.menu)


@dp.message(FSMForm.fill_GroundNum, F.text)
async def fill_ground_num_text_handler(message: Message, state: FSMContext):
    await state.update_data(GroundNum=message.text)
    await message.edit_text(text='Введи контактные данные (номера телефонов, имена контактов)',reply_markup = create_phon_keyboard())
    await state.set_state(FSMForm.fill_PhoneNum)


# --- Хендлеры для ввода телефона ---
@dp.message(FSMForm.fill_PhoneNum)
async def fill_phone_num_handler(message: Message, state: FSMContext):
    await state.update_data(PhoneNum=message.text)
    await message.edit_text(text='Введи контактные данные (номера телефонов, имена контактов)',reply_markup = create_phon_keyboard())

@dp.callback_query(StateFilter(FSMForm.fill_PhoneNum), F.data == 'Later')
async def choise_later_handler(callback: CallbackQuery, state: FSMContext):
    await state.set_state(FSMForm.fill_Task)
    await callback.message.edit_text(text='Введи стоимость работ и порядок оплаты',  reply_markup= create_price_keyboard())

@dp.callback_query(StateFilter(FSMForm.fill_PhoneNum), F.data == 'Back')
async def back_to_prev_handler(callback: CallbackQuery, state: FSMContext):
    await state.set_state(FSMForm.fill_VisitTime)
    await callback.message.edit_text(text='Введите кадастровый номер объекта работ (или ориентира, или земельного участка на котором находится объект работ, или кадастрового квартала, если ориентира нет)',reply_markup = create_ground_keyboard())

@dp.callback_query(StateFilter(FSMForm.fill_PhoneNum), F.data == 'menu')
async def return_to_menu_handler(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.edit_text('Вы вернулись в главное меню.')
    await state.set_state(FSMForm.menu)
    await callback.message.edit_text(
        text='Вы находитесь в меню, выберите нужную вам опцию', reply_markup=create_menu_keyboard())

    # --- Хендлеры для ввода цены ---
@dp.message(FSMForm.fill_Price)
async def fill_price_handler(message: Message, state: FSMContext):
    await state.update_data(Price=message.text)
    await message.edit_text(text='Введи стоимость работ и порядок оплаты',  reply_markup= create_price_keyboard())

@dp.callback_query(StateFilter(FSMForm.fill_Price), F.data == 'Back')
async def back_to_prev_handler(callback: CallbackQuery, state: FSMContext):
    await state.set_state(FSMForm.fill_Task)
    await callback.message.edit_text(text='Введи контактные данные (номера телефонов, имена контактов)',reply_markup = create_phon_keyboard())


@dp.callback_query(StateFilter(FSMForm.fill_Price), F.data == 'Later')
async def choise_later_handler(callback: CallbackQuery, state: FSMContext):
    await state.set_state(FSMForm.fill_Source)
    await callback.message.edit_text(text='Введите источник заявки',reply_markup = create_source_keyboard())

@dp.callback_query(StateFilter(FSMForm.fill_Price), F.data == 'menu')
async def return_to_menu_handler(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.edit_text(text='Вы находитесь в меню, выберите нужную вам опцию', reply_markup=create_menu_keyboard())
    await state.set_state(FSMForm.menu)



# --- Хендлеры для ввода описания заявки ---
@dp.message(FSMForm.fill_Task)
async def fill_task_handler(message: Message, state: FSMContext):
    await state.update_data(Task=message.text)
    if message.photo:
        media_type = 'photo'
        file_id = message.photo[-1].file_id
    elif message.document:
        media_type = 'document'
        file_id = message.document.file_id
    else:
        await message.answer("Пожалуйста, прикрепите фото или файл.")
        return
    await state.update_data(Media= {'type': media_type, 'id': file_id})
    await message.answer(
        text='Введите описание заявки (суть работ) - всё что ты хочешь сказать относительно заявки, не вошедшее в предыдущие поля. Если надо прикрепить изображения или файлы - можешь это сделать здесь же.',reply_markup = create_task_keyboard())


@dp.callback_query(StateFilter(FSMForm.fill_Task), F.data == 'Back')
async def back_to_prev_handler(callback: CallbackQuery, state: FSMContext):
    await state.set_state(FSMForm.fill_GroundNum)
    await callback.message.edit_text (text='Введи стоимость работ и порядок оплаты',  reply_markup= create_price_keyboard())

@dp.callback_query(StateFilter(FSMForm.fill_Task), F.data == 'Later')
async def choise_later_handler(callback: CallbackQuery, state: FSMContext):
    await state.set_state(FSMForm.fill_Source)
    await callback.message.edit_text(text='Введите источник заявки',reply_markup= create_source_keyboard())

@dp.callback_query(StateFilter(FSMForm.fill_Task), F.data == 'menu')
async def return_to_menu_handler(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.edit_text(text='Вы находитесь в меню, выберите нужную вам опцию', reply_markup=create_menu_keyboard())
    await state.set_state(FSMForm.menu)


# --- Хендлеры для ввода источника заявки ---
@dp.message(FSMForm.fill_Source)
async def fill_source_handler(message: Message, state: FSMContext):
    await state.update_data(Source=message.text)
    await message.answer(text='Выберите источник заявки или введите вручную',reply_markup= create_source_keyboard())

@dp.callback_query(lambda c: c.data in ['Я Авито', 'Я Сарафан', 'Я Ркк', 'Другой пользователь'])
async def source_press_handler(callback: CallbackQuery, state: FSMContext):
    await state.update_data(Source=callback.data)
    what = callback.data
    await callback.message.edit_text(f'Вы указали: {what}')
    await callback.message.edit_text(
        text='Заявка создана, публикуем?',reply_markup = create_publish_keyboard())
    await state.set_state(FSMForm.upload)


@dp.callback_query(StateFilter(FSMForm.fill_Source), F.data == 'Back')
async def back_to_prev_handler(callback: CallbackQuery, state: FSMContext):
    await state.set_state(FSMForm.fill_Price)
    await callback.message.edit_text(
        text='Введите описание заявки (суть работ) - всё что ты хочешь сказать относительно заявки, не вошедшее в предыдущие поля. Если надо прикрепить изображения или файлы - можешь это сделать здесь же.',reply_markup = create_task_keyboard())

@dp.callback_query(StateFilter(FSMForm.fill_Source), F.data == 'Later')
async def choise_later_handler(callback: CallbackQuery, state: FSMContext):
    await state.set_state(FSMForm.upload)
    await callback.message.edit_text(
        text='Заявка создана, публикуем?', reply_markup = create_publish_keyboard())

@dp.callback_query(StateFilter(FSMForm.fill_Source), F.data == 'menu')
async def return_to_menu_handler(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.edit_text(text='Вы находитесь в меню, выберите нужную вам опцию', reply_markup=create_menu_keyboard())
    await state.set_state(FSMForm.menu)

# --- Хендлеры для отправки заявки ---
@dp.message(FSMForm.upload)
async def fill_link_handler(message: Message, state: FSMContext):
    await state.update_data(Link=message.text)
    await state.set_state(FSMForm.upload)
    await message.edit_text(
        text='Заявка создана, публикуем?',reply_markup = create_publish_keyboard())

@dp.callback_query(StateFilter(FSMForm.upload), F.data == 'publish')
async def publish_handler(call: CallbackQuery, state: FSMContext):
    user_data = await state.get_data()
    if user_data:
        caption = (
            f'Номер заявки: {uuid.uuid4()}\n'
            f'Дата создания заявки: {datetime.now()}\n'
            f'Вид работ: {user_data["WorkType"]}\n'
            f'День визита: {user_data["VisitDate"]}\n'
            f'Время визита: {user_data["VisitTime"]}\n'
            f'Кадастровый номер: {user_data["GroundNum"]}\n'
            f'Контактные данные: {user_data["PhoneNum"]}\n'
            f'Стоимость: {user_data["Price"]}\n'
            f'Суть заявки: {user_data["Task"]}\n'
            f'Источник заявки: {user_data["Source"]}\n'
        )
        await call.answer("Заявка опубликована!")
        try:
            await call.message.delete()
        except MessageToDeleteNotFound:
            pass
        await state.clear()
        if 'Media' in user_data:
            await bot.send_photo(chat_id=call.message.chat.id, photo=user_data['Media'], caption=caption)
        else:
            await bot.send_message(chat_id=call.message.chat.id, text=caption)

@dp.callback_query(StateFilter(FSMForm.upload), F.data == 'publish_and_create')
async def publish_and_create_handler(call: CallbackQuery, state: FSMContext):
    user_data = await state.get_data()
    if user_data:
        caption = (
            f'Номер заявки: {uuid.uuid4()}\n'
            f'Дата создания заявки: {datetime.now()}\n'
            f'Вид работ: {user_data["WorkType"]}\n'
            f'День визита: {user_data["VisitDate"]}\n'
            f'Время визита: {user_data["VisitTime"]}\n'
            f'Кадастровый номер: {user_data["GroundNum"]}\n'
            f'Суть заявки: {user_data["Task"]}\n'
            f'Стоимость: {user_data["Price"]}\n'
            f'Источник заявки: {user_data["Source"]}\n'
            f'Ссылка: {user_data["Link"]}\n'
        )
        await call.answer("Заявка опубликована!")
        try:
            await call.message.delete()
        except MessageToDeleteNotFound:
            pass
        await state.set_state(FSMForm.menu)
        await call.message.answer(text='Вы находитесь в меню, выберите нужную вам опцию', reply_markup=create_menu_keyboard())
        if 'Media' in user_data:
            await bot.send_photo(chat_id=call.message.chat.id, photo=user_data['Media'], caption=caption)
        else:
            await bot.send_message(chat_id=call.message.chat.id, text=caption)


if __name__ == '__main__':
    dp.run_polling(bot)