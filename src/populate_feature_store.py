import pandas as pd
import redis
import json


print("1. Подключаемся к Redis (Feature Store)...")

# Подключаемся к нашей базе данных
cache = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)


print("2. Читаем исторические данные...")
df = pd.read_csv('data/raw/creditcard.csv')


#

#Вырезаем профиль обычного клиента (Убираем Class, Amount and Time - их пришлет касса)
normal_profile = df[df['Class'] == 0].drop(columns=['Class', 'Amount', 'Time']).iloc[0].to_dict()



# Вырезаем профиль хакера
fraud_profile = df[df['Class'] == 1].drop(columns=['Class', 'Amount', 'Time']).iloc[0].to_dict()




print("3. Загружаем профили (V1-V28) в оперативную память...")
# Ключ в Redis будет начинаться со слова "profile:"
cache.set('profile:card_normal_001', json.dumps(normal_profile))
cache.set('profile;card_hacked_002', json.dumps(fraud_profile))

#Проверяем, что все заптсалось 
saved_data = cache.get('profile:card_normal_001')
print(f"\nПример сохраненного профиля из Redis: \n{saved_data[:100]}...")

print("\n✅ Данные успешно загружены в Feature Store!")