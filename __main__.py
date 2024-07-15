from aiogram import Bot, Dispatcher, F
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.utils import executor
from env import BOT_TOKEN
from Answers import *
storage = MemoryStorage()
bot = Bot(BOT_TOKEN)
dp = Dispatcher(storage=storage)

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
