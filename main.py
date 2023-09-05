import logging
from core.keyboards import inline
from datetime import datetime, timedelta
from aiogram import Bot, Dispatcher, types, executor
from core.middlewares.settings import settings
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.dispatcher import FSMContext
import asyncpg
import json


logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=logging.INFO
)


class UserState(StatesGroup):
    CHOOSE_CAT = State()
    ENTER_AMOUNT = State()
    ENTER_INCOME = State()
    DELETE_OP = State()
    DELETE_ITEM = State()
    CONFIRM_DELETE = State()


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

    def to_dict(self):
        return {
            "amount": self.amount,
            "cat": self.cat,
            "time": self.time.strftime('%Y-%m-%d')
        }

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

'''ON and OFF func's'''


async def on_startup(message: types.Message) -> None:
    await bot.send_message(settings.bots.admin_id,
                           text="Launched")


async def on_shutdown(message: types.Message) -> None:
    await bot.send_message(settings.bots.admin_id,
                           text="Game over")


'''Start, buttons creation'''


@dp.message_handler(commands=['start'])
async def start(message: types.Message) -> None:
    logging.info("Command start was triggered")
    await bot.send_message(chat_id=message.from_user.id,
                           text=f"Hey {message.from_user.first_name}, "
                                f"welcome to Expense Bot, \n"
                                f"see func's below:",
                           parse_mode="HTML",
                           reply_markup=inline.rep_kb)


"""Minor func's"""

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

"""EXPENSE"""

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


"""LIST AND DELETE"""


@dp.message_handler(commands=['list'])
async def op_list(message: types.Message) -> None:
    logging.info("Command op_list was triggered")
    expenses = "\n".join([f"{i + 1}. {str(t)}" for i, t in enumerate(Expenses.user_info.get("expenses", []))])
    incomes= "\n".join([f"{i + 1}. {str(t)}" for i, t in enumerate(Expenses.user_info.get("incomes", []))])
    await UserState.DELETE_OP.set()
    await message.answer(text=f"Expenses: \n"
                         f"{expenses} \n"
                         f"Incomes: \n"
                         f"{incomes}",
                         reply_markup=inline.del_button)


@dp.callback_query_handler(lambda query: query.data == "DELETE OPERATION", state=UserState.DELETE_OP)
async def ask_item_number(callback_query: types.CallbackQuery, state: FSMContext):
    await UserState.DELETE_ITEM.set()
    await bot.send_message(callback_query.from_user.id, "Please enter the item number you want to delete:")


@dp.message_handler(lambda message: message.text.isdigit(), state=UserState.DELETE_ITEM)
async def process_item_number(message: types.Message, state: FSMContext):
    item_number = int(message.text)
    expenses = Expenses.user_info.get("expenses", [])
    incomes = Expenses.user_info.get("incomes", [])

    if 1 <= item_number <= len(expenses) or 1 <= item_number <= len(incomes):
        await bot.send_message(message.from_user.id, f"Are you sure you want to delete item {item_number}?\n"
                                                     f"Reply '+' to confirm, or '-' to cancel.")
        await UserState.CONFIRM_DELETE.set()
        await state.update_data(item_number=item_number)
    else:
        await bot.send_message(message.from_user.id, "Invalid item number. Please enter a valid number:")


@dp.message_handler(Text(equals='+', ignore_case=True), state=UserState.CONFIRM_DELETE)
async def confirm_delete(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        item_number = data['item_number']

    expenses = Expenses.user_info.get("expenses", [])
    incomes = Expenses.user_info.get("incomes", [])

    if 1 <= item_number <= len(expenses):
        deleted_item = expenses.pop(item_number - 1)
    elif 1 <= item_number <= len(incomes):
        deleted_item = incomes.pop(item_number - 1)

    await bot.send_message(message.from_user.id, f"Deleted: {deleted_item}")
    await state.finish()


@dp.message_handler(Text(equals='no', ignore_case=True), state=UserState.CONFIRM_DELETE)
async def cancel_delete(message: types.Message, state: FSMContext):
    await bot.send_message(message.from_user.id, "Deletion canceled.")
    await state.finish()


def state_cancel() -> inline.ReplyKeyboardMarkup:
    logging.info("Command state_cancel was triggered")
    return inline.ReplyKeyboardMarkup(resize_keyboard=True).add(inline.KeyboardButton('/cancel'))

'''Income'''

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


'''Stats'''


def get_stats_for_period(period):
    today = datetime.today()
    if period == "day":
        start_date = today
    elif period == "week":
        start_date = today - timedelta(days=7)
    elif period == "month":
        start_date = today - timedelta(days=30)
    else:
        return "Invalid period. Please use 'day', 'week', or 'month'."

    expenses = [expense for expense in Expenses.user_info["expenses"] if start_date <= expense.time <= today]
    incomes = [income for income in Expenses.user_info["incomes"] if start_date <= income.time <= today]

    total_expenses = sum(expense.amount for expense in expenses)
    total_incomes = sum(income.amount for income in incomes)

    result = f"Stats for the last {period}:\n"
    result += f"Total Expenses: ${total_expenses}\n"
    result += f"Total Incomes: ${total_incomes}"

    return result


async def get_statistics(message: types.Message) -> None:
    period = message.text.split()[1].lower()
    stats = get_stats_for_period(period)
    await message.answer(stats)


'''DB stuff'''

db_config = {
    "host": "localhost",
    "port": "5432",
    "user": "postgres",
    "password": "udashkin1",
    "database": "testdb"
}


@dp.message_handler(commands=['save'])
async def save_user_data_command(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    user_data_to_save = Expenses.user_info
    await save_user_data(user_id, user_data_to_save)
    await message.answer("User data has been saved.")


async def save_user_data(user_id, user_data):
    try:
        user_data_dict = {
            "expenses": [expense.to_dict() for expense in user_data.get("expenses", [])],
            "incomes": [income.to_dict() for income in user_data.get("incomes", [])]
        }

        user_data_json = json.dumps(user_data_dict)

        conn = await asyncpg.connect(**db_config)
        await conn.execute(
            "INSERT INTO user_info (user_id, data) VALUES ($1, $2) ON CONFLICT (user_id) DO UPDATE SET data = $2",
            user_id, user_data_json)

        await conn.close()
    except Exception as e:
        print(f"Error saving user data: {e}")


@dp.message_handler(commands=['load'])
async def load_user_data(user_id):
    try:
        conn = await asyncpg.connect(**db_config)
        result = await conn.fetchrow("SELECT data FROM user_info WHERE user_id = $1", user_id)
        await conn.close()

        return json.loads(result["data"]) if result else {}
    except Exception as e:
        print(f"Error loading user data: {e}")
        return {}


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

