import logging

from datetime import datetime, timedelta
from telegram import Update, ReplyKeyboardMarkup,\
    KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardRemove

from telegram.ext import ApplicationBuilder, CallbackContext, \
    CommandHandler, CallbackQueryHandler, ConversationHandler


TOKEN = '6694866011:AAGee_T16mY22-w7QF49MVfE5Zfs09JIGYw'

logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=logging.INFO
)


class Expenses:

    user_data = {"expenses" : [],
                 "incomes" : []}

    def __init__(self, amount, cat, time=None):
        self.amount = int(amount)
        self.cat = cat
        if time:
            self.time = datetime.now()
        else:
            self.time = time

        self.to_user_data()

    def to_user_data(self):
        cat_val = Expenses.user_data.get(self.cat)
        if not cat_val:
            Expenses.user_data[self.cat] = [self]
        else:
            cat_val.append(self)

    def __str__(self):
        return f"${self.amount}, spent for {self.cat}, on {self.time.strftime('%Y-%m-%d')}"


class Incomes(Expenses):
    def __init__(self, amount, cat, time=None):
        super().__init__(amount, cat, time)

    def __str__(self):
        return f"${self.amount} received for {self.cat}, on {self.time.strftime('%Y-%m-%d')}"


async def start(update: Update, context: CallbackContext) -> None:
    logging.info("Command start was triggered")
    keyboard = [['/add_expense', '/add_income',],
                  ['/list', '/save'],
                ['/delete_operation', '/stats', '/close_keyboard']]
    markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=False)
    await update.message.reply_text(
        "Welcome to BrainsExpenseBot!\n"
        "Please see below options: ",
        reply_markup=markup
    )


async def close_keyboard(update: Update, context: CallbackContext):
    await update.message.reply_text('Keyboard closed', reply_markup=ReplyKeyboardRemove())


async def add_expense(update: Update, context: CallbackContext) -> None:
    logging.info("Command add_expense was triggered")
    keyboard = [
        [InlineKeyboardButton("food", callback_data="category_food"),
         InlineKeyboardButton("health", callback_data="category_health")],
        [InlineKeyboardButton("fun", callback_data="category_fun"),
         InlineKeyboardButton("other", callback_data="category_other")]
    ]
    markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Select the expense category:", reply_markup=markup)


async def button(update: Update, context: CallbackContext) -> None:
    logging.info("Command 'button' was triggered")
    query = update.callback_query
    logging.info(f"QUERY == {query}")
    category = query.data
    await query.answer()
    user_id = query.from_user.id


    await query.message.reply_text(f"Category is '{category}',\n"
                                    "please enter amount: ")
    await ex_storage(update, context)


async def ex_storage(update: Update, context: CallbackContext) -> None:
    logging.info("Command ex_storage was triggered")
    amount = int(update.message.text)
    category = context.user_data.get("category")

    expense = Expenses(amount - amount*2, category)
    Expenses.user_data[category].append(expense)


async def op_list(update: Update, context: CallbackContext) -> None:
    for obj, values in Expenses.user_data.items():
        await update.message.reply_text(f'{obj}, {values}')


async def add_income(update: Update, context: CallbackContext) -> None:
    user_id = update.message.from_user.id


def run():
    app = ApplicationBuilder().token(TOKEN).build()
    logging.info("Application build successfully!")
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("add_expense", add_expense))
    app.add_handler(CommandHandler("add_income", add_income))
    app.add_handler(CommandHandler("close_keyboard", close_keyboard))
    app.add_handler(CommandHandler("list", op_list))
    app.add_handler(CallbackQueryHandler(button, pattern='^category_'))
    app.add_handler(CallbackQueryHandler(button))
    app.run_polling()


if __name__ == "__main__":
    run()

