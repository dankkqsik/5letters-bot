import sqlite3

conn = sqlite3.connect("bot.db", check_same_thread=False)
cursor = conn.cursor()

# --- Таблицы ---
cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY,
    username TEXT,
    elo INTEGER DEFAULT 1000,
    wins INTEGER DEFAULT 0,
    losses INTEGER DEFAULT 0
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS friends (
    user_id INTEGER,
    friend_id INTEGER
)
""")

conn.commit()


# --- Пользователи ---

def add_user(user_id, username):
    cursor.execute("INSERT OR IGNORE INTO users (user_id, username) VALUES (?, ?)", (user_id, username))
    conn.commit()

def get_user(user_id):
    cursor.execute("SELECT * FROM users WHERE user_id=?", (user_id,))
    return cursor.fetchone()

def get_user_by_username(username):
    cursor.execute("SELECT * FROM users WHERE username=?", (username,))
    return cursor.fetchone()

def update_elo(user_id, new_elo):
    cursor.execute("UPDATE users SET elo=? WHERE user_id=?", (new_elo, user_id))
    conn.commit()

def add_win(user_id):
    cursor.execute("UPDATE users SET wins = wins + 1 WHERE user_id=?", (user_id,))
    conn.commit()

def add_loss(user_id):
    cursor.execute("UPDATE users SET losses = losses + 1 WHERE user_id=?", (user_id,))
    conn.commit()

def get_top_players():
    cursor.execute("SELECT username, elo FROM users ORDER BY elo DESC LIMIT 10")
    return cursor.fetchall()


# --- Друзья ---

def add_friend(user_id, friend_id):
    cursor.execute("INSERT INTO friends VALUES (?, ?)", (user_id, friend_id))
    conn.commit()

def get_friends(user_id):
    cursor.execute("SELECT friend_id FROM friends WHERE user_id=?", (user_id,))
    return [row[0] for row in cursor.fetchall()]


# --- Система рейтинга ---

def update_elo_after_match(winner_id, loser_id, k=32):
    winner = get_user(winner_id)
    loser = get_user(loser_id)

    winner_elo = winner[2]
    loser_elo = loser[2]

    expected_win = 1 / (1 + 10 ** ((loser_elo - winner_elo) / 400))
    expected_lose = 1 / (1 + 10 ** ((winner_elo - loser_elo) / 400))

    new_winner_elo = int(winner_elo + k * (1 - expected_win))
    new_loser_elo = int(loser_elo + k * (0 - expected_lose))

    cursor.execute("UPDATE users SET elo=? WHERE user_id=?", (new_winner_elo, winner_id))
    cursor.execute("UPDATE users SET elo=? WHERE user_id=?", (new_loser_elo, loser_id))
    conn.commit()