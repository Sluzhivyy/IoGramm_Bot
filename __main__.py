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

    ask_TimeImportant = State()
    fill_TicketAuthor = State()
    fill_VisitDate = State()
    fill_VisitTime = State()
    fill_GroundNum = State()
    fill_Task = State()
    fill_Price = State()
    fill_Advance = State()
    fill_PhoneNum = State()
    fill_Source = State()
    fill_Link = State()
    upload_photo = State()
    upload = State()
    fill_TicketId = uuid.uuid4()
    fill_CreationDate =  datetime.now()

@dp.message(CommandStart(), StateFilter(default_state))
async def process_start_command(message: Message):
    await message.answer(
        text='Для получения информации - '
            'отправьте команду /info'
    )


@dp.message(Command(commands='cancel'), StateFilter(default_state))
async def process_cancel_command(message: Message):
    await message.answer(
        text='Отменять нечего. Вы вне машины состояний\n\n'
            'Чтобы перейти к заполнению анкеты - '
            'отправьте команду /form'
    )

@dp.message(Command(commands='cancel'), ~StateFilter(default_state))
async def process_cancel_command_state(message: Message, state: FSMContext):
    await message.answer(
        text='Вы вышли из запонения анкеты\n\n'
            'Чтобы снова перейти к заполнению анкеты - '
            'отправьте команду /form'
    )
    await state.clear()

@dp.message(Command(commands='info'))
async def process_info_command(message:Message):
    await message.answer(
        text='Это бот, который позволяет быстро и удобно заполнять формы\n\n'
            'Для начала работы отправьте /form\n\n'
            'Для отмены заполнения анкеты отправьте /cancel',)

@dp.message(Command(commands='form'), StateFilter(default_state))
async def process_form_command(message:Message, state: FSMContext):
        await message.answer(text='Вы в форме заполнения анкеты !')
        await message.answer(text='Введите имя заказчика')
        await state.set_state(FSMForm.fill_TicketAuthor)

@dp.message(StateFilter(FSMForm.fill_TicketAuthor))
async def process_name_sent(message: Message, state: FSMContext):
    await state.update_data(Name=message.text)
    print(await state.get_data())
    await state.set_state(FSMForm.fill_VisitDate)
    await process_date(message, state)

@dp.message(StateFilter(FSMForm.fill_VisitDate))
async def process_date(message:Message, state: FSMContext):
    today = date.today()
    tomorrow = today + timedelta(days=1)
    dates = [today + timedelta(days=i) for i in range(2, 6)]
    keyboard = [
        [InlineKeyboardButton(text='Сегодня', callback_data=f'date:{today.isoformat()}')],
        [InlineKeyboardButton(text='Завтра', callback_data=f'date:{tomorrow.isoformat()}')],
    ] + [
        [InlineKeyboardButton(text=f'{d.strftime("%d.%m.%y")} ({d.strftime("%a")[:2].capitalize()})',
                            callback_data=f'date:{d.isoformat()}') for d in dates]
    ]
    markup = InlineKeyboardMarkup(inline_keyboard=keyboard)
    await message.answer(
        text='Выберите дату визита к клиенту',
        reply_markup=markup
    )

@dp.callback_query(StateFilter(FSMForm.fill_VisitDate), F.data.startswith('date:'))
async def visitDate_press(callback: CallbackQuery, state: FSMContext):
    date_str = callback.data.split(':')[1]
    try:
        input_date = date.fromisoformat(date_str)
        if input_date >= date.today() and input_date < date.today() + timedelta(days=100):
            await state.update_data(VisitDate=input_date)
            await callback.message.edit_text(f'Вы выбрали дату: {input_date.strftime("%d.%m.%y")}')
            await state.set_state(FSMForm.fill_VisitTime)
            await callback.message.answer(
                text='У вас есть предпочитаемое время визита?',
                reply_markup=InlineKeyboardMarkup(
                    inline_keyboard=[
                        [InlineKeyboardButton(text='Да', callback_data='time_important:yes')],
                        [InlineKeyboardButton(text='Нет', callback_data='time_important:no')]
                    ]
                )
            )
        else:
            await callback.message.answer('Неверная дата. Пожалуйста, выберите дату в пределах ближайших 100 дней.')
    except ValueError:
        await callback.message.answer('Неверный формат даты.')

# --- Handle time selection or input ---
@dp.callback_query(StateFilter(FSMForm.fill_VisitTime), F.data.startswith('time:'))
async def process_time(callback: CallbackQuery, state: FSMContext):
    time_str = callback.data.split(':')[1]
    if time_str == 'first_half':
        await state.update_data(VisitTime='Первая половина')
        print(await state.get_data())
        await callback.message.edit_text('Вы выбрали первую половину дня.')
    elif time_str == 'second_half':
        await state.update_data(VisitTime='Вторая половина')
        print(await state.get_data())
        await callback.message.edit_text('Вы выбрали вторую половину дня.')
    else:
        await state.update_data(VisitTime=time_str)
        print(await state.get_data())
        await callback.message.edit_text(f'Вы выбрали время: {time_str}')
        await callback.message.answer(
            text='Введите кадастровый номер объекта недвижимости в отношении которого будут проводится работы (или участка на котором объект недвижимости расположен или ориентира)',
        )
    await state.set_state(FSMForm.fill_GroundNum)

@dp.message(StateFilter(FSMForm.fill_VisitTime))
async def process_time_input(message: Message, state: FSMContext):
    try:
        hour, minute = map(int, message.text.split(':'))
        if 0 <= hour <= 23 and 0 <= minute <= 59:
            await state.update_data(VisitTime=f'{hour:02}:{minute:02}')
            print(await state.get_data())
            await message.answer(f'Вы выбрали время: {hour:02}:{minute:02}')
            await state.set_state(FSMForm.fill_GroundNum)
            # Send the GroundNum question after transition
            await message.answer(
                text='Введите кадастровый номер объекта недвижимости в отношении которого будут проводится работы (или участка на котором объект недвижимости расположен или ориентира)',
            )
        else:
            await message.answer('Неверный формат времени. Пожалуйста, введите время в формате чч:мм.')
    except ValueError:
        await message.answer('Неверный формат времени. Пожалуйста, введите время в формате чч:мм.')

# --- Handle "time_important" choice ---
@dp.callback_query(StateFilter(FSMForm.fill_VisitTime), F.data.startswith('time_important:'))
async def time_important_pressed(callback: CallbackQuery, state: FSMContext):
    choice = callback.data.split(':')[1]
    if choice == 'yes':
        await callback.message.edit_text(
            text='Выберите время визита или введите своё в формате чч:мм',
            reply_markup=InlineKeyboardMarkup(
                inline_keyboard=[
                    [InlineKeyboardButton(text='Первая половина', callback_data='time:Первая половина дня')],
                    [InlineKeyboardButton(text='Вторая половина', callback_data='time:Вторая половина дня')],
                    [InlineKeyboardButton(text='Утро (09:00)', callback_data='time:Утро(Начиная с 9)')],
                    [InlineKeyboardButton(text='День (13:00)', callback_data='time:День(Начиная с 13)')],
                    [InlineKeyboardButton(text='Вечер (16:00)', callback_data='time:Вечер(начиная с 16)')]
                ]
            )
        )

    else:
        await state.update_data(VisitTime='Не важно')
        await callback.message.edit_text(text='Отлично! Время визита не важно.')
        print(await state.get_data())
        await state.set_state(FSMForm.fill_GroundNum)
        # Send the GroundNum question after transition
        await callback.message.answer(
            text='Введите кадастровый номер объекта недвижимости в отношении которого будут проводится работы (или участка на котором объект недвижимости расположен или ориентира)',
        )
# --- Handle Ground Number Input ---
@dp.message(StateFilter(FSMForm.fill_GroundNum))
async def process_GroundNum(message:Message, state: FSMContext):
    await state.update_data(GroundNum=message.text)
    print(await state.get_data())
    await message.answer(
        text='Спасибо, а теперь ввведите суть заявки'
    )
    await state.set_state(FSMForm.fill_Task)


@dp.message(StateFilter( FSMForm.fill_Task))
async def task(message:Message, state: FSMContext):
    await state.update_data(Task=message.text)
    print(await state.get_data())
    await message.answer(text = 'Превосходно, а теперь введите цену')
    await state.set_state(FSMForm.fill_Price)

@dp.message(StateFilter(FSMForm.fill_Price))
async def price(message: Message, state: FSMContext):
    await state.update_data(Price=message.text)
    print(await state.get_data())
    await state.set_state(FSMForm.fill_Advance)

    Half = InlineKeyboardButton(text='Половина на выезде', callback_data='Половина на выезде')
    Already = InlineKeyboardButton(text='Уже оплачен', callback_data='Уже оплачен')
    Office = InlineKeyboardButton(text='Полную сумму  в офисе', callback_data='Полную сумму  в офисе')
    keyboard: list[list[InlineKeyboardButton]] = [
        [Half, Already],
        [Office]
    ]
    markup = InlineKeyboardMarkup(inline_keyboard=keyboard)
    await message.answer(text='Восхитительно, а теперь выберите вариант предоплаты:', reply_markup=markup)

@dp.callback_query(StateFilter(FSMForm.fill_Advance), F.data.in_(['Половина на выезде', 'Уже оплачен', 'Полную сумму  в офисе']))
async def process_advance_press(callback: CallbackQuery, state: FSMContext):
    await state.update_data(Advance=callback.data)
    advance_choise = callback.data
    await callback.message.edit_text(f"Вы выбрали: {advance_choise}")
    await callback.message.answer(text='Хорошо, а теперь введите контактные данные и пояснения')
    await state.set_state(FSMForm.fill_PhoneNum)


@dp.message(StateFilter(FSMForm.fill_PhoneNum))
async def phone_num(message: Message, state: FSMContext):
    await state.update_data(Phone=message.text)
    print(await state.get_data())
    # Send the inline keyboard directly
    AvitoUser = InlineKeyboardButton(text='Авито пользователь', callback_data='Avito')
    SarafanUser = InlineKeyboardButton(text='Сарафан пользователь', callback_data='Sarafan')
    keyboard: list[list[InlineKeyboardButton]] = [
        [AvitoUser, SarafanUser],
    ]
    markup = InlineKeyboardMarkup(inline_keyboard=keyboard)
    await message.answer(text='Выберите источник заявки', reply_markup=markup)
    await state.set_state(FSMForm.fill_Source)

@dp.callback_query(F.data.in_(['Avito', 'Sarafan']))
async def source_press(callback: CallbackQuery, state: FSMContext):
    await state.update_data(Source=callback.data)
    print(await state.get_data())
    what = callback.data
    await callback.message.edit_text(f'Вы указали: {what}')
    await state.set_state(FSMForm.fill_Link)
    await callback.message.answer(text='Лучше не бывает, а теперь введите ссылку')

@dp.message(StateFilter(FSMForm.fill_Link))
async def process_link_sent(message:Message, state: FSMContext):
    await state.update_data(Link=message.text)
    await message.answer(text='Вы ввели ссылку: ' + message.text)
    print(await state.get_data())
    await message.answer(text='Хорошо, а теперь прикрепите ваше фото')
    await state.set_state(FSMForm.upload_photo)

@dp.message(StateFilter(FSMForm.upload_photo),
            F.photo[-1].as_('largest_photo'))
async def process_photo_sent(message: Message,state: FSMContext,largest_photo: PhotoSize):
    await state.update_data(
        photo_unique_id=largest_photo.file_unique_id,
        photo_id=largest_photo.file_id
    )
    print(await state.get_data())
    user_dict[message.from_user.id] = await state.get_data()
    await state.clear()
    await message.answer(
        text='Спасибо! Ваши данные сохранены!\n\n'
            'Вы вышли из машины состояний'
    )
    await message.answer(
        text='Чтобы посмотреть данные вашей '
            'анкеты - отправьте команду /show'
    )

@dp.message(Command(commands='show'), StateFilter(default_state))
async def process_showdata_command(message: Message):
    if user_dict:
        for user_id, user_data in user_dict.items():
            caption = (
                f'Номер заявки: {uuid.uuid4()}\n'
                f'Дата создания заявки: {datetime.now()}\n'
                f'Имя: {user_data["Name"]}\n'
                f'День визита: {user_data["VisitDate"]}\n'
                f'Время визита: {user_data["VisitTime"]}\n'
                f'Кадастровый номер: {user_data["GroundNum"]}\n'
                f'Суть заявки: {user_data["Task"]}\n'
                f'Стоимость: {user_data["Price"]}\n'
                f'Предоплата: {user_data["Advance"]}\n'
                f'Телефон: {user_data["Phone"]}\n'
                f'Источник заявки: {user_data["Source"]}\n'
                f'Ссылка на карту: {user_data["Link"]}\n'
            )

            await message.answer_photo(
                photo=user_data['photo_id'],
                caption=caption
            )
    else:

        await message.answer(
            text='Вы еще не заполняли анкету. Чтобы приступить - '
            'отправьте команду /form'
        )


@dp.message(StateFilter(default_state))
async def send_echo(message: Message):
    await message.reply(text='Извините, я вас не понимаю')

if __name__ == '__main__':
    dp.run_polling(bot)
