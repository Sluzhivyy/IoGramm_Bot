import uuid
from datetime import datetime, date, timedelta
from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command, CommandStart, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import default_state, State, StatesGroup
from aiogram.types import (CallbackQuery, InlineKeyboardButton,InlineKeyboardMarkup, Message, PhotoSize)
from aiogram.fsm.storage.memory import MemoryStorage
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
    fill_Task = State()
    fill_Task_Media = State()
    fill_Price = State()
    fill_Source = State()
    fill_Link = State()
    upload = State()

# Обработчик команды /start
@dp.message(CommandStart())
async def process_start_command(message: Message):
    await message.answer(
        text='Для получения информации - '
            'отправьте команду /info n'
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

# Функция для создания клавиатуры меню
def create_menu_keyboard():
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text='Заполнить форму', callback_data='form')],
            [InlineKeyboardButton(text='Информация о функционале', callback_data='info')]
        ]
    )
    return keyboard

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
    await callback.message.edit_text("Вы выбрали заполнение анкеты")
    await state.set_state(FSMForm.work_type)

@dp.callback_query(lambda c: c.data == 'info')
async def info_handler(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text("Вы выбрали информацию о функционале")
    await callback.message.answer(
        text='Это бот, который позволяет быстро и удобно заполнять формы'
    )
    await state.set_state(FSMForm.menu)
    await callback.message.answer(
        text='Вы находитесь в меню, выберите нужную вам опцию',
        reply_markup=create_menu_keyboard()
    )

# --- Хендлеры для выбора типа работ ---
@dp.message(StateFilter(FSMForm.work_type))
async def work_type_handler(message: Message, state: FSMContext):
    PlanHouse = InlineKeyboardButton(text='Техплан жилой дом', callback_data='Техплан жилой дом')
    PlanGarage = InlineKeyboardButton(text='Техплан гараж', callback_data='Техплан гараж')
    PlanBuilding = InlineKeyboardButton(text='Техплан постройка ', callback_data='Техплан постройка ')

    GoBack = InlineKeyboardButton(text='Вернуться в главное меню', callback_data='GoBack')
    keyboard: list[list[InlineKeyboardButton]] = [
        [PlanHouse, PlanGarage],
        [PlanBuilding, GoBack]
    ]
    markup = InlineKeyboardMarkup(inline_keyboard=keyboard)
    await message.edit_text(text='Выбери вид работ или введи свой:', reply_markup=markup)

@dp.callback_query(StateFilter(FSMForm.work_type), F.data.in_(['Техплан жилой дом', 'Техплан гараж', 'Техплан постройка']))
async def work_type_press_handler(callback: CallbackQuery, state: FSMContext):
    await state.update_data(WorkType=callback.data)
    work_choise = callback.data
    await callback.message.edit_text(f"Вы выбрали: {work_choise}")
    await state.set_state(FSMForm.fill_VisitDate)

@dp.callback_query(StateFilter(FSMForm.work_type), F.data == 'GoBack')
async def go_back_handler(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.edit_text("Вы вернулись в главное меню.")
    await state.set_state(FSMForm.menu)

# --- Хендлеры для ввода даты выезда ---
@dp.message(StateFilter(FSMForm.fill_VisitDate))
async def fill_visit_date_handler(message: Message, state: FSMContext):
    today = date.today()
    tomorrow = today + timedelta(days=1)
    dates = [today + timedelta(days=i) for i in range(2, 6)]
    keyboard = [
        [InlineKeyboardButton(text='Без выезда', callback_data='Без выезда')],
        [InlineKeyboardButton(text='Сегодня', callback_data=f'date:{today.isoformat()}')],
        [InlineKeyboardButton(text='Завтра', callback_data=f'date:{tomorrow.isoformat()}')],
    ] + [
        [InlineKeyboardButton(text=f'{d.strftime("%d.%m.%y")} ({d.strftime("%a")[:2].capitalize()})',
                            callback_data=f'date:{d.isoformat()}') for d in dates]
    ]
    keyboard.append([InlineKeyboardButton(text='В главное меню', callback_data='menu')])
    markup = InlineKeyboardMarkup(inline_keyboard=keyboard)
    await message.answer(
        text='Выбери дату выезда или введи свою (дд.мм.гггг)',
        reply_markup=markup
    )

@dp.callback_query(StateFilter(FSMForm.fill_VisitDate), F.data.startswith('date:'))
async def visit_date_press_handler(callback: CallbackQuery, state: FSMContext):
    date_str = callback.data.split(':')[1]
    try:
        input_date = date.fromisoformat(date_str)
        if input_date >= date.today() and input_date < date.today() + timedelta(days=100):
            await state.update_data(VisitDate=input_date)
            await callback.message.edit_text(f'Вы выбрали дату: {input_date.strftime("%d.%m.%y")}')
            await state.set_state(FSMForm.fill_VisitTime)
        else:
            await callback.message.answer('Неверная дата. Пожалуйста, выберите дату в пределах ближайших 100 дней.')
    except ValueError:
        await callback.message.answer('Неверный формат даты.')

@dp.callback_query(StateFilter(FSMForm.fill_VisitDate), F.data == 'Без выезда')
async def without_time_handler(callback: CallbackQuery, state: FSMContext):
    await state.update_data(VisitDate='Без выезда')
    await state.set_state(FSMForm.fill_VisitTime)
    await callback.message.edit_text('Вы выбрали дату: Без выезда')

@dp.callback_query(StateFilter(FSMForm.fill_VisitDate), F.data == 'menu')
async def return_to_menu_handler(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.edit_text('Вы вернулись в главное меню.')
    await state.set_state(FSMForm.menu)

# --- Хендлеры для ввода времени выезда ---
@dp.message(StateFilter(FSMForm.fill_VisitTime))
async def fill_visit_time_handler(message: Message, state: FSMContext):
    try:
        hour, minute = map(int, message.text.split(':'))
        if 0 <= hour <= 23 and 0 <= minute <= 59:
            await state.update_data(VisitTime=f'{hour:02}:{minute:02}')
            await message.answer(f'Вы выбрали время: {hour:02}:{minute:02}')
            await state.set_state(FSMForm.fill_GroundNum)
            await message.answer(
                text='Введи кадастровый номер объекта работ (или ориентира, или земельного участка на котором находится объект работ, или кадастрового квартала, если ориентира нет)'
            )
        else:
            await message.answer('Неверный формат времени. Пожалуйста, введите время в формате чч:мм.')
    except ValueError:
        await message.answer('Неверный формат времени. Пожалуйста, введите время в формате чч:мм.')

@dp.callback_query(StateFilter(FSMForm.fill_VisitTime), F.data.startswith('time:'))
async def visit_time_press_handler(callback: CallbackQuery, state: FSMContext):
    time_str = callback.data.split(':')[1]
    if time_str == 'Первая половина':
        await state.update_data(VisitTime='Первая половина')
        await callback.message.edit_text('Вы выбрали первую половину дня.')
    elif time_str == 'Вторая половина':
        await state.update_data(VisitTime='Вторая половина')
        await callback.message.edit_text('Вы выбрали вторую половину дня.')
    else:
        await state.update_data(VisitTime=time_str)
        await callback.message.edit_text(f'Вы выбрали время: {time_str}')
        await callback.message.answer(
            text='Введите кадастровый номер объекта недвижимости в отношении которого будут проводится работы (или участка на котором объект недвижимости расположен или ориентира)',
        )
    await state.set_state(FSMForm.fill_GroundNum)

# --- Хендлеры для ввода кадастрового номера ---
@dp.message(FSMForm.fill_GroundNum)
async def fill_ground_num_handler(message: Message, state: FSMContext):
    await state.update_data(GroundNum=message.text)
    await message.answer(
        text='Введите кадастровый номер объекта работ (или ориентира, или земельного участка на котором находится объект работ, или кадастрового квартала, если ориентира нет)',
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text='Ввести кадастровый позже', callback_data='Later')],[InlineKeyboardButton(text='Назад', callback_data='Back')],
                [InlineKeyboardButton(text='Отменить ввод', callback_data='menu')]
            ]
        )
    )

@dp.callback_query(StateFilter(FSMForm.fill_GroundNum), F.data == 'Later')
async def choise_later_handler(callback: CallbackQuery, state: FSMContext):
    await state.set_state(FSMForm.fill_Task)
    await callback.message.edit_text(
        text='Введите описание заявки (суть работ) - всё что ты хочешь сказать относительно заявки, не вошедшее в предыдущие поля. Если надо прикрепить изображения или файлы - можешь это сделать здесь же.',
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text='Назад', callback_data='Back')],
                [InlineKeyboardButton(text='Ввести позже', callback_data='Later')],
                [InlineKeyboardButton(text='Отменить ввод', callback_data='menu')]
            ]
        )
    )

@dp.callback_query(StateFilter(FSMForm.fill_GroundNum), F.data == 'Back')
async def back_to_prev_handler(callback: CallbackQuery, state: FSMContext):
    await state.set_state(FSMForm.fill_VisitTime)
    await callback.message.edit_text(
        text='Введите время выезда в формате чч:мм'
    )

@dp.callback_query(StateFilter(FSMForm.fill_GroundNum), F.data == 'menu')
async def return_to_menu_handler(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.edit_text('Вы вернулись в главное меню.')
    await state.set_state(FSMForm.menu)
    await callback.message.answer(text='Вы находитесь в меню, выберите нужную вам опцию', reply_markup=create_menu_keyboard())

# --- Хендлеры для ввода описания заявки ---
@dp.message(FSMForm.fill_Task)
async def fill_task_handler(message: Message, state: FSMContext):
    await state.update_data(Task=message.text)
    await message.answer(
        text='Введите описание заявки (суть работ) - всё что ты хочешь сказать относительно заявки, не вошедшее в предыдущие поля. Если надо прикрепить изображения или файлы - можешь это сделать здесь же.',
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text='Назад', callback_data='Back')],
                [InlineKeyboardButton(text='Ввести позже', callback_data='Later')],
                [InlineKeyboardButton(text='Отменить ввод', callback_data='menu')]
            ]
        )
    )

@dp.message(FSMForm.fill_Task_Media)
async def fill_task_media_handler(message: Message, state: FSMContext):
    if message.photo or message.document:
        await state.update_data(Media=message)
        await state.set_state(FSMForm.fill_Price)
        await message.answer(
            text='Введите желаемую цену работ'
        )
    else:
        await message.answer("Пожалуйста, прикрепите фото или файл.")

@dp.callback_query(StateFilter(FSMForm.fill_Task), F.data == 'Back')
async def back_to_prev_handler(callback: CallbackQuery, state: FSMContext):
    await state.set_state(FSMForm.fill_GroundNum)
    await callback.message.edit_text(
        text='Введите кадастровый номер объекта работ (или ориентира, или земельного участка на котором находится объект работ, или кадастрового квартала, если ориентира нет)',
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text='Ввести кадастровый позже', callback_data='Later')],
                [InlineKeyboardButton(text='Назад', callback_data='Back')],
                [InlineKeyboardButton(text='Отменить ввод', callback_data='menu')]
            ]
        )
    )

@dp.callback_query(StateFilter(FSMForm.fill_Task), F.data == 'Later')
async def choise_later_handler(callback: CallbackQuery, state: FSMContext):
    await state.set_state(FSMForm.fill_Source)
    await callback.message.edit_text(
        text='Введите источник заявки',
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text='Назад', callback_data='Back')],
                [InlineKeyboardButton(text='Ввести позже', callback_data='Later')],
                [InlineKeyboardButton(text='Отменить ввод', callback_data='menu')],
                [InlineKeyboardButton(text='Я Авито', callback_data='Я Авито')],
                [InlineKeyboardButton(text='Я Сарафан', callback_data='Я Сарафан')],
                [InlineKeyboardButton(text='Я Ркк', callback_data='Я Ркк')],
                [InlineKeyboardButton(text='Другой пользователь', callback_data='Другой пользователь')]
            ]
        )
    )

@dp.callback_query(StateFilter(FSMForm.fill_Task), F.data == 'menu')
async def return_to_menu_handler(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.edit_text('Вы вернулись в главное меню.')
    await state.set_state(FSMForm.menu)
    await callback.message.answer(text='Вы находитесь в меню, выберите нужную вам опцию', reply_markup=create_menu_keyboard())

# --- Хендлеры для ввода цены ---
@dp.message(FSMForm.fill_Price)
async def fill_price_handler(message: Message, state: FSMContext):
    await state.update_data(Price=message.text)
    keyboard: list[list[InlineKeyboardButton]] = [
        [InlineKeyboardButton(text='Назад', callback_data='Back')],
        [InlineKeyboardButton(text='Ввести позже', callback_data='Later')],[InlineKeyboardButton(text='Отменить ввод', callback_data='menu')]
    ]
    markup = InlineKeyboardMarkup(inline_keyboard=keyboard)
    await message.edit_text(text='Восхитительно, а теперь выберите вариант предоплаты:', reply_markup=markup)

@dp.callback_query(StateFilter(FSMForm.fill_Price), F.data == 'Back')
async def back_to_prev_handler(callback: CallbackQuery, state: FSMContext):
    await state.set_state(FSMForm.fill_Task)
    await callback.message.edit_text(
        text='Введите описание заявки (суть работ) - всё что ты хочешь сказать относительно заявки, не вошедшее в предыдущие поля. Если надо прикрепить изображения или файлы - можешь это сделать здесь же.',
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text='Назад', callback_data='Back')],
                [InlineKeyboardButton(text='Ввести позже', callback_data='Later')],
                [InlineKeyboardButton(text='Отменить ввод', callback_data='menu')]
            ]
        )
    )

@dp.callback_query(StateFilter(FSMForm.fill_Price), F.data == 'Later')
async def choise_later_handler(callback: CallbackQuery, state: FSMContext):
    await state.set_state(FSMForm.fill_Source)
    await callback.message.edit_text(
        text='Введите источник заявки',
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text='Назад', callback_data='Back')],
                [InlineKeyboardButton(text='Ввести позже', callback_data='Later')],
                [InlineKeyboardButton(text='Отменить ввод', callback_data='menu')],
                [InlineKeyboardButton(text='Я Авито', callback_data='Я Авито')],
                [InlineKeyboardButton(text='Я Сарафан', callback_data='Я Сарафан')],
                [InlineKeyboardButton(text='Я Ркк', callback_data='Я Ркк')],
                [InlineKeyboardButton(text='Другой пользователь', callback_data='Другой пользователь')]
            ]
        )
    )

@dp.callback_query(StateFilter(FSMForm.fill_Price), F.data == 'menu')
async def return_to_menu_handler(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.edit_text('Вы вернулись в главное меню.')
    await state.set_state(FSMForm.menu)
    await callback.message.answer(text='Вы находитесь в меню, выберите нужную вам опцию', reply_markup=create_menu_keyboard())

# --- Хендлеры для ввода источника заявки ---
@dp.message(FSMForm.fill_Source)
async def fill_source_handler(message: Message, state: FSMContext):
    await state.update_data(Source=message.text)
    keyboard: list[list[InlineKeyboardButton]] = [
        [InlineKeyboardButton(text='Назад', callback_data='Back')],
        [InlineKeyboardButton(text='Ввести позже', callback_data='Later')],[InlineKeyboardButton(text='Отменить ввод', callback_data='menu')],
        [InlineKeyboardButton(text='Я Авито', callback_data='Я Авито')],
        [InlineKeyboardButton(text='Я Сарафан', callback_data='Я Сарафан')],
        [InlineKeyboardButton(text='Я Ркк', callback_data='Я Ркк')],
        [InlineKeyboardButton(text='Другой пользователь', callback_data='Другой пользователь')]

    ]
    markup = InlineKeyboardMarkup(inline_keyboard=keyboard)
    await message.answer(text='Выберите источник заявки или введите вручную', reply_markup=markup)

@dp.callback_query(lambda c: c.data in ['Я Авито', 'Я Сарафан', 'Я Ркк', 'Другой пользователь'])
async def source_press_handler(callback: CallbackQuery, state: FSMContext):
    await state.update_data(Source=callback.data)
    what = callback.data
    await callback.message.edit_text(f'Вы указали: {what}')
    await state.set_state(FSMForm.fill_Link)
    await callback.message.answer(text='Лучше не бывает, а теперь введите ссылку')

@dp.callback_query(StateFilter(FSMForm.fill_Source), F.data == 'Back')
async def back_to_prev_handler(callback: CallbackQuery, state: FSMContext):
    await state.set_state(FSMForm.fill_Price)
    await callback.message.edit_text(
        text='Введите желаемую цену работ'
    )

@dp.callback_query(StateFilter(FSMForm.fill_Source), F.data == 'Later')
async def choise_later_handler(callback: CallbackQuery, state: FSMContext):
    await state.set_state(FSMForm.upload)
    await callback.message.edit_text(
        text='Отлично, теперь вы можете просмотреть и отправить заявку',
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(text="Опубликовать", callback_data="publish"),

                ],
                [
                    InlineKeyboardButton(text="Опубликовать и создать новую", callback_data="publish_and_create"),

                ],
                [
                    InlineKeyboardButton(text="Назад", callback_data="Back"),InlineKeyboardButton(text="Отменить ввод", callback_data="cancel"),
                ]
            ]
        )
    )

@dp.callback_query(StateFilter(FSMForm.fill_Source), F.data == 'menu')
async def return_to_menu_handler(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.edit_text('Вы вернулись в главное меню.')
    await state.set_state(FSMForm.menu)
    await callback.message.answer(text='Вы находитесь в меню, выберите нужную вам опцию', reply_markup=create_menu_keyboard())

# --- Хендлеры для ввода ссылки ---
@dp.message(FSMForm.fill_Link)
async def fill_link_handler(message: Message, state: FSMContext):
    await state.update_data(Link=message.text)
    await state.set_state(FSMForm.upload)
    await message.edit_text(
        text='Отлично, теперь вы можете просмотреть и отправить заявку',
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(text="Опубликовать", callback_data="publish"),

                ],
                [
                    InlineKeyboardButton(text="Опубликовать и создать новую", callback_data="publish_and_create"),

                ],
                [
                    InlineKeyboardButton(text="Назад", callback_data="Back"),
                    InlineKeyboardButton(text="Отменить ввод", callback_data="cancel"),
                ]
            ]
        )
    )

# --- Хендлеры для отправки заявки ---
@dp.callback_query(StateFilter(FSMForm.fill_Link), F.data == 'publish')
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
        await state.clear()
        if 'Media' in user_data:
            await bot.send_photo(chat_id=call.message.chat.id, photo=user_data['Media'], caption=caption)
        else:
            await bot.send_message(chat_id=call.message.chat.id, text=caption)

@dp.callback_query(StateFilter(FSMForm.fill_Link), F.data == 'publish_and_create')
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

@dp.callback_query(StateFilter(FSMForm.fill_Link), F.data == 'Back')
async def back_handler(call: CallbackQuery, state: FSMContext):
    await call.answer("Вернулись к предыдущему шагу")
    await call.message.delete()
    await state.set_state(FSMForm.fill_Link)
    await call.message.answer(text='Лучше не бывает, а теперь введите ссылку')

@dp.callback_query(StateFilter(FSMForm.fill_Link), F.data == 'cancel')
async def cancel_handler(call: CallbackQuery, state: FSMContext):
    await call.answer("Ввод отменен")
    await call.message.delete()
    await state.clear()
    await state.set_state(FSMForm.menu)
    await call.message.answer(text='Вы находитесь в меню, выберите нужную вам опцию', reply_markup=create_menu_keyboard())

if __name__ == '__main__':
    dp.run_polling(bot)