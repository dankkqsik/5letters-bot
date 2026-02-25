import time
from telegram import (
    Update,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    ReplyKeyboardMarkup,
    KeyboardButton
)
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

from config import TOKEN
from database import get_user, get_top_players, add_win, add_loss, update_elo
from duel_system import create_duel, make_move, active_duels


# =============================
# Глобальные переменные
# =============================

pending_duels = {}
player_matches = {}
duel_timers = {}  # match_id: timestamp


# =============================
# Клавиатуры
# =============================

def main_menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🎮 Играть", callback_data="play")],
        [InlineKeyboardButton("🏆 Моя статистика", callback_data="rating")],
        [InlineKeyboardButton("🌍 Глобальный топ", callback_data="top")]
    ])


def back_button():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("⬅️ Назад", callback_data="menu")]
    ])


def bottom_menu():
    return ReplyKeyboardMarkup(
        [[KeyboardButton("🏠 Главное меню")]],
        resize_keyboard=True,
        is_persistent=True
    )


# =============================
# Команда /start
# =============================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🚀 Добро пожаловать в Word Duel!",
        reply_markup=main_menu()
    )

    await update.message.reply_text(
        "Используй кнопку ниже для возврата:",
        reply_markup=bottom_menu()
    )


# =============================
# Callback обработчик
# =============================

async def callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id
    data = query.data

    if data == "menu":
        await query.edit_message_text(
            "🏠 Главное меню",
            reply_markup=main_menu()
        )
        return

    if data == "rating":
        user = get_user(user_id)

        text = (
            f"🏆 Твоя статистика\n\n"
            f"ELO: {user[2]}\n"
            f"Победы: {user[3]}\n"
            f"Поражения: {user[4]}"
        )

        await query.edit_message_text(
            text,
            reply_markup=back_button()
        )
        return

    if data == "top":
        players = get_top_players()

        text = "🌍 Глобальный рейтинг:\n\n"
        for i, p in enumerate(players, 1):
            text += f"{i}. @{p[0]} — {p[1]} Elo\n"

        await query.edit_message_text(
            text,
            reply_markup=back_button()
        )
        return

    if data.startswith("duel_"):
        opponent_id = int(data.split("_")[1])
        pending_duels[opponent_id] = user_id

        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("✅ Принять", callback_data="accept_duel")]
        ])

        await context.bot.send_message(
            opponent_id,
            "⚔️ Вас вызвали на дуэль!",
            reply_markup=keyboard
        )

        await query.edit_message_text("Приглашение отправлено!")
        return

    if data == "accept_duel":
        if user_id not in pending_duels:
            await query.edit_message_text("❌ Приглашение устарело")
            return

        challenger = pending_duels[user_id]
        match_id = create_duel(challenger, user_id)

        player_matches[challenger] = match_id
        player_matches[user_id] = match_id
        duel_timers[match_id] = time.time()

        await context.bot.send_message(challenger, "⚔️ Дуэль началась!")
        await query.edit_message_text("⚔️ Дуэль началась!")

        del pending_duels[user_id]


# =============================
# Обработка текста (ходы)
# =============================

async def text_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    text = update.message.text.lower()

    if text == "🏠 главное меню":
        await update.message.reply_text(
            "🏠 Главное меню",
            reply_markup=main_menu()
        )
        return

    if user_id not in player_matches:
        return

    match_id = player_matches[user_id]

    status, visual = make_move(match_id, user_id, text)

    await update.message.reply_text(visual)

    opponent = [
        p for p in active_duels[match_id]["players"]
        if p != user_id
    ][0]

    if status == "win":
        add_win(user_id)
        add_loss(opponent)
        update_elo(user_id, opponent)

        await update.message.reply_text("🏆 Победа!")

        cleanup_match(match_id)

    elif status == "lose":
        add_win(opponent)
        add_loss(user_id)
        update_elo(opponent, user_id)

        await update.message.reply_text("💀 Поражение!")

        cleanup_match(match_id)


# =============================
# Очистка дуэли
# =============================

def cleanup_match(match_id):
    players = active_duels[match_id]["players"]

    for p in players:
        if p in player_matches:
            del player_matches[p]

    if match_id in active_duels:
        del active_duels[match_id]

    if match_id in duel_timers:
        del duel_timers[match_id]


# =============================
# Таймер дуэли (30 минут)
# =============================

async def check_timeouts(context: ContextTypes.DEFAULT_TYPE):
    now = time.time()

    for match_id in list(duel_timers.keys()):
        if now - duel_timers[match_id] > 1800:
            players = active_duels[match_id]["players"]

            for p in players:
                await context.bot.send_message(
                    p,
                    "⏳ Дуэль завершена по таймеру!"
                )

            cleanup_match(match_id)


# =============================
# Запуск
# =============================

def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(callback))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, text_handler))

    app.job_queue.run_repeating(check_timeouts, interval=30)

    print("Бот запущен 🚀")
    app.run_polling()


if __name__ == "__main__":
    main()