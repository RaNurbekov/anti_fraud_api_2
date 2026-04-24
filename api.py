
import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from pydantic import BaseModel
import joblib
import pandas as pd
import redis

ml_models = {}
cache = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    global cache
    print("⏳ Загружаю ML-мозг Стража...")
    ml_models["lgbm"] = joblib.load('models/lgbm_fraud.pkl')
    
    print("⏳ Подключаюсь к оперативной памяти Redis...")
      # --- ИЗМЕНЕННЫЙ БЛОК ---
    # Читаем адрес из переменных окружения. Если его нет, берем localhost.
    redis_url = os.getenv("REDIS_HOST", "localhost")
    cache = redis.Redis(host=redis_url, port=6379, db=0, decode_responses=True)
    # ---
    
    print("✅ Кибер-полиция готова к бою!")
    yield
    ml_models.clear()
    cache.close()

app = FastAPI(title="Anti-Fraud API", lifespan=lifespan)

# Ждем от кассового аппарата номер карты и признаки
class Transaction(BaseModel):
    card_id: str
    features: dict

@app.post("/scan")
def scan_transaction(tx: Transaction):
    # 1. ПЕРВЫЙ СЛОЙ ЗАЩИТЫ: Проверка скорости (Velocity) через Redis
    tx_count = cache.incr(tx.card_id)
    
    # Если это первая транзакция, ставим таймер очистки памяти - 60 секунд
    if tx_count == 1:
        cache.expire(tx.card_id, 60)
        
    # Правило: больше 3 транзакций в минуту = 100% ФРОД
    if tx_count > 3:
        return {
            "decision": "BLOCK 🚨", 
            "reason": "Сработала защита Redis: Слишком частые списания!",
            "risk_probability": 1.0
        }
        
    # 2. ВТОРОЙ СЛОЙ ЗАЩИТЫ: Искусственный Интеллект (LightGBM)
    df = pd.DataFrame([tx.features])
    
    # Модель предсказывает вероятность мошенничества
    prob = ml_models["lgbm"].predict_proba(df)[:, 1][0]
    
    # Если модель уверена больше чем на 50% - блокируем
    if prob > 0.50:
        decision = "BLOCK 🚨"
        reason = "ML-модель распознала паттерн хакера"
    else:
        decision = "APPROVE ✅"
        reason = "Транзакция выглядит безопасной"
        
    return {
        "decision": decision,
        "reason": reason,
        "risk_probability": round(float(prob), 4)
    }