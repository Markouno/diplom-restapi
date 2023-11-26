import random


def create_token(): # Функция генерации токена
    symbols = "abcdefghijklmnopqrstuvwxyz"
    upper_symbols = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    numbers = "1234567890"

    var_array = symbols + upper_symbols + numbers # Строка всех символов
    token = "".join(random.sample(var_array, 16)) # Через join соединяем символы по sample из библиотеки random
    return token
