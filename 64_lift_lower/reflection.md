# Что такое абстрация-2

## Пример 1: Валидация email

Конкретный мир: строки, регулярные выражения, проверки
Абстрактный мир: понятия "валидный/невалидный email"

```python
from dataclasses import dataclass
from typing import Callable, Tuple

# Конкретное представление
RawEmail = str

# Абстрактное представление
@dataclass(frozen=True)
class ValidatedEmail:
    value: str
    
    def __post_init__(self):
        if "@" not in self.value or "." not in self.value.split("@")[-1]:
            raise ValueError(f"Invalid email: {self.value}")

# Абстракция: отображение между конкретным и абстрактным
def lift_email(raw: RawEmail) -> ValidatedEmail:
    """Поднимаем сырую строку в доменный тип"""
    return ValidatedEmail(raw.strip().lower())

def lower_email(validated: ValidatedEmail) -> RawEmail:
    """Принижаем доменный тип обратно к строке"""
    return validated.value

# Использование абстракции
def send_notification(email: RawEmail, message: str) -> bool:
    try:
        # LIFT: поднимаем в абстрактный домен
        validated = lift_email(email)
        
        # Работаем в абстрактном мире (гарантированно валидные данные)
        print(f"Sending to {validated.value}: {message}")
        
        # LOWER: принижаем обратно для конкретной операции
        actual_email = lower_email(validated)
        # ... реальная отправка через SMTP
        
        return True
    except ValueError:
        return False

# Теперь мы можем быть АБСОЛЮТНО ТОЧНЫ в абстрактном мире:
# Если у нас есть ValidatedEmail - он гарантированно валиден
```

## Пример 2: Обработка JSON

Конкретный мир: словари, списки, строки JSON  
Абстрактный мир: типизированные модели данных

```python
from typing import Any, Dict, List
from datetime import datetime

# Конкретное представление
RawJSON = Dict[str, Any]

# Абстрактное представление
@dataclass(frozen=True)
class User:
    id: int
    name: str
    email: ValidatedEmail  # Композиция абстракций!
    created_at: datetime

# Абстракция lift/lower для JSON ↔ Domain Model
def lift_user_from_json(raw: RawJSON) -> User:
    """Поднимаем сырой JSON в доменную модель"""
    try:
        return User(
            id=int(raw["id"]),
            name=str(raw["name"]).strip(),
            email=lift_email(raw["email"]),  # Используем другую абстракцию!
            created_at=datetime.fromisoformat(raw["created_at"].replace('Z', '+00:00'))
        )
    except (KeyError, ValueError, TypeError) as e:
        raise ValueError(f"Invalid user data: {e}")

def lower_user_to_json(user: User) -> RawJSON:
    """Принижаем доменную модель обратно к JSON"""
    return {
        "id": user.id,
        "name": user.name,
        "email": lower_email(user.email),
        "created_at": user.created_at.isoformat()
    }

# Операции в абстрактном мире
def is_user_active(user: User, threshold_days: int = 30) -> bool:
    """Проверка активности пользователя"""
    days_since_creation = (datetime.now() - user.created_at).days
    return days_since_creation <= threshold_days

# Использование
raw_data = {
    "id": "123",
    "name": "  John Doe  ",
    "email": "JOHN@EXAMPLE.COM",
    "created_at": "2024-01-15T10:30:00Z"
}

# LIFT: поднимаем в абстрактный мир
try:
    user = lift_user_from_json(raw_data)
    # Теперь мы можем быть АБСОЛЮТНО ТОЧНЫ:
    # user гарантированно имеет правильные типы и валидные данные
    
    if is_user_active(user):
        print(f"User {user.name} is active")
    
    # LOWER: принижаем для ответа API
    response_data = lower_user_to_json(user)
    
except ValueError as e:
    print(f"Validation error: {e}")
```

## Пример 3: State machine

Конкретный мир: флаги, условия, мутабельное состояние  
Абстрактный мир: детерминированный конечный автомат

```python
from enum import Enum
from typing import Callable, TypeVar

# Конкретное представление
RawState = str
RawEvent = str

# Абстрактное представление
class OrderStatus(Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed" 
    SHIPPED = "shipped"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"

class OrderEvent(Enum):
    CONFIRM = "confirm"
    SHIP = "ship"
    DELIVER = "deliver"
    CANCEL = "cancel"

# Абстракция lift/lower
def lift_status(raw: RawState) -> OrderStatus:
    """Поднимаем строку в типизированный статус"""
    try:
        return OrderStatus(raw.lower())
    except ValueError:
        raise ValueError(f"Invalid order status: {raw}")

def lower_status(status: OrderStatus) -> RawState:
    """Принижаем статус обратно к строке"""
    return status.value

# Детерминированные переходы в абстрактном мире
TRANSITIONS = {
    OrderStatus.PENDING: [OrderEvent.CONFIRM, OrderEvent.CANCEL],
    OrderStatus.CONFIRMED: [OrderEvent.SHIP, OrderEvent.CANCEL],
    OrderStatus.SHIPPED: [OrderEvent.DELIVER],
    OrderStatus.DELIVERED: [],
    OrderStatus.CANCELLED: [],
}

NEXT_STATE = {
    (OrderStatus.PENDING, OrderEvent.CONFIRM): OrderStatus.CONFIRMED,
    (OrderStatus.PENDING, OrderEvent.CANCEL): OrderStatus.CANCELLED,
    (OrderStatus.CONFIRMED, OrderEvent.SHIP): OrderStatus.SHIPPED,
    (OrderStatus.CONFIRMED, OrderEvent.CANCEL): OrderStatus.CANCELLED,
    (OrderStatus.SHIPPED, OrderEvent.DELIVER): OrderStatus.DELIVERED,
}

def can_transition(current: OrderStatus, event: OrderEvent) -> bool:
    """Можем ли выполнить переход (абстрактная логика)"""
    return event in TRANSITIONS[current]

def transition(current: OrderStatus, event: OrderEvent) -> OrderStatus:
    """Выполняем переход (детерминированно!)"""
    if not can_transition(current, event):
        raise ValueError(f"Cannot {event.value} from {current.value}")
    return NEXT_STATE[(current, event)]

# Использование
def process_order_event(current_state: RawState, event: RawEvent) -> RawState:
    """Конкретная функция обработки"""
    # LIFT: поднимаем в абстрактный автомат
    current_status = lift_status(current_state)
    order_event = OrderEvent(event.lower())
    
    # Работаем в абстрактном мире (гарантированно корректные переходы)
    if can_transition(current_status, order_event):
        new_status = transition(current_status, order_event)
        # LOWER: принижаем обратно для хранения
        return lower_status(new_status)
    else:
        raise ValueError(f"Invalid transition")
```

## Выводы

Раньше я думал, что абстракция - это просто "скрыть сложность" или "сделать интерфейс попроще":

- Абстракция = интерфейсы, классы, функции
- Хорошая абстракция = простой API

Теперь я понимаю:
- Абстракция - это мост между реальностью и идеалом
- Хорошая абстракция создает новый семантический уровень, где можно рассуждать абсолютно точно

Концепция "поднять/принизить" показала мне, как именно работать с абстракциями на практике:

Lift - поднимаем сырые данные в идеальный мир, где:
- Все типы гарантированно корректны
- Все инварианты соблюдены
- Можно рассуждать детерминированно

Lower - возвращаемся в реальный мир для выполнения конкретных операций.

Хорошие абстракции можно комбинировать как Lego. Каждая абстракция приносит свои гарантии в композицию.

Это меняет подход к проектированию.
Раньше я начинал с кода: "какие классы мне нужны?"
Теперь я начинаю с вопросов:
- Какой "грязный" мир я хочу абстрагировать? (сырые строки, JSON, флаги)
- В какой "чистый" мир я хочу его отобразить? (типизированные доменные модели)
- Какие операции должны быть абсолютно точными в чистом мире?
- Как обеспечить soundness при преобразованиях?

Что я буду делать:
- Сначала проектировать отображения, а потом реализацию
- Явно разделять lift/lower операции в коде
- Создавать "идеальные миры" для критически важной логики
- Тестировать не просто код, а корректность отображений между мирами
- Искать места, где можно быть "абсолютно точным" через правильные абстракции

Главный вывод:  
Хорошая абстракция - это не про "удобный API", а про создание нового уровня реальности, где правила ясны, инварианты гарантированы, а рассуждения абсолютно точны.

Теперь, когда я пишу `ValidatedEmail`, я понимаю, что создаю не просто класс, а целый мир, где не существует невалидных `email`.
