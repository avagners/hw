# Долгосрочное проектирование API

## 1. Сериализация данных

Проблема: Клиенты полагаются на порядок полей или структуру JSON.

До (хрупкий API)
```python
from dataclasses import dataclass

@dataclass
class User:
    id: int
    name: str

# Клиентский код (может сломаться при изменении структуры)
user = User(1, "Alice")
json_data = '{"id": 1, "name": "Alice"}'  # Хардкод порядка полей
```

После (устойчивый API + chaos-тестирование)
```python
from pydantic import BaseModel, Field
from typing import Optional
import random

class User(BaseModel):
    id: int = Field(gt=0)
    name: str
    role: Optional[str] = None  # Новое поле не ломает старых клиентов

# Chaos-режим: меняем порядок полей в тестах
def chaos_serialize(user: User) -> str:
    fields = user.dict()
    if random.choice([True, False]):
        fields["_chaos"] = "test"  # Добавляем мусор
    return json.dumps(fields, indent=None, sort_keys=True)  # Случайный порядок!

# Тест:
user = User(id=1, name="Alice")
chaos_json = chaos_serialize(user)
parsed_user = User.parse_raw(chaos_json)  # Должен работать!
```

Клиенты должны использовать User.parse_raw(), а не ручной парсинг JSON.
Добавление новых полей (role) не ломает обратную совместимость.

## 2. REST API

Проблема: Клиенты зависят от порядка полей, кодов статусов или формата ошибок.

До (ригидный API)
```python
from fastapi import FastAPI

app = FastAPI()

@app.get("/user")
def get_user():
    return {"id": 1, "name": "Alice"}  # Жёсткая структура
```

После (chaos-тестирование + версионирование)
```python
from fastapi import FastAPI, Header
from pydantic import BaseModel
import random

app = FastAPI()

class UserResponse(BaseModel):
    id: int
    name: str

@app.get("/user")
def get_user(chaos: bool = False):
    user = UserResponse(id=1, name="Alice")
    if chaos:
        return {
            "data": user.dict(),
            "_meta": {"chaos": True},  # Добавляем лишние поля
        }
    return user

# Тест:
def test_client_handles_chaos():
    response = client.get("/user?chaos=true")
    assert UserResponse(**response.json()["data"])  # Клиент должен игнорировать _meta
```

Клиенты не должны полагаться на порядок полей или наличие _meta.
Новые поля (например, email) добавляются через Optional.

## 3. RPC / gRPC 

Проблема: Клиенты зависят от порядка полей в .proto или бинарного формата.

До (неявные зависимости)
```protobuf
// user.proto
message User {
  int32 id = 1;
  string name = 2;
}
```

Клиенты могут парсить бинарные данные вручную, полагаясь на тэги полей.

После (chaos-тестирование)

```python
# Генерация "хаотичного" .proto для тестов
message ChaosUser {
  int32 id = 1;
  string _chaos = 999;  # Добавляем поле с высоким тэгом
  string name = 2;
}

# Тест:
user = User(id=1, name="Alice")
chaos_data = ChaosUser(id=1, name="Alice", _chaos="test").SerializeToString()

# Клиент должен корректно десериализовать, игнорируя _chaos
parsed_user = User.FromString(chaos_data)
```

Клиенты используют только официальные методы десериализации.
Добавление новых полей в .proto не ломает старых клиентов.

## Выводы

После разбора темы я осознал несколько ключевых вещей:
- Раньше я думал: «Работает? Значит, ок». Теперь я вижу, как клиенты (внутренние или внешние) могут незаметно завязываться на детали реализации: порядок полей в `JSON`, отсутствие валидации, хардкод структуры данных. Теперь понимаю, когда `API` начнёт меняться, всё посыпется на проде. 
- Обязательное внедрение Chaos-тестирования. Кстати, впервые услышал о данном инструменте. 
- Обязательное использование `Pydantic` и `Dataclasses` вместо голого `dict`. 
- Версионирование — это не просто «v1/», «v2/». Даже внутри одной версии API нужно добавлять новые поля как опциональные, не удалять старые поля, а помечать их `deprecated`, тестировать старых клиентов против новых версий API.

Спасибо за пример с `STRUCT` в Си — он показал мне как можно осознано ломать неявные зависимости.