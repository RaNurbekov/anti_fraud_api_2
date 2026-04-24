import redis
import time

print("1. Подключаемся к сверхбыстрой памяти Redis...")
# Подключаемся к нашему Docker-контейнеру
cache = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)

# Имитируем номер карты клиента
card_number = "card_4455_1234"

print("2. Клиент делает первую покупку...")
# Команда INCR увеличивает счетчик на 1. Если счетчика нет - создает его со значением 1.
cache.incr(card_number)
# Ставим таймер: этот счетчик сам удалится из памяти через 60 секунд!
cache.expire(card_number, 60)

# Смотрим, сколько транзакций было за последнюю минуту
count = cache.get(card_number)
print(f"Транзакций по карте за минуту: {count}")

print("\n3. Хакер украл карту и делает серию быстрых списаний!")
cache.incr(card_number)
cache.incr(card_number)
cache.incr(card_number)

count_after_hack = int(cache.get(card_number))
print(f"Транзакций по карте за минуту: {count_after_hack}")

if count_after_hack > 3:
    print("🚨 ВНИМАНИЕ: Слишком много списаний подряд! Блокируем карту!")