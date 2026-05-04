from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import joblib
import pandas as pd
import redis
import json
import random
import os

ml_models = {}
cache = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    global cache
    print("⏳ Загружаю Чемпиона (Модель А) и Претендента (Модель Б)...")
    ml_models["model_a"] = joblib.load('models/lgbm_fraud.pkl')
    ml_models["model_b"] = joblib.load('models/lgbm_fraud_b.pkl')
    
    print("⏳ Подключаюсь к Feature Store (Redis)...")
    redis_url = os.getenv("REDIS_HOST", "localhost")
    cache = redis.Redis(host=redis_url, port=6379, db=0, decode_responses=True)
    
    print("✅ A/B Роутер готов к бою!")
    yield
    ml_models.clear()
    cache.close()

app = FastAPI(title="A/B Anti-Fraud API", lifespan=lifespan)

# Теперь касса присылает ТОЛЬКО номер карты и сумму покупки!
class Transaction(BaseModel):
    card_id: str
    amount: float

@app.post("/scan")
def scan_transaction(tx: Transaction):
    # --- 1. ВЫТАСКИВАЕМ ИСТОРИЮ ИЗ FEATURE STORE ---
    profile_str = cache.get(f"profile:{tx.card_id}")
    if not profile_str:
        raise HTTPException(status_code=404, detail="Профиль клиента не найден в базе!")
        
    # Превращаем строку из Redis обратно в словарь
    features = json.loads(profile_str)
    
    # Склеиваем исторический профиль с текущей транзакцией
    features["Amount"] = tx.amount
    features["Time"] = 0.0 # Модель обучалась с колонкой Time, ставим заглушку
    
    df = pd.DataFrame([features])
    
    # --- 2. A/B ТЕСТИРОВАНИЕ (РОУТЕР) ---
    # Генерируем случайное число от 0 до 1
    if random.random() < 0.20:
        # 20% трафика отдаем новой модели
        active_model = ml_models["model_b"]
        model_name = "Model B (Challenger)"
    else:
        # 80% трафика обрабатывает проверенная модель
        active_model = ml_models["model_a"]
        model_name = "Model A (Champion)"
        
    # --- 3. ПРЕДСКАЗАНИЕ ---
    prob = active_model.predict_proba(df)[:, 1][0]
    
    if prob > 0.50:
        decision = "BLOCK 🚨"
        reason = f"Обнаружен фрод! Решение приняла {model_name}"
    else:
        decision = "APPROVE ✅"
        reason = f"Безопасно. Решение приняла {model_name}"
        
    return {
        "decision": decision,
        "reason": reason,
        "risk_probability": round(float(prob), 4),
        "model_used": model_name
    }