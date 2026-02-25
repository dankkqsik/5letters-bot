import random
from config import WORD_LENGTH, MAX_TRIES

with open("words.txt", encoding="utf-8") as f:
    WORDS = [w.strip() for w in f.readlines() if len(w.strip()) == WORD_LENGTH]

def get_random_word():
    return random.choice(WORDS)

def check_word(guess, word):
    result = ["gray"] * WORD_LENGTH
    word_list = list(word)

    for i in range(WORD_LENGTH):
        if guess[i] == word[i]:
            result[i] = "green"
            word_list[i] = None

    for i in range(WORD_LENGTH):
        if result[i] == "green":
            continue
        if guess[i] in word_list:
            result[i] = "yellow"
            word_list[word_list.index(guess[i])] = None

    return result
