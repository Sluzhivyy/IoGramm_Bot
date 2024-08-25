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


# Состояния для FSM
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
    await state.clear()  # Очищаем состояние FSM

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
    await state.set_state(FSMForm.menu)  # Перевод в состояние меню
    await message.answer(text='Вы находитесь в меню, выберите нужную вам опцию', reply_markup=create_menu_keyboard())

# Обработчик выбора опции "Перейти в заполнение формы"
@dp.callback_query(text='form')
async def option1_handler(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text("Вы выбрали заполнение анкеты")
    await state.set_state(FSMForm.work_type)
    await callback.message.answer(text='Введите вид работ')

# Обработчик выбора опции "Получение информации по функционалу"
@dp.callback_query(text='info')
async def option2_handler(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text("Вы выбрали информацию о функционале")
    await callback.message.answer(
        text='Это бот, который позволяет быстро и удобно заполнять формы'
    )
    await state.set_state(FSMForm.menu)  # Возврат в меню

# Обработчик ввода вида работ
@dp.message(StateFilter(FSMForm.work_type))
async def process_name_sent(message: Message, state: FSMContext):
    await state.update_data(WorkType=message.text)

    PlanHouse = InlineKeyboardButton(text='Техплан жилой дом', callback_data='Техплан жилой дом')
    PlanGarage = InlineKeyboardButton(text='Техплан гараж', callback_data='Техплан гараж')
    PlanBuilding = InlineKeyboardButton(text='Техплан постройка ', callback_data='Техплан постройка ')

    GoBack = InlineKeyboardButton(text='Вернуться в главное меню', callback_data='GoBack')
    keyboard: list[list[InlineKeyboardButton]] = [
        [PlanHouse, PlanGarage],
        [PlanBuilding, GoBack]
    ]
    markup = InlineKeyboardMarkup(inline_keyboard=keyboard)
    await message.answer(text='Выбери вид работ или введи свой:', reply_markup=markup)

# Обработчик выбора типа работ с клавиатуры
@dp.callback_query(StateFilter(FSMForm.work_type), F.data.in_(['Техплан жилой дом', 'Техплан гараж', 'Техплан постройка']))
async def process_advance_press(callback: CallbackQuery, state: FSMContext):
    await state.update_data(Work=callback.data)
    work_choise = callback.data
    await callback.message.edit_text(f"Вы выбрали: {work_choise}")
    await callback.message.answer(text='Хорошо, а теперь введите контактные данные и пояснения')
    await state.set_state(FSMForm.fill_VisitDate)

# Обработчик кнопки "Вернуться в главное меню"
@dp.callback_query(StateFilter(FSMForm.work_type), F.data == 'GoBack')
async def process_go_back(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.edit_text("Вы вернулись в главное меню.")
    await state.set_state(FSMForm.menu)

# Обработчик ввода даты визита
@dp.message(FSMForm.fill_VisitDate)
async def process_date(message: Message, state: FSMContext):
    try:
        input_date = datetime.strptime(message.text, '%d.%m.%Y').date()
        if input_date >= date.today() and input_date < date.today() + timedelta(days=100):
            await state.update_data(VisitDate=input_date)
            await message.answer(f'Вы выбрали дату: {input_date.strftime("%d.%m.%y")}')
            await state.set_state(FSMForm.fill_VisitTime)
            await message.answer(
                text='Введите время выезда в формате чч:мм'
            )
        else:
            await message.answer('Неверная дата. Пожалуйста, выберите дату в пределах ближайших 100 дней.')
    except ValueError:
        await message.answer('Неверный формат даты.')

# Обработчик ввода времени визита
@dp.message(FSMForm.fill_VisitTime)
async def process_time_input(message: Message, state: FSMContext):
    try:
        hour, minute = map(int, message.text.split(':'))
        if 0 <= hour <= 23 and 0 <= minute <= 59:
            await state.update_data(VisitTime=f'{hour:02}:{minute:02}')
            await message.answer(f'Вы выбрали время: {hour:02}:{minute:02}')
            await state.set_state(FSMForm.fill_GroundNum)
            await message.answer(text='Введите кадастровый номер объекта работ (или ориентира, или земельного участка на котором находится объект работ, или кадастрового квартала, если ориентира нет)'
            )
        else:
            await message.answer('Неверный формат времени. Пожалуйста, введите время в формате чч:мм.')
    except ValueError:
        await message.answer('Неверный формат времени. Пожалуйста, введите время в формате чч:мм.')

# Обработчик ввода кадастрового номера
@dp.message(FSMForm.fill_GroundNum)
async def process_GroundNum(message: Message, state: FSMContext):
    await state.update_data(GroundNum=message.text)
    await message.answer(
        text='Введите кадастровый номер объекта работ (или ориентира, или земельного участка на котором находится объект работ, или кадастрового квартала, если ориентира нет)',
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text='Ввести кадастровый позже', callback_data='Later')],
                [InlineKeyboardButton(text='Назад', callback_data='Back')],
                [InlineKeyboardButton(text='Отменить ввод', callback_data='menu')]
            ]
        )
    )

# Обработчик кнопки "Ввести кадастровый позже"
@dp.callback_query(text='Later')
async def choise_later(callback: CallbackQuery, state: FSMContext):
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

# Обработчик кнопки "Назад" в вводе кадастрового номера
@dp.callback_query(text='Back')
async def back_to_prev(callback: CallbackQuery, state: FSMContext):
    await state.set_state(FSMForm.fill_VisitTime)
    await callback.message.edit_text(
        text='Введите время выезда в формате чч:мм'
    )

# Обработчик кнопки "Отменить ввод" в вводе кадастрового номера
@dp.callback_query(text='menu')
async def return_to_menu(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.edit_text('Вы вернулись в главное меню.')
    await state.set_state(FSMForm.menu)
    await callback.message.answer(text='Вы находитесь в меню, выберите нужную вам опцию', reply_markup=create_menu_keyboard())

# Обработчик ввода описания заявки
@dp.message(FSMForm.fill_Task)
async def task(message: Message, state: FSMContext):
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

# Обработчик ввода медиафайлов в описании заявки
@dp.message(FSMForm.fill_Task_Media)
async def task_media(message: Message, state: FSMContext):
    if message.photo or message.document:
        await state.update_data(Media=message)
        await state.set_state(FSMForm.fill_Price)
        await message.answer(
            text='Введите желаемую цену работ'
        )
    else:
        await message.answer("Пожалуйста, прикрепите фото или файл.")

# Обработчик кнопки "Назад" в описании заявки
@dp.callback_query(text='Back')
async def back_to_prev(callback: CallbackQuery, state: FSMContext):
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

# Обработчик кнопки "Ввести позже" в описании заявки
@dp.callback_query(text='Later')
async def choise_later(callback: CallbackQuery, state: FSMContext):
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

# Обработчик кнопки "Отменить ввод" в описании заявки
@dp.callback_query(text='menu')
async def return_to_menu(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.edit_text('Вы вернулись в главное меню.')
    await state.set_state(FSMForm.menu)
    await callback.message.answer(text='Вы находитесь в меню, выберите нужную вам опцию', reply_markup=create_menu_keyboard())

# Обработчик ввода цены
@dp.message(FSMForm.fill_Price)
async def price(message: Message, state: FSMContext):
    await state.update_data(Price=message.text)
    keyboard: list[list[InlineKeyboardButton]] = [
        [InlineKeyboardButton(text='Назад', callback_data='Back')],
        [InlineKeyboardButton(text='Ввести позже', callback_data='Later')],[InlineKeyboardButton(text='Отменить ввод', callback_data='menu')]
    ]
    markup = InlineKeyboardMarkup(inline_keyboard=keyboard)
    await message.edit_text(text='Восхитительно, а теперь выберите вариант предоплаты:', reply_markup=markup)

# Обработчик кнопки "Назад" в вводе цены
@dp.callback_query(text='Back')
async def back_to_prev(callback: CallbackQuery, state: FSMContext):
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

# Обработчик кнопки "Ввести позже" в вводе цены
@dp.callback_query(text='Later')
async def choise_later(callback: CallbackQuery, state: FSMContext):
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

# Обработчик кнопки "Отменить ввод" в вводе цены
@dp.callback_query(text='menu')
async def return_to_menu(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.edit_text('Вы вернулись в главное меню.')
    await state.set_state(FSMForm.menu)
    await callback.message.answer(text='Вы находитесь в меню, выберите нужную вам опцию', reply_markup=create_menu_keyboard())

# Обработчик ввода источника заявки
@dp.message(FSMForm.fill_Source)
async def phone_num(message: Message, state: FSMContext):
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

# Обработчик выбора источника заявки с клавиатуры
@dp.callback_query(text_contains=['Я Авито', 'Я Сарафан', 'Я Ркк', 'Другой пользователь'])
async def source_press(callback: CallbackQuery, state: FSMContext):
    await state.update_data(Source=callback.data)
    what = callback.data
    await callback.message.edit_text(f'Вы указали: {what}')
    await state.set_state(FSMForm.fill_Link)
    await callback.message.answer(text='Лучше не бывает, а теперь введите ссылку')

# Обработчик кнопки "Назад" в выборе источника заявки
@dp.callback_query(text='Back')
async def back_to_prev(callback: CallbackQuery, state: FSMContext):
    await state.set_state(FSMForm.fill_Price)
    await callback.message.edit_text(
        text='Введите желаемую цену работ'
    )

# Обработчик кнопки "Ввести позже" в выборе источника заявки
@dp.callback_query(text='Later')
async def choise_later(callback: CallbackQuery, state: FSMContext):
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

# Обработчик кнопки "Отменить ввод" в выборе источника заявки
@dp.callback_query(text='menu')
async def return_to_menu(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.edit_text('Вы вернулись в главное меню.')
    await state.set_state(FSMForm.menu)
    await callback.message.answer(text='Вы находитесь в меню, выберите нужную вам опцию', reply_markup=create_menu_keyboard())

# Обработчик ввода ссылки
@dp.message(FSMForm.fill_Link)
async def process_link(message: Message, state: FSMContext):
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

# Обработчик отправки заявки
@dp.callback_query(text='publish')
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
            pass  # В случае, если сообщение уже было удалено
        await state.finish()
        if 'Media' in user_data:
            await bot.send_photo(chat_id=call.message.chat.id, photo=user_data['Media'], caption=caption)
        else:
            await bot.send_message(chat_id=call.message.chat.id, text=caption)

# Обработчик отправки заявки и создания новой
@dp.callback_query(text='publish_and_create')
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

# Обработчик кнопки "Назад" при просмотре заявки
@dp.callback_query(text='Back')
async def back_handler(call: CallbackQuery, state: FSMContext):
    await call.answer("Вернулись к предыдущему шагу")
    await call.message.delete()
    await state.set_state(FSMForm.fill_Link)
    await call.message.answer(text='Лучше не бывает, а теперь введите ссылку')

# Обработчик кнопки "Отменить ввод" при просмотре заявки
@dp.callback_query(text='cancel')
async def cancel_handler(call: CallbackQuery, state: FSMContext):
    await call.answer("Ввод отменен")
    await call.message.delete()
    await state.clear()
    await state.set_state(FSMForm.menu)
    await call.message.answer(text='Вы находитесь в меню, выберите нужную вам опцию', reply_markup=create_menu_keyboard())

if __name__ == '__main__':
    dp.run_polling(bot)