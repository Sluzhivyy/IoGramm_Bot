import uuid
from datetime import datetime, date, timedelta
from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command, CommandStart, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import default_state, State, StatesGroup
from aiogram.types import (CallbackQuery, InlineKeyboardButton,InlineKeyboardMarkup, Message, PhotoSize)
from aiogram.fsm.storage.memory import MemoryStorage
from env import BOT_TOKEN
storage = MemoryStorage()
bot = Bot(BOT_TOKEN)
dp = Dispatcher(storage=storage)

user_dict: dict[int, dict[str, str | int]] = {}
class FSMForm(StatesGroup):


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
    await state.update_data(name=message.text)
    print(await state.get_data())
    await state.set_state(FSMForm.fill_VisitDate)

@dp.message(StateFilter(FSMForm.fill_VisitDate))
async def process_date(message:Message, state: FSMContext):
    dates = [date.today() + timedelta(days=i) for i in range(1, 5)]
    keyboard = [
        [InlineKeyboardButton(text=str(d), callback_data=f'date:{d}') for d in dates],
    ]
    markup = InlineKeyboardMarkup(inline_keyboard=keyboard)
    await message.answer(
        text='Введите дату, ниже выведены подсказки по датам',
        reply_markup=markup
    )


@dp.callback_query(StateFilter(FSMForm.fill_VisitDate), F.data.startswith('date:'))
async def VisitDate_press(callback: CallbackQuery, state: FSMContext):
    date_str = callback.data.split(':')[1]
    try:
        input_date = date.fromisoformat(date_str)
        if input_date >= date.today() and input_date < date.today() + timedelta(days=100):
            await state.update_data(VisitDate=input_date)
            await callback.message.answer(f'Вы выбрали дату: {input_date.strftime("%Y-%m-%d")}')
            print(await state.get_data())
            await state.set_state(FSMForm.fill_VisitTime)

        else:
            await callback.message.answer(text='Неверная дата. Пожалуйста, введите дату в формате yyyy-mm-dd, не ранее сегодняшнего дня и не позднее 100 дней от сегодняшнего.')
    except ValueError:
        await callback.message.answer(text='Неверный формат даты. Пожалуйста, введите дату в формате yyyy-mm-dd.')

@dp.message(StateFilter(FSMForm.fill_VisitTime))
async def Visit_Timed(message: Message, state: FSMContext):
    FirstPart = InlineKeyboardButton(text='Первая половина дня', callback_data='FirstPart')
    SecondPart = InlineKeyboardButton(text='Вторая половина дня', callback_data='SecondPart')
    Morning = InlineKeyboardButton(text='Утро', callback_data='Morning')
    Day = InlineKeyboardButton(text='День', callback_data='Daytime')
    Evening = InlineKeyboardButton(text='Вечер', callback_data='Evening')

    keyboard = [
        [FirstPart, SecondPart],
        [Morning, Day, Evening]
    ]
    markup = InlineKeyboardMarkup(inline_keyboard=keyboard)
    await message.answer(
        text='Спасибо, а теперь выберите время визита',
        reply_markup=markup
    )


@dp.callback_query(F.data.in_(['FirstPart', 'SecondPart', 'Morning', 'Daytime', 'Evening']))
async def VisitTime_press(callback: CallbackQuery, state: FSMContext):
    await state.update_data(VisitTime=callback.data)
    await callback.message.answer(f'Вы выбрали время: {callback.data}')
    print(await state.get_data())
    await callback.message.answer(text = 'Потрясающе, а теперь введите номер земельного участка')
    await state.set_state(FSMForm.fill_GroundNum)


@dp.message(StateFilter(FSMForm.fill_GroundNum))
async def Price_(message:Message, state: FSMContext):
        await state.update_data(GroundNum=message.text)
        print(await state.get_data())
        await message.answer(text = 'Спасибо, а теперь ввведите суть заявки')
        await state.set_state(FSMForm.fill_Task)

@dp.message(StateFilter( FSMForm.fill_Task))
async def Task_(message:Message, state: FSMContext):
    await state.update_data(Task=message.text)
    print(await state.get_data())
    await message.answer(text = 'Превосходно, а теперь введите цену')
    await state.set_state(FSMForm.fill_Price)

@dp.message(StateFilter(FSMForm.fill_Price))
async def Task_(message:Message, state: FSMContext):
    await state.update_data(Price=message.text)
    print(await state.get_data())
    await state.set_state(FSMForm.fill_Advance)

@dp.message(StateFilter(FSMForm.fill_Advance))
async def Advance(message: Message, state: FSMContext):
    Half = InlineKeyboardButton(text='Половина на выезде', callback_data='Half')
    Already = InlineKeyboardButton(text='Уже оплачен', callback_data='Already')
    Office = InlineKeyboardButton(text='Полную сумму  в офисе', callback_data='Office')
    Another = InlineKeyboardButton(text='Иное', callback_data='Another')
    keyboard: list[list[InlineKeyboardButton]] = [
        [Half, Already],
        [Office,Another]
    ]
    markup = InlineKeyboardMarkup(inline_keyboard=keyboard)
    await message.answer(text= 'Восхитительно, а теперь выберите вариант предоплаты', reply_markup = markup)


@dp.callback_query(StateFilter(FSMForm.fill_Advance),
                F.data.in_(['Half', 'Already', 'Office', 'Another']))
async def process_Advance_press(callback: CallbackQuery, state: FSMContext):
        await state.update_data(Advance=callback.data)
        await callback.message.answer(text= 'Супер, а теперь введите номер/а заказчика и пояснение/я')
        await state.set_state(FSMForm.fill_PhoneNum)


@dp.message(StateFilter(FSMForm.fill_PhoneNum))
async def PhoneNum1(message: Message, state: FSMContext):
    await state.update_data(Phone1=message.text)
    print(await state.get_data())
    await state.set_state(FSMForm.fill_Source)

@dp.message(StateFilter(FSMForm.fill_Source))
async def Source_Answer(message: Message, state: FSMContext):
    MyselfAvio = InlineKeyboardButton(text='Я Авито', callback_data='MyselfAvito')
    MyselfSarafan = InlineKeyboardButton(text='Я Сарафан', callback_data='MyselfSarafan')
    AvitoUser = InlineKeyboardButton(text='Авито пользователь', callback_data='AvitoUser')
    SarafanUser = InlineKeyboardButton(text='Сарафан пользователь', callback_data='SarafanUser')
    keyboard: list[list[InlineKeyboardButton]] = [
        [MyselfAvio, MyselfSarafan],
        [AvitoUser,SarafanUser]
    ]
    markup = InlineKeyboardMarkup(inline_keyboard=keyboard)
    await message.answer(text='Выберите источник заявки',reply_markup = markup)

@dp.callback_query(StateFilter(FSMForm.fill_Source),
                F.data.in_(['MyselfAvito', 'MyselfSarafan', 'AvitoUser', 'SarafanUser']))
async def Source_press(callback: CallbackQuery, state: FSMContext):
        await state.update_data(Source=callback.data)
        print(await state.get_data())
        await callback.message.answer(text='Лучше не бывает, а теперь введите ссылку')
        await state.set_state(FSMForm.fill_Link)

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
                    f'Источник заявки: {user_dict[message.from_user.id]["Source"]}\n'
                    f'Ссылка на карту: {user_dict[message.from_user.id]["Link"]}\n'
        )
    else:

        await message.answer(
            text='Вы еще не заполняли анкету. Чтобы приступить - '
            'отправьте команду /start'
        )


@dp.message(StateFilter(default_state))
async def send_echo(message: Message):
    await message.reply(text='Извините, я вас не понимаю')

if __name__ == '__main__':
    dp.run_polling(bot)
