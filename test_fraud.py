import requests
import json

url = "http://127.0.0.1:8000/scan"

print("--- ТЕСТ 1: Обычная покупка кофе (Нормальный клиент) ---")
payload_1 = {"card_id": "card_normal_001", "amount": 4.50}
resp_1 = requests.post(url, json=payload_1)
print(json.dumps(resp_1.json(), indent=4, ensure_ascii=False))


print("\n--- ТЕСТ 2: Хакерская транзакция (Скомпрометированная карта) ---")
# Хакер проверяет карту (списывает 0.00)
payload_2 = {"card_id": "card_hacked_002", "amount": 0.00}

print("\n--- ТЕСТ 3: Проверка A/B Роутера (10 транзакций) ---")
# Спамим запросами, чтобы увидеть, как трафик делится между Моделями А и Б
for i in range(1, 11):
    resp = requests.post(url, json=payload_1).json()
    model = resp.get("model_used", "Unknown")
    print(f"Транзакция #{i:02d} обработана: {model}")