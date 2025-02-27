# Справляемся с краевыми случаями

## Пример 1 

Бот принимает заказы, и пользователи одновременно жмут "Подтвердить". Если обработка не атомарная, несколько обновлений могут перезаписать друг друга, теряя данные.

Использовал механизм транзакций в базе данных. Например, в PostgreSQL:

```python
from sqlalchemy.exc import IntegrityError

def confirm_order(user_id, order_id):
    with session.begin():  # транзакция
        order = session.query(Order).filter_by(id=order_id, user_id=user_id).with_for_update().first()
        if not order or order.status != "pending":
            return "Ошибка: заказ уже обработан"
        order.status = "confirmed"
        session.commit()
```
- `with_for_update()` блокирует строку в БД, предотвращая гонки.
- `session.begin()` гарантирует атомарность.

## Пример 2
Бот отправляет сообщение, но запрос зависает или падает с 502 Bad Gateway. Простая отправка через requests.post() приводит к зависанию бота.

Как решено:
Асинхронные запросы + ретраи с экспоненциальной задержкой.

```python
import asyncio
import aiohttp

async def send_message(chat_id, text, retries=5):
    url = f"https://api.telegram.org/bot<TOKEN>/sendMessage"
    params = {"chat_id": chat_id, "text": text}
    
    for attempt in range(retries):
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=params, timeout=5) as resp:
                    if resp.status == 200:
                        return await resp.json()
                    else:
                        print(f"Ошибка {resp.status}, попытка {attempt + 1}")
        except Exception as e:
            print(f"Ошибка: {e}, попытка {attempt + 1}")
        
        await asyncio.sleep(2 ** attempt)  # экспоненциальная задержка
```
- Бот не зависает на одном запросе.  
- Ретраи спасают от временных проблем сети.

## Пример 3
Пользователь отправляет в бот необычные символы (например, `Zero Width Space \u200B` или суррогатные пары эмодзи), и парсинг строки падает.

Как решено:
Нормализация Unicode + защита от краша.

```python
import unicodedata

def safe_text(text):
    try:
        return unicodedata.normalize("NFKC", text)  # нормализация
    except Exception:
        return "Ошибка: неподдерживаемые символы"
```
- NFKC нормализует сложные символы (например, заменяет ½ на 1/2).
- Бот не падает на неожиданных символах.


## Пример 3
Бот запрашивает у пользователя несколько шагов (например, ввод `e-mail` → подтверждение). После перезапуска память очищается, и бот "забывает" пользователей.

Как решено:
Использовал Redis как хранилище состояний.

```python
import redis

r = redis.Redis(host="localhost", port=6379, decode_responses=True)

def set_user_state(user_id, state):
    r.setex(f"user:{user_id}:state", 3600, state)  # TTL 1 час

def get_user_state(user_id):
    return r.get(f"user:{user_id}:state") or "start"
```
- Redis переживает рестарт бота.
- TTL предотвращает "засорение" старыми данными.

## После прочтения материала

Прочитав материал, я вывел для себя такое важное определение как `"отравление проекта краевыми случаями"` и пришел к следующим выводам:

1) Разделять основную логику и исключения.
2) Использовать абстракции с осторожностью.
3) Внедрять раннюю валидацию данных.
4) Тестировать и изолировать краевые случаи.
5) Коммуницировать с заказчиком, чтобы минимизировать ненужные сложности.

Главное — не позволять краевым случаям "отравлять" проект, сохраняя баланс между гибкостью и простотой.