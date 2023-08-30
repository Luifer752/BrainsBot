import logging
from core.keyboards import inline
from datetime import datetime
from aiogram import Bot, Dispatcher, types, executor
from core.middlewares.settings import settings
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.dispatcher import FSMContext

logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=logging.INFO
)


class UserState(StatesGroup):
    CHOOSE_CAT = State()
    ENTER_AMOUNT = State()
    ENTER_INCOME = State()

class Expenses:

    user_states = {}
    user_info = {"expenses": [],
                 "incomes": []}

    def __init__(self, amount, cat, time=None):
        self.amount = int(amount)
        self.cat = cat
        if not time:
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


async def on_startup(message: types.Message) -> None:
    await bot.send_message(settings.bots.admin_id,
                           text="Launched")


async def on_shutdown(message: types.Message) -> None:
    await bot.send_message(settings.bots.admin_id,
                           text="Game over")


@dp.message_handler(commands=['start'])
async def start(message: types.Message) -> None:
    logging.info("Command start was triggered")
    await bot.send_message(chat_id=message.from_user.id,
                           text=f"Hey {message.from_user.first_name}, "
                                f"welcome to Expense Bot, \n"
                                f"see func's below:",
                           parse_mode="HTML",
                           reply_markup=inline.rep_kb)


@dp.message_handler(commands=['close_keyboard'])
async def close_keyboard(message: types.Message) -> None:
    logging.info("Command close_keyboard was triggered")
    await bot.send_message(chat_id=message.from_user.id,
                           text=f"Keyboard closed, press 'Start' to open again",
                           reply_markup=inline.ReplyKeyboardRemove()
                           )


@dp.message_handler(commands=['help'])
async def helper(message: types.Message) -> None:
    await bot.send_message(chat_id=message.from_user.id,
                           text="HEEEEELLLLLPPP")


@dp.message_handler(Text(equals='/add_expense', ignore_case=True))
async def add_expense(message: types.Message) -> None:
    logging.info("Command add_expense was triggered")
    await UserState.CHOOSE_CAT.set()
    await message.answer(text="Please choose your expense category: ",
                         reply_markup=inline.in_kb)


@dp.callback_query_handler(lambda query: query.data in ["food", "health", "fun", "other"], state=UserState.CHOOSE_CAT)
async def cat_amount(callback_query: types.CallbackQuery, state: FSMContext):
    logging.info("Command cat_amount was triggered")
    async with state.proxy() as data:
        data['chosen_cat'] = callback_query.data
    await UserState.ENTER_AMOUNT.set()
    await bot.send_message(callback_query.from_user.id,
                           f"Category is '{callback_query.data}',\n"
                           f"please enter amount: ")


@dp.message_handler(state=UserState.ENTER_AMOUNT)
async def save_expense(message: types.Message, state: FSMContext) -> None:
    logging.info("Command save_expense was triggered")
    async with state.proxy() as data:
        cat = data['chosen_cat']
    amount = message.text
    expense = Expenses(amount, cat)
    Expenses.user_info["expenses"].append(expense)
    await message.answer(str(expense))
    await state.finish()


@dp.message_handler(commands=['list'])
async def op_list(message: types.Message) -> None:
    logging.info("Command op_list was triggered")
    expenses = "\n".join([f"{i + 1}. {str(t)}" for i, t in enumerate(Expenses.user_info.get("expenses", []))])
    incomes= "\n".join([f"{i + 1}. {str(t)}" for i, t in enumerate(Expenses.user_info.get("incomes", []))])
    await message.answer(f"Expenses: \n"
                         f"{expenses} \n"
                         f"Incomes: \n"
                         f"{incomes}")


@dp.message_handler(commands=['delete_operation'])
async def delete_op(message: types.Message) -> None:
    pass


def state_cancel() -> inline.ReplyKeyboardMarkup:
    logging.info("Command add_expense was triggered")
    return inline.ReplyKeyboardMarkup(resize_keyboard=True).add(inline.KeyboardButton('/cancel'))


@dp.message_handler(commands=['add_income'])
async def add_income_start(message: types.Message) -> None:
    logging.info(f"Command add_expense was ")
    await UserState.ENTER_INCOME.set()
    await message.answer("Please enter the income details in the following format:\n"
                         "amount category date \n"
                         "For example: 100 food 2023-08-30")


@dp.message_handler(state=UserState.ENTER_INCOME)
async def add_income_process(message: types.Message, state: FSMContext) -> None:
    income_details = message.text.split()
    if len(income_details) < 2:
        await message.answer("Invalid input format. Please use 'amount category [date]'.")
        return

    amount = income_details[0]
    cat = income_details[1]

    if len(income_details) > 2:
        date_str = income_details[2]
        try:
            time = datetime.strptime(date_str, '%Y-%m-%d')
        except ValueError:
            await message.answer("Invalid date format. Please use '%Y-%m-%d' format.")
            return
    else:
        time = datetime.now()

    income = Incomes(amount, cat, time)
    Expenses.user_info["incomes"].append(income)
    await message.answer(f"Income: {income} was successfully added!")
    await state.finish()



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
