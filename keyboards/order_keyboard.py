from aiogram.filters.callback_data import CallbackData
from aiogram.types import KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery, ReplyKeyboardMarkup
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder


class TableCallback(CallbackData, prefix="table"):
    action: str
    table_id: str


class EditOrderStatusCallback(CallbackData, prefix="edit_status"):
    status: str
    order_creator_id: int


def get_table_button(amount: int):
    builder = ReplyKeyboardBuilder()

    for i in range(1, amount + 1):
        builder.add(KeyboardButton(text=str(i)))

    builder.adjust(3)

    return builder.as_markup()


def get_count_button():
    builder = ReplyKeyboardBuilder()

    for i in range(0, 9):
        builder.add(KeyboardButton(text=str(i)))

    builder.adjust(3)

    return builder.as_markup()


def get_order_option_button(table_id) -> InlineKeyboardButton:
    buttons = [
        [
            InlineKeyboardButton(
                text="🧹 Очистить стол",
                callback_data=TableCallback(action="clear", table_id=table_id).pack()
            ),
            InlineKeyboardButton(
                text="📝 Редактировать",
                callback_data=TableCallback(action="edit", table_id=table_id).pack()
            )
        ]
    ]
    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)

    return keyboard


def get_order_status_keyboard(order_creator_id: int):
    builder = InlineKeyboardBuilder()
    builder.button(
        text="☑️ Заказ Готов",
        callback_data=EditOrderStatusCallback(status="Готов", order_creator_id=order_creator_id
                                              )
    )
    builder.button(
        text="🚫 Заказ Не готов",
        callback_data=EditOrderStatusCallback(status="Не готов", order_creator_id=order_creator_id
                                              )
    )
    # builder.button(
    #     text="💤 Заказ выполнен",
    #     callback_data=EditOrderStatusCallback(status="Заказ выполнен", order_creator_id=order_creator_id
    #                                           )
    # )

    # Выравниваем кнопки по 4 в ряд, чтобы получилось 4 + 1
    builder.adjust(4)
    return builder.as_markup()


def choose_food_type():
    kb = [
        [
            KeyboardButton(text="save"),
        ],
        [
            KeyboardButton(text="Шашлык 🍢"),
            KeyboardButton(text="Лагман 🍜"),
            KeyboardButton(text="Пиво 🍺"),
        ],
        [
            KeyboardButton(text="Горячие Блюда 🐦‍🔥"),
            KeyboardButton(text="Салаты 🥗"),
            KeyboardButton(text="Блюда с гарниром 🍛"),
        ],
        [

            KeyboardButton(text="Напитки 🥤"),
            KeyboardButton(text="Чипсы"),
            KeyboardButton(text="Закуски 🍟")

        ],

    ]
    keyboard = ReplyKeyboardMarkup(keyboard=kb)

    return keyboard


def choose_shashlik_food():
    kb = [
        [
            KeyboardButton(text="Баранина"),
            KeyboardButton(text="Утка"),
            KeyboardButton(text="Люля"),
        ],
        [

            KeyboardButton(text="Ребра"),
            KeyboardButton(text="Антрекот"),
            KeyboardButton(text="Говядина"),

        ],
        [
            KeyboardButton(text="Крылочка"),
            KeyboardButton(text="Окорачка"),
            KeyboardButton(text="Шампинион"),
            KeyboardButton(text="Овощной"),
        ]

    ]
    keyboard = ReplyKeyboardMarkup(keyboard=kb)

    return keyboard


def choose_lagman_food():
    kb = [
        [
            KeyboardButton(text="Гуйру"),
            KeyboardButton(text="Суйру"),
            KeyboardButton(text="Домашний лагман")
        ],
        [
            KeyboardButton(text="Гуйру цомян"),
            KeyboardButton(text="Дин-дин"),
            KeyboardButton(text="Лагман с ребрами"),
        ],
        [
            KeyboardButton(text="Могру"),
            KeyboardButton(text="Хаухуа"),
            KeyboardButton(text="Мошру"),
            KeyboardButton(text="Фирменный лагман \"Арыс\""),
        ]

    ]
    keyboard = ReplyKeyboardMarkup(keyboard=kb)

    return keyboard


def choose_dishes_food():
    kb = [
        [
            KeyboardButton(text="Красные пельмени"),
            KeyboardButton(text="Мампар")
        ],
        [
            KeyboardButton(text="Суп с мясом"),
            KeyboardButton(text="Пельмень"),
        ],
        [
            KeyboardButton(text="Фри с мясом"),
            KeyboardButton(text="Пюре"),
        ]

    ]
    keyboard = ReplyKeyboardMarkup(keyboard=kb)

    return keyboard


def choose_selad_food():
    kb = [
        [
            KeyboardButton(text="Свежий салат"),
            KeyboardButton(text="Пекинский салат")
        ],
        [
            KeyboardButton(text="Ачучук"),
            KeyboardButton(text="Хрустящий баклажан"),
        ]

    ]
    keyboard = ReplyKeyboardMarkup(keyboard=kb)

    return keyboard


def choose_garnish_food():
    kb = [
        [
            KeyboardButton(text="Мясо по-тайски"),
            KeyboardButton(text="Мушуру сай"),
        ],
        [
            KeyboardButton(text="Могуру сай"),
            KeyboardButton(text="Казан-кебаб"),
        ],
        [
            KeyboardButton(text="Дапанджи"),
        ]

    ]
    keyboard = ReplyKeyboardMarkup(keyboard=kb)

    return keyboard


def choose_garnish_additional():
    kb = [
        [
            KeyboardButton(text="Фри"),
            KeyboardButton(text="Рис"),
        ],
        [
            KeyboardButton(text="Пюре"),
        ]

    ]
    keyboard = ReplyKeyboardMarkup(keyboard=kb)

    return keyboard


def choose_drinks():
    kb = [
        [
            KeyboardButton(text="Coca-Cola 2л"),
            KeyboardButton(text="Coca-Cola 1л"),
            KeyboardButton(text="Coca-Cola 1.5л"),

        ],
        [
            KeyboardButton(text="Fanta 1л"),
            KeyboardButton(text="Fanta 0.5л"),
            KeyboardButton(text="Fanta 1.5л"),
            KeyboardButton(text="Flash"),
        ],
        [
            KeyboardButton(text="Детский сок"),
            KeyboardButton(text="Turan Вода"),
            KeyboardButton(text="Чай"),
        ]

    ]
    keyboard = ReplyKeyboardMarkup(keyboard=kb)

    return keyboard


def choose_snacks():
    kb = [
        [
            KeyboardButton(text="Фри"),
            KeyboardButton(text="Спиральные чипсы"),
        ],
        [
            KeyboardButton(text="Лепешка"),
            KeyboardButton(text="Курт"),
            KeyboardButton(text="Чечел"),
        ]

    ]
    keyboard = ReplyKeyboardMarkup(keyboard=kb)

    return keyboard


def choose_bear():
    kb = [
        [
            KeyboardButton(text="Прага"),
            KeyboardButton(text="Водка 100мл"),
            KeyboardButton(text="Жигули"),
        ],
        [
            KeyboardButton(text="Гусь"),
            KeyboardButton(text="Гусь Экспортное"),
            KeyboardButton(text="Гусь Крепкое"),
        ],
        [
            KeyboardButton(text="Carlsberg"),
            KeyboardButton(text="Holsten Pilsener"),
            KeyboardButton(text="Holsten Light"),
            KeyboardButton(text="Yang"),
        ],
        [
            KeyboardButton(text="Garage Lemon"),
            KeyboardButton(text="Garage Cherry"),
            KeyboardButton(text="Добрый Бобр"),
            KeyboardButton(text="Добрый Крепкое"),
        ]
    ]

    keyboard = ReplyKeyboardMarkup(keyboard=kb)
    return keyboard


def choose_chips():
    kb = [
        [
            KeyboardButton(text="Смак"),
            KeyboardButton(text="Лейс сыр"),
            KeyboardButton(text="Фан"),
        ],
        [
            KeyboardButton(text="Кириешки"),
            KeyboardButton(text="Кириешки лайт"),
            KeyboardButton(text="Кольца"),
        ],
        [
            KeyboardButton(text="Арахис"),
            KeyboardButton(text="Арахис лайт"),
            KeyboardButton(text="Хрустим"),
        ]
    ]

    keyboard = ReplyKeyboardMarkup(keyboard=kb)
    return keyboard