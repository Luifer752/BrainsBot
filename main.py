import logging
from core.keyboards import inline
from datetime import datetime
from aiogram import Bot, Dispatcher, types, executor
from core.middlewares.settings import settings
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher.filters.state import StatesGroup, State


logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=logging.INFO
)

class UserState(StatesGroup):
    CHOOSE_CAT = State()
    ENTER_AMOUNT = State
class Expenses:

    user_states = {}
    user_info = {"expenses": [],
                 "incomes": []}

    def __init__(self, amount, cat, time=None):
        self.amount = int(amount)
        self.cat = cat
        if time:
            self.time = datetime.now()
        else:
            self.time = time

        self.to_user_info()

    def to_user_info(self):
        cat_val = Expenses.user_info.get(self.cat)
        if not cat_val:
            Expenses.user_info[self.cat] = [self]
        else:
            cat_val.append(self)

    def __str__(self):
        return f"${self.amount}, spent for {self.cat}, on {self.time.strftime('%Y-%m-%d')}"


class Incomes(Expenses):
    def __init__(self, amount, cat, time=None):
        super().__init__(amount, cat, time)

    def __str__(self):
        return f"${self.amount} received for {self.cat}, on {self.time.strftime('%Y-%m-%d')}"


storage = MemoryStorage()

bot = Bot(token=settings.bots.bot_token,
          parse_mode="HTML")

dp = Dispatcher(bot=bot,
                storage=storage)


async def on_startup(message: types.Message):
    await bot.send_message(settings.bots.admin_id,
                           text="Launched")


async def on_shutdown(message: types.Message):
    await bot.send_message(settings.bots.admin_id,
                           text="Game over")


@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    await bot.send_message(chat_id=message.from_user.id,
                           text=f"Hey {message.from_user.first_name}, see func's below:",
                           parse_mode="HTML",
                           reply_markup=inline.rep_kb)


@dp.message_handler(commands=['close_keyboard'])
async def close_keyboard(message: types.Message):
    await bot.send_message(chat_id=message.from_user.id,
                           text=f"Keyboard closed, press 'Start' to open again",
                           reply_markup=inline.ReplyKeyboardRemove()
                           )


@dp.message_handler(commands=['help'])
async def helper(message: types.Message):
    await bot.send_message(chat_id=message.from_user.id,
                           text="HEEEEELLLLLPPP")


@dp.callback_query_handler(Text(equals='', ignore_case=True))
async def cat_callback(callback: types.CallbackQuery):
    logging.info(f"Command cat_callback was triggered, {callback.data}")
    cat = callback.data
    user_id = callback.from_user.id
    await callback.answer(f"Category is '{cat}',\n"
                          "please enter amount: ")
    #await



@dp.message_handler(commands=['add_expense'])
async def add_expense(message: types.Message):
    logging.info("Command add_expense was triggered")
    await State
    await message.answer(text="Please choose your expense category: ",
                         reply_markup=inline.in_kb)



async def run():

    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()


if __name__ == '__main__':
    executor.start_polling(dispatcher=dp,
                           skip_updates=True,
                           on_startup=on_startup,
                           on_shutdown=on_shutdown
                           )
