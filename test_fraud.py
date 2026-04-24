import pandas as pd
import requests
import json
import time

print("Загружаем базу данных для симуляции...")
df = pd.read_csv('data/raw/creditcard.csv')

# Берем одну нормальную транзакцию и одну 100% мошенническую из истории
normal_tx = df[df['Class'] == 0].drop(columns=['Class']).iloc[0].to_dict()
fraud_tx = df[df['Class'] == 1].drop(columns=['Class']).iloc[0].to_dict()

url = "http://127.0.0.1:8000/scan"

print("\n--- СЦЕНАРИЙ 1: Обычный человек покупает кофе ---")
payload_1 = {"card_id": "card_normal_001", "features": normal_tx}
resp_1 = requests.post(url, json=payload_1).json()
print(json.dumps(resp_1, indent=4, ensure_ascii=False))

print("\n--- СЦЕНАРИЙ 2: Хакер делает хитрый, одиночный перевод ---")
payload_2 = {"card_id": "card_hacked_002", "features": fraud_tx}
resp_2 = requests.post(url, json=payload_2).json()
print(json.dumps(resp_2, indent=4, ensure_ascii=False))

print("\n--- СЦЕНАРИЙ 3: Брутфорс-атака (хакер спамит переводами) ---")
# Хакер пытается списать нормальную транзакцию, но делает это 4 раза подряд!
payload_3 = {"card_id": "card_spammed_003", "features": normal_tx}
for i in range(4):
    print(f"Попытка списания #{i+1}...")
    resp_3 = requests.post(url, json=payload_3).json()
    time.sleep(0.5) # Пауза полсекунды

print("Результат последней попытки:")
print(json.dumps(resp_3, indent=4, ensure_ascii=False))