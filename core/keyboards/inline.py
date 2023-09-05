from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, \
    ReplyKeyboardMarkup, ReplyKeyboardRemove, KeyboardButton

keyboard = [['/add_expense', '/add_income',],
                  ['/save', '/load'],
                ['/list', '/close_keyboard'],
            ['/stats day', '/stats week', '/stats month']]

rep_kb = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)




in_kb = InlineKeyboardMarkup(row_width=2)

in_keyboard = {
        'b1': InlineKeyboardButton(text="food", callback_data="food"),
        'b2': InlineKeyboardButton(text="health", callback_data="health"),
        'b3': InlineKeyboardButton(text="fun", callback_data="fun"),
        'b4': InlineKeyboardButton(text="other", callback_data="other")
}


del_button = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton("Delete Operation", callback_data="DELETE OPERATION")]
])

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