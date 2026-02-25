from database import add_win, add_loss, get_user
from game_engine import get_random_word, check_word

import time  # ДОБАВИТЬ В НАЧАЛО ФАЙЛА

active_duels = {}

def create_duel(player1, player2):
    word1 = get_random_word()
    word2 = get_random_word()

    match_id = f"{player1}_{player2}"

    active_duels[match_id] = {
        "players": [player1, player2],
        "words": {
            player1: word1,
            player2: word2
        },
        "last_move": {          # 👈 ВОТ ЭТО НОВОЕ
            player1: time.time(),
            player2: time.time()
        },
        "states": {
            player1: {
                "current": [""]*5,
                "tries": 0,
                "history": [],
                "letters": {}
            },
            player2: {
                "current": [""]*5,
                "tries": 0,
                "history": [],
                "letters": {}
            }
        }
    }

    return match_id
def make_move(match_id, player_id, guess):
    duel = active_duels[match_id]
    word = duel["words"][player_id]
    state = duel["states"][player_id]

    result = check_word(guess, word)
    # Обновляем визуал и буквы
    visual = ""
    for i in range(5):
        letter = guess[i].upper()
        if result[i] == "green":
            visual += "🟩" + letter + " "
            state["letters"][guess[i]] = "green"
        elif result[i] == "yellow":
            visual += "🟨" + letter + " "
            if state["letters"].get(guess[i]) != "green":
                state["letters"][guess[i]] = "yellow"
        else:
            visual += "⬛" + letter + " "
            if guess[i] not in state["letters"]:
                state["letters"][guess[i]] = "gray"

    state["history"].append(visual)
    state["tries"] += 1
    state["current"] = [""]*5

    duel["last_move"][player_id] = time.time()

    # Проверка победы
    if guess == word:
        return "win", visual
    if state["tries"] >= 6:
        return "lose", visual

    return "continue", visual
