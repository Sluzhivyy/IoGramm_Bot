import uuid
from datetime import datetime, date, timedelta
from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command, CommandStart, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import default_state, State, StatesGroup
from aiogram.types import (CallbackQuery, InlineKeyboardButton,InlineKeyboardMarkup, Message, PhotoSize, ReplyKeyboardRemove)
from aiogram.fsm.storage.memory import MemoryStorage
from keyboards import *
from env import BOT_TOKEN
import locale
import re

storage = MemoryStorage()
bot = Bot(BOT_TOKEN)
dp = Dispatcher(storage=storage)
locale.setlocale(locale.LC_ALL, 'ru_RU')
user_dict: dict[int, dict[str, str | int]] = {}

class FSMForm(StatesGroup):
    menu = State()
    work_type = State()
    fill_VisitDate = State()
    fill_VisitTime = State()
    fill_GroundNum = State()
    fill_PhoneNum = State()
    fill_Task = State()
    upload = State()


@dp.message(CommandStart())
async def process_start_command(message: Message):
    await message.answer(
        text= 'Для перехода в меню, отправьте команду /menu'
    )


@dp.message(Command(commands='cancel'))
async def process_cancel_command(message: Message, state: FSMContext):
    await message.answer(
        text='Отмена ввода. Вы можете вернуться в главное меню введя команду /menu или нажав на нее в этом сообщении.'
    )
    await state.clear()


@dp.message(Command(commands='info'))
async def process_info_command(message: Message):
    await message.answer(
        text='👋 Привет!\n'
            'Я создан для того, чтобы сделать процесс заполнения форм максимально простым и удобным. '

    )

@dp.message(Command(commands='menu'))
async def process_menu(message: Message, state: FSMContext):
    await state.set_state(FSMForm.menu)
    await message.answer(
        text='Вы находитесь в меню, выберите нужную вам опцию',
        reply_markup=create_menu_keyboard()
    )

# Обработка команды /menu
@dp.message(Command(commands='menu'))
async def process_menu(message: Message, state: FSMContext):
    await state.set_state(FSMForm.menu)
    await message.answer(
        text='Вы находитесь в меню, выберите нужную вам опцию',
        reply_markup=create_menu_keyboard()
    )

# Обработка любых текстовых сообщений в состоянии menu
@dp.message(StateFilter(FSMForm.menu))
async def p_menu(message: Message, state: FSMContext):
    await message.answer(
        'Зачем? Выберите действие из "Заполнить форму" и "Информация о функционале".'
    )

# Хендлеры для выбора опций в меню
@dp.callback_query(lambda c: c.data == 'form')
async def form_handler(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text(
        text='Выберите вид работ или введите свой:',
        reply_markup=None
    )
    await state.set_state(FSMForm.work_type)

@dp.callback_query(lambda c: c.data == 'info')
async def info_handler(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text(
        text='👋 Привет!\n'
             'Я создан для того, чтобы сделать процесс заполнения форм максимально простым и удобным.\n'
             'Для того чтобы начать заполнение, нажми на кнопку "Заполнить форму"'
    )
    await state.set_state(FSMForm.menu)
    await callback.message.answer(
        text='Вы находитесь в меню, выберите нужную вам опцию',
        reply_markup=create_menu_keyboard()
    )

# Хендлеры для выбора типа работ
@dp.message(StateFilter(FSMForm.work_type))
async def work_type_handler(message: Message, state: FSMContext):
    await message.edit_text(
        text='Выберите вид работ или введите свой:',
        reply_markup=None
    )
    await state.update_data(WorkType=message.text)
    print(await state.get_data())
    await state.set_state(FSMForm.fill_VisitDate)
    await message.answer(text='Выберите дату выезда или введите свою (дд.мм.гггг)')

@dp.callback_query(StateFilter(FSMForm.work_type), F.data.in_(['Техплан жилой дом', 'Техплан гараж', 'Техплан постройка']))
async def work_type_press_handler(callback: CallbackQuery, state: FSMContext):
    await state.update_data(WorkType=callback.data)
    print(await state.get_data())
    await callback.message.edit_text(
        text='Выберите дату выезда или введите свою (дд.мм.гггг)',
        reply_markup=create_date_keyboard()
    )
    await state.set_state(FSMForm.fill_VisitDate)

@dp.callback_query(StateFilter(FSMForm.work_type), F.data == 'GoBack')
async def go_back_handler(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await state.set_state(FSMForm.menu)
    await callback.message.edit_text(
        text='Вы находитесь в меню, выберите нужную вам опцию',
        reply_markup=create_menu_keyboard()
    )

# Хендлеры для ввода даты выезда
@dp.message(StateFilter(FSMForm.fill_VisitDate))
async def fill_visit_date_handler(message: Message, state: FSMContext):
    try:
        input_date = datetime.strptime(message.text, '%d.%m.%Y').date()
        if input_date >= date.today() and input_date < date.today() + timedelta(days=100):
            await state.update_data(VisitDate=input_date)
            print(await state.get_data())
            await message.answer('Выберите время выезда или введите в формате чч:мм', reply_markup=None)
            await state.set_state(FSMForm.fill_VisitTime)
            await message.edit_text('Выберите время выезда или введите в формате чч:мм', reply_markup=create_time_keyboard())
        else:
            await message.answer('Неверная дата. Пожалуйста, выберите дату в пределах ближайших 100 дней.', reply_markup=None)
    except ValueError:
        await message.answer(text='Неверный формат даты. Пожалуйста, введите дату в формате дд.мм.гггг.', reply_markup=None)

@dp.callback_query(StateFilter(FSMForm.fill_VisitDate), lambda c: c.data.startswith('date:'))
async def visit_date_press_handler(callback: CallbackQuery, state: FSMContext):
    date_str = callback.data.split(':')[1]
    try:
        input_date = date.fromisoformat(date_str)
        if input_date >= date.today() and input_date < date.today() + timedelta(days=100):
            await state.update_data(VisitDate=input_date)
            print(await state.get_data())
            await state.set_state(FSMForm.fill_VisitTime)
            await callback.message.edit_text('Выберите время выезда или введите в формате чч:мм', reply_markup=create_time_keyboard())
        else:
            await callback.message.answer('Неверная дата. Пожалуйста, выберите дату в пределах ближайших 100 дней.')
    except ValueError:
        await callback.message.answer('Неверный формат даты.')

@dp.callback_query(StateFilter(FSMForm.fill_VisitDate), lambda c: c.data == 'Без выезда')
async def without_time_handler(callback: CallbackQuery, state: FSMContext):
    await state.update_data(VisitDate='Без выезда')
    await state.set_state(FSMForm.fill_VisitTime)
    await callback.message.edit_text('Выберите время выезда или введите в формате чч:мм', reply_markup=create_time_keyboard())

@dp.callback_query(StateFilter(FSMForm.fill_VisitDate), lambda c: c.data == 'menu')
async def return_to_menu_handler(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.edit_text(
        text='Вы находитесь в меню, выберите нужную вам опцию',
        reply_markup=create_menu_keyboard()
    )
    await state.set_state(FSMForm.menu)

# Хендлеры для ввода времени выезда
@dp.message(StateFilter(FSMForm.fill_VisitTime))
async def fill_visit_time_handler(message: Message, state: FSMContext):
    try:
        hour, minute = map(int, message.text.split(':'))
        if 0 <= hour <= 23 and 0 <= minute <= 59:
            await state.update_data(VisitTime=f'{hour:02}:{minute:02}')
            await message.edit_text(text='Введите кадастровый номер объекта работ (или ориентира, или земельного участка на котором находится объект работ, или кадастрового квартала, если ориентира нет)', reply_markup=None)
            await state.set_state(FSMForm.fill_GroundNum)
            print(await state.get_data())
        else:
            await message.answer('Неверный формат времени. Пожалуйста, введите время в формате чч:мм.')
    except ValueError:
        await message.answer('Неверный формат времени. Пожалуйста, введите время в формате чч:мм.')

@dp.callback_query(StateFilter(FSMForm.fill_VisitTime), lambda c: c.data in ['Не важно', 'Первая половина дня', 'Вторая половина дня', 'Утро (первой заявкой)'])
async def visit_time_press_handler(callback: CallbackQuery, state: FSMContext):
    time_str = callback.data
    await state.update_data(VisitTime=time_str)
    print(await state.get_data())
    await callback.message.edit_text(text='Введите кадастровый номер объекта недвижимости в отношении которого будут проводиться работы (или участка на котором объект недвижимости расположен или ориентира)', reply_markup=create_ground_keyboard())
    await state.set_state(FSMForm.fill_GroundNum)

# Хендлеры для ввода кадастрового номера
@dp.message(FSMForm.fill_GroundNum, F.text)
async def fill_ground_num_handler(message: Message, state: FSMContext):
    await state.update_data(GroundNum=message.text)
    print(await state.get_data())
    await message.answer(text='Введите контактные данные', reply_markup=create_phon_keyboard())
    await state.set_state(FSMForm.fill_PhoneNum)

@dp.callback_query(StateFilter(FSMForm.fill_GroundNum), F.data == 'menu')
async def return_to_menu_handler(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.edit_text(text='Вы находитесь в меню, выберите нужную вам опцию', reply_markup=create_menu_keyboard())
    await state.set_state(FSMForm.menu)

# Хендлеры для ввода номера телефона
@dp.message(StateFilter(FSMForm.fill_PhoneNum))
async def fill_phone_num_handler(message: Message, state: FSMContext):
    phone_num = message.text.strip()
    if re.match(r'^\+?\d{10,15}$', phone_num):  # Исправлена ошибка в регулярном выражении
        await state.update_data(PhoneNum=phone_num)
        await message.answer(
            'Спасибо! Ваш номер телефона успешно сохранен.\nА теперь можете прикрепить медиа и описать задачу',
            reply_markup=None  # Убираем клавиатуру
        )
        await state.set_state(FSMForm.fill_Task)
        print(await state.get_data())
    else:
        await message.answer('Некорректный номер телефона. Пожалуйста, введите его снова в формате +1234567890.')

@dp.callback_query(StateFilter(FSMForm.fill_PhoneNum), F.data == 'menu')
async def return_to_menu_handler(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.edit_text(
        text='Вы находитесь в меню, выберите нужную вам опцию',
        reply_markup=create_menu_keyboard()
    )
    await state.set_state(FSMForm.menu)

# Хендлеры для ввода описания заявки
@dp.message(FSMForm.fill_Task)
async def fill_task_handler(message: Message, state: FSMContext):
    media_type = None
    file_id = None
    media_description = message.caption if message.caption else ""

    # Сохраняем текст заявки независимо от наличия медиа
    if message.text:
        await state.update_data(Task=message.text)
        print(f"Текст заявки сохранен: {message.text}")  # Выводим текст заявки для проверки

    if message.photo:
        media_type = 'photo'
        file_id = message.photo[-1].file_id
    elif message.document:
        media_type = 'document'
        file_id = message.document.file_id

    # Сохраняем информацию о медиа, если она есть
    if media_type and file_id:
        await state.update_data(Media={'type': media_type, 'id': file_id, 'description': media_description})

    print(await state.get_data())  # Проверяем данные состояния
    await message.answer(
        text='Заявка создана, публикуем?', reply_markup=create_publish_keyboard()
    )
    await state.set_state(FSMForm.upload)

@dp.callback_query(StateFilter(FSMForm.fill_Task), F.data == 'menu')
async def return_to_menu_handler(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.edit_text(
        text='Вы находитесь в меню, выберите нужную вам опцию',
        reply_markup=create_menu_keyboard()
    )
    await state.set_state(FSMForm.menu)

# --- Хендлеры для отправки заявки ---
@dp.message(FSMForm.upload)
async def fill_link_handler(message: Message, state: FSMContext):
    await state.update_data(Link=message.text)
    await state.set_state(FSMForm.upload)
    await message.answer(
        text='Заявка создана, публикуем?', reply_markup=create_publish_keyboard())

@dp.callback_query(StateFilter(FSMForm.upload), F.data == 'cancel')
async def publish_clear(call: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.edit_text(text='Вы находитесь в меню, выберите нужную вам опцию', reply_markup=create_menu_keyboard())
    await state.set_state(FSMForm.menu)

@dp.callback_query(StateFilter(FSMForm.upload), F.data == 'publish')
async def publish_handler(call: CallbackQuery, state: FSMContext):
    user_data = await state.get_data()

    if user_data:
        caption = (
        f"✅ Ваша заявка успешно создана!\n"
        f'Номер заявки: {uuid.uuid4()}\n'
        f'Дата создания заявки: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}\n'
        f'Вид работ: {user_data.get("WorkType", "Не указано")}\n'
        f"📅 Дата выезда: {user_data.get('VisitDate', 'Не указана')}\n"
        f"🕒 Время выезда: {user_data.get('VisitTime', 'Не указано')}\n"
        f"🏡 Кадастровый номер: {user_data.get('GroundNum', 'Не указан')}\n"
        f"📞 Контактные данные: {user_data.get('PhoneNum', 'Не указаны')}\n"
    )

    # Получаем описание, если медиа отсутствует
    media_description = user_data.get('Media', {}).get('description', None)
    task_description = user_data.get("Task", "Не указано")

    if media_description:
        caption += f'📝 Описание: {media_description}\n'
    else:
        caption += f'📝 Описание: {task_description}\n'

    await call.answer("Заявка опубликована!")

    try:
        await call.message.delete()
    except MessageToDeleteNotFound:
        pass

    await state.clear()

    # Отправляем медиа, если оно есть
    if 'Media' in user_data and user_data['Media'] is not None:
        media_type = user_data['Media']['type']
        file_id = user_data['Media']['id']

        if media_type == 'photo':
            await bot.send_photo(chat_id=call.message.chat.id, photo=file_id, caption=caption)
        elif media_type == 'document':
            await bot.send_document(chat_id=call.message.chat.id, document=file_id, caption=caption)
    else:
        await bot.send_message(chat_id=call.message.chat.id, text=caption)

    # Добавляем кнопку для открытия кадастровой карты
    cadastre_number = user_data.get('GroundNum', '')
    base_url = "https://map.ru/pkk?kad="

    if cadastre_number:
        full_url = f"{base_url}{cadastre_number}"
    else:
        full_url = base_url

    web_app_button = InlineKeyboardButton(text="Открыть кадастровую карту", url=full_url)
    keyboard = InlineKeyboardMarkup(inline_keyboard=[[web_app_button]])

    await bot.send_message(chat_id=call.message.chat.id, text="Вы можете открыть кадастровую карту, нажав на кнопку ниже:", reply_markup=keyboard)


@dp.message(StateFilter(default_state))
async def send_echo(message: Message):
    await message.reply(text='Извините, я вас не понимаю')

if __name__ == '__main__':
    dp.run_polling(bot)
