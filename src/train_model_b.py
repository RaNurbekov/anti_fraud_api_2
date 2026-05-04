import pandas as pd
import lightgbm as lgb
import joblib
import os

print("1. Загружаем данные для Модели Б (Challenger)...")
df = pd.read_csv('data/raw/creditcard.csv')


X = df.drop(columns=['Class'])
y = df['Class']

print("2. Обучаем альтернативную модель...")
# Мы делаем еe "Претендентом : меняем количество деревьев и их глубину"

model_b = lgb.LGBMClassifier (
    n_estimators=150, # Больше дерерьев (было 100)
    learning_rate=0.1, # Делаем ее более "быстрой"
    max_depth=5, # Ограничиваем глубину, чтобы избежать переобучения 
    is_unbalance=True, # Обязательно оставляем балансировку ! 
    random_state=42,
    n_jobs=-1
)

model_b.fit(X, y)

print("3. Сохраняем Модель Б....")
os.makedirs('models', exist_ok=True)

# Сохраняем под новым именем ! 
joblib.dump(model_b, 'models/lgbm_fraud_b.pkl')
print("✅ Претендент (Model B) успешно сохранен и готов к A/B тестированию!")