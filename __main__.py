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

class FSMForm(StatesGroup):
    menu = State()
    work_type = State()
    fill_VisitDate = State()
    fill_VisitTime = State()
    fill_GroundNum = State()
    fill_Task = State()
    fill_Price = State()
    fill_Source = State()
    fill_Link = State()
    upload = State()
    fill_Task_Media = State()

# Функция для создания клавиатуры
def create_menu_keyboard():
    Form = InlineKeyboardButton(text='Перейти в заполнение формы', callback_data='/form')
    Info = InlineKeyboardButton(text='Получение информации по функционалу', callback_data='/info')
    keyboard: list[list[InlineKeyboardButton]] = [
        [Form, Info],
    ]
    markup = InlineKeyboardMarkup(inline_keyboard=keyboard)
    return markup

# Обработчик команды /start
@dp.message(CommandStart(), StateFilter(FSMForm.menu))
async def process_start_command(message: Message):
    await message.answer(
        text='Для получения информации - '
            'отправьте команду /info'
            'Для перехода в меню, отправте команду /menu'
    )

# Обработчик команды /cancel
@dp.message(Command(commands='cancel'), StateFilter(FSMForm.menu))
async def process_cancel_command(message: Message):
    await message.answer(
        text='Отменять нечего. Вы вне машины состоянийnn'
            'Чтобы перейти к заполнению анкеты - '
    )

# Обработчик команды /cancel при нахождении в FSM
@dp.message(Command(commands='cancel'), ~StateFilter(FSMForm.menu))
async def process_cancel_command_state(message: Message, state: FSMContext):
    await message.answer(
        text='Вы вышли из запонения анкетыnn'
            'Чтобы снова перейти к заполнению анкеты - '
    )
    await state.clear()

# Обработчик команды /info
@dp.message(Command(commands='info'))
async def process_info_command(message: Message):
    await message.answer(
        text='Это бот, который позволяет быстро и удобно заполнять формы\n\n'
    )

# Обработчик команды /menu
@dp.message(Command(commands='menu'), StateFilter(FSMForm.menu))
async def process_menu(message: Message, state: FSMContext):
    markup = create_menu_keyboard()
    await message.edit_text(text='Вы находитесь в меню, выберите нужную вам опцию', reply_markup=markup)

# Обработчик выбора опции "Перейти в заполнение формы"
@dp.message_handler(lambda message: message == "/form", state=FSMForm.menu)
async def option1_handler(message: Message, state: FSMContext):
    await message.answer("Вы выбрали заполнение анкеты")
    await state.set_state(FSMForm.work_type)

# Обработчик выбора опции "Получение информации по функционалу"
@dp.message_handler(lambda message: message == "/info", state=FSMForm.menu)
async def option1_handler(message: Message, state: FSMContext):
    await message.answer("Вы выбрали информацию о функционале")
    await state.set_state(FSMForm.menu)

# Обработчик ввода типа работ
@dp.message(StateFilter(FSMForm.work_type))
async def process_name_sent(message: Message, state: FSMContext):
    await state.update_data(WorkType=message.text)
    await state.set_state(FSMForm.fill_VisitDate)

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
    await state.set_state(FSMForm.fill_PhoneNum)

# Обработчик кнопки "Вернуться в главное меню"
@dp.callback_query(StateFilter(FSMForm.work_type), F.data == 'GoBack')
async def process_go_back(callback: CallbackQuery, state: FSMContext):
    await state.finish()
    await callback.message.edit_text("Вы вернулись в главное меню.")
    await state.set_state(FSMForm.menu)

# Обработчик ввода даты визита
@dp.message(StateFilter(FSMForm.fill_VisitDate))
async def process_date(message: Message, state: FSMContext):
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
    async def process_info_command(message: Message):
        await message.answer(
        text='Это бот, который позволяет быстро и удобно заполнять формы\n\n'
    )

# Обработчик команды /menu
@dp.message(Command(commands='menu'), StateFilter(FSMForm.menu))
async def process_menu(message: Message, state: FSMContext):
    markup = create_menu_keyboard()
    await message.edit_text(text='Вы находитесь в меню, выберите нужную вам опцию', reply_markup=markup)

# Обработчик выбора опции "Перейти в заполнение формы"
@dp.message_handler(lambda message: message == "/form", state=FSMForm.menu)
async def option1_handler(message: Message, state: FSMContext):
    await message.answer("Вы выбрали заполнение анкеты")
    await state.set_state(FSMForm.work_type)

# Обработчик выбора опции "Получение информации по функционалу"
@dp.message_handler(lambda message: message == "/info", state=FSMForm.menu)
async def option1_handler(message: Message, state: FSMContext):
    await message.answer("Вы выбрали информацию о функционале")
    await state.set_state(FSMForm.menu)

# Обработчик ввода типа работ
@dp.message(StateFilter(FSMForm.work_type))
async def process_name_sent(message: Message, state: FSMContext):
    await state.update_data(WorkType=message.text)
    await state.set_state(FSMForm.fill_VisitDate)

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
    await state.set_state(FSMForm.fill_PhoneNum)

# Обработчик кнопки "Вернуться в главное меню"
@dp.callback_query(StateFilter(FSMForm.work_type), F.data == 'GoBack')
async def process_go_back(callback: CallbackQuery, state: FSMContext):
    await state.finish()
    await callback.message.edit_text("Вы вернулись в главное меню.")
    await state.set_state(FSMForm.menu)

# Обработчик ввода даты визита
@dp.message(StateFilter(FSMForm.fill_VisitDate))
async def process_date(message: Message, state: FSMContext):
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
    await message.answer(text='Выбери дату выезда или введи свою (дд.мм.гггг)',
        reply_markup=markup
    )

# Обработчик выбора даты визита с клавиатуры
@dp.callback_query(StateFilter(FSMForm.fill_VisitDate), F.data.startswith('date:'))
async def visitDate_press(callback: CallbackQuery, state: FSMContext):
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

# Обработчик кнопки "В главное меню" в выборе даты
@dp.callback_query(StateFilter(FSMForm.fill_VisitDate), F.data == 'menu')
async def return_to_menu(callback: CallbackQuery, state: FSMContext):
    await state.finish()
    await callback.message.edit_text('Вы вернулись в главное меню.')
    await state.set_state(FSMForm.menu)

# Обработчик ввода времени визита
@dp.message(StateFilter(FSMForm.fill_VisitTime))
async def process_time_input(message: Message, state: FSMContext):
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

# Обработчик ввода кадастрового номера
@dp.message(StateFilter(FSMForm.fill_GroundNum))
async def process_GroundNum(message: Message, state: FSMContext):
    await state.update_data(GroundNum=message.text)
    await message.edit_text(
            text='Введи кадастровый номер объекта работ (или ориентира, или земельного участка на котором находится объект работ, или кадастрового квартала, если ориентира нет)',
            reply_markup=InlineKeyboardMarkup(
                inline_keyboard=[
                    [InlineKeyboardButton(text='Ввести кадастровый позже', callback_data='Later')],
                    [InlineKeyboardButton(text='Назад', callback_data='Back')],
                    [InlineKeyboardButton(text='Отменить ввод', callback_data='menu')]
                ]
            )
        )

# Обработчик кнопки "Ввести кадастровый позже"
@dp.callback_query(StateFilter(FSMForm.fill_GroundNum), F.data == 'Later')
async def choise_later(callback: CallbackQuery, state: FSMContext):
    await state.set_state(FSMForm.fill_Task)

# Обработчик кнопки "Назад" в вводе кадастрового номера
@dp.callback_query(StateFilter(FSMForm.fill_GroundNum), F.data == 'Back')
async def back_to_prev(callback: CallbackQuery, state: FSMContext):
    await state.finish()
    await state.set_state(FSMForm.fill_VisitTime)

# Обработчик кнопки "Отменить ввод" в вводе кадастрового номера
@dp.callback_query(StateFilter(FSMForm.fill_GroundNum), F.data == 'menu')
async def return_to_menu(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.edit_text('Вы вернулись в главное меню.')
    await state.set_state(FSMForm.menu)

# Обработчик ввода описания заявки
@dp.message(StateFilter(FSMForm.fill_Task))
async def task(message: Message, state: FSMContext):
    await state.update_data(Task=message.text)
    await message.edit_text(
            text='Введи описание заявки (суть работ) - всё что ты хочешь сказать относительно заявки, не вошедшее в предыдущие поля. Если надо прикрепить изображения или файлы - можешь это сделать здесь же.',
            reply_markup=InlineKeyboardMarkup(
                inline_keyboard=[
                    [InlineKeyboardButton(text='Назад', callback_data='back')],
                    [InlineKeyboardButton(text='Ввести позже', callback_data='later')],
                    [InlineKeyboardButton(text='Отменить ввод', callback_data='menu')]
                ]
            )
        )

# Обработчик ввода медиафайлов в описании заявки
@dp.message(StateFilter(FSMForm.fill_Task_Media))
async def task_media(message: Message, state: FSMContext):
    if message.photo or message.document:
        await state.update_data(Media=message)
        await state.set_state(FSMForm.fill_Price)
    else:
        await message.answer("Пожалуйста, прикрепите фото или файл.")

# Обработчик кнопки "Назад" в описании заявки
@dp.callback_query(StateFilter(FSMForm.fill_Task), F.data == 'back')
async def back_to_prev(callback: CallbackQuery, state: FSMContext):
    await state.finish()
    await state.set_state(FSMForm.fill_GroundNum)

# Обработчик кнопки "Ввести позже" в описании заявки
@dp.callback_query(StateFilter(FSMForm.fill_Task), F.data == 'later')
async def choise_later(callback: CallbackQuery, state: FSMContext):
    await state.set_state(FSMForm.fill_Source)

# Обработчик кнопки "Отменить ввод" в описании заявки
@dp.callback_query(StateFilter(FSMForm.fill_Task), F.data == 'menu')
async def return_to_menu(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.edit_text('Вы вернулись в главное меню.')
    await state.set_state(FSMForm.menu)

# Обработчик ввода цены
@dp.message(StateFilter(FSMForm.fill_Price))
async def price(message: Message, state: FSMContext):
    await state.update_data(Price=message.text)
    keyboard: list[list[InlineKeyboardButton]] = [
        [InlineKeyboardButton(text='Назад', callback_data='back')],
        [InlineKeyboardButton(text='Ввести позже', callback_data='later')],
        [InlineKeyboardButton(text='Отменить ввод', callback_data='menu')]
    ]
    markup = InlineKeyboardMarkup(inline_keyboard=keyboard)
    await message.edit_text(text='Восхитительно, а теперь выберите вариант предоплаты:', reply_markup=markup)


# Обработчик кнопки "Назад" в вводе цены
@dp.callback_query(StateFilter(FSMForm.fill_Price), F.data == 'back')
async def back_to_prev(callback: CallbackQuery, state: FSMContext):
    await state.finish()
    await state.set_state(FSMForm.fill_Task)

# Обработчик кнопки "Ввести позже" в вводе цены
@dp.callback_query(StateFilter(FSMForm.fill_Price), F.data == 'later')
async def choise_later(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text(text='Хорошо, вы можете ввести цену позже.')
    await state.set_state(FSMForm.fill_Source)

# Обработчик кнопки "Отменить ввод" в вводе цены
@dp.callback_query(StateFilter(FSMForm.fill_Price), F.data == 'menu')
async def return_to_menu(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.edit_text('Вы вернулись в главное меню.')
    await state.set_state(FSMForm.menu)

# Обработчик ввода источника заявки
@dp.message(StateFilter(FSMForm.fill_Source))
async def phone_num(message: Message, state: FSMContext):
    await state.update_data(Phone=message.text)
    keyboard: list[list[InlineKeyboardButton]] = [
        [InlineKeyboardButton(text='Назад', callback_data='back')],
        [InlineKeyboardButton(text='Ввести позже', callback_data='later')],
        [InlineKeyboardButton(text='Отменить ввод', callback_data='menu')],
        [InlineKeyboardButton(text='Я Авито', callback_data='Я Авито')],
        [InlineKeyboardButton(text='Я Сарафан', callback_data='Я Сарафан')],
        [InlineKeyboardButton(text='Я Ркк', callback_data='Я Ркк')],
        [InlineKeyboardButton(text='Другой пользователь', callback_data='Другой пользователь')]

    ]
    markup = InlineKeyboardMarkup(inline_keyboard=keyboard)
    await message.answer(text='Выбери источник заявки или введи вручную', reply_markup=markup)

# Обработчик выбора источника заявки с клавиатуры
@dp.callback_query(F.data.in_(['Я Авито', 'Я Сарафан', 'Я Ркк', 'Другой пользователь']))
async def source_press(callback: CallbackQuery, state: FSMContext):
    await state.update_data(Source=callback.data)
    what = callback.data
    await callback.message.edit_text(f'Вы указали: {what}')
    await state.set_state(FSMForm.fill_Link)
    await callback.message.answer(text='Лучше не бывает, а теперь введите ссылку')

# Обработчик кнопки "Назад" в выборе источника заявки
@dp.callback_query(StateFilter(FSMForm.fill_Source), F.data == 'back')
async def back_to_prev(callback: CallbackQuery, state: FSMContext):
    await state.finish()
    await state.set_state(FSMForm.fill_Task)

# Обработчик кнопки "Ввести позже" в выборе источника заявки
@dp.callback_query(StateFilter(FSMForm.fill_Source), F.data == 'later')
async def choise_later(callback: CallbackQuery, state: FSMContext):
    await state.set_state(FSMForm.upload)

# Обработчик кнопки "Отменить ввод" в выборе источника заявки
@dp.callback_query(StateFilter(FSMForm.fill_Source), F.data == 'menu')
async def return_to_menu(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.edit_text('Вы вернулись в главное меню.')
    await state.set_state(FSMForm.menu)

# Обработчик ввода ссылки
@dp.message(StateFilter(FSMForm.fill_Link))
async def process_link(message: Message, state: FSMContext):
    await state.update_data(Link=message.text)
    await state.set_state(FSMForm.upload)
    await message.answer(
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
                    InlineKeyboardButton(text="Назад", callback_data="back"),
                    InlineKeyboardButton(text="Отменить ввод", callback_data="cancel"),
                ]
            ]
        )
    )

# Обработчик отправки заявки
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
            f'Суть заявки: {user_data["Task"]}\n'
            f'Стоимость: {user_data["Price"]}\n'
            f'Источник заявки: {user_data["Source"]}\n'
            f'Ссылка: {user_data["Link"]}\n'
        )
        await call.answer("Заявка опубликована!")
        await call.message.delete()
        await state.finish()
        await bot.send_photo(chat_id=call.message.chat.id, photo=user_data['Media'], caption=caption)

# Обработчик отправки заявки и создания новой
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
        await call.message.delete()
        await state.set_state(FSMForm.menu)
        await bot.send_photo(chat_id=call.message.chat.id, photo=user_data['Media'], caption=caption)

# Обработчик кнопки "Назад" при просмотре заявки
@dp.callback_query_handler(StateFilter(FSMForm.upload), F.data == 'back')
async def back_handler(call: CallbackQuery, state: FSMContext):
    await call.answer("Вернулись к предыдущему шагу")
    await call.message.delete()
    await state.set_state(FSMForm.fill_Source)

# Обработчик кнопки "Отменить ввод" при просмотре заявки
@dp.callback_query_handler(StateFilter(FSMForm.upload), F.data == 'cancel')
async def cancel_handler(call: CallbackQuery, state: FSMContext):
    await call.answer("Ввод отменен")
    await call.message.delete()
    await state.clear()

if __name__ == '__main__':
    dp.run_polling(bot)