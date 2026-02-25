from telegram import (
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    ReplyKeyboardMarkup,
    KeyboardButton
)

def bottom_menu():
    return ReplyKeyboardMarkup(
        [[KeyboardButton("🏠 Главное меню")]],
        resize_keyboard=True,
        is_persistent=True
    )

def main_menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🎮 Играть", callback_data="play")],
        [InlineKeyboardButton("⚔️ Дуэль", callback_data="duel")],
        [InlineKeyboardButton(f"🏆 Рейтинг", callback_data="stats")],
        [InlineKeyboardButton("👥 Друзья", callback_data="friends")],
        [InlineKeyboardButton("📅 Слово дня", callback_data="daily")],
        [InlineKeyboardButton("🌍 Топ 10", callback_data="top")],
    ])

def friends_menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("➕ Добавить друга", callback_data="add_friend")],
        [InlineKeyboardButton("📜 Список друзей", callback_data="friends_list")],
        [InlineKeyboardButton("⚔ Вызвать на дуэль", callback_data="friend_duel")],
        [InlineKeyboardButton("⬅ Назад", callback_data="back_main")]
    ])