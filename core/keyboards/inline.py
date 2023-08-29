from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, \
    ReplyKeyboardMarkup, ReplyKeyboardRemove

keyboard = [['/add_expense', '/add_income',],
                  ['/list', '/save'],
                ['/delete_operation', '/stats', '/close_keyboard']]

rep_kb = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
rep_kb.add("/help")

in_kb = InlineKeyboardMarkup(row_width=2)

in_keyboard = {
        'b1': InlineKeyboardButton(text="food", callback_data="food"),
        'b2': InlineKeyboardButton(text="health", callback_data="health"),
        'b3': InlineKeyboardButton(text="fun", callback_data="fun"),
        'b4': InlineKeyboardButton(text="other", callback_data="other")
}

in_kb.add(in_keyboard['b1'], in_keyboard['b2'], in_keyboard['b3'], in_keyboard['b4'])

select_cat = InlineKeyboardMarkup(inline_keyboard=[
    [
        InlineKeyboardButton(
            text="start",
            callback_data=""
        )
    ],
    [
        InlineKeyboardButton(
            text="start",
            callback_data=""
        )
    ],
    [  InlineKeyboardButton(
            text="start",
            callback_data=""
        )
    ],
    [InlineKeyboardButton(
            text="start",
            callback_data=""
        )
    ]
])