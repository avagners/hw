# Переход к иммутабельности

## Пример 1

### Было: 

Передача состояния игрока по ссылке в функцию с возможностью изменения приводит к сложным зависимостям. Например, если состояние здоровья игрока изменяется в нескольких функциях, это усложняет тестирование и понимание программы.

```python
class Player:
    def __init__(self, name: str, health: int):
        self.name = name
        self.health = health


def take_damage(player: Player, damage: int):
    player.health -= damage


player = Player("Hero", 100)
take_damage(player, 10)
print(player.health)  # 90, но это изменение сложно отслеживать
```

### Стало: 

Теперь состояние игрока неизменяемо, а при обновлении создаётся новая копия объекта, что упрощает контроль за состоянием.

```python
from dataclasses import dataclass


@dataclass(frozen=True)
class Player:
    name: str
    health: int


def take_damage(player: Player, damage: int) -> Player:
    return Player(player.name, player.health - damage)


player = Player("Hero", 100)
new_player = take_damage(player, 10)
print(new_player.health)  # 90, исходный объект не изменён
```


## Пример 2

### Было:

Объект пользователя перезаписывается при каждом изменении.

```python
class User:
    def __init__(self, user_id: int, name: str, address: str):
        self.user_id = user_id
        self.name = name
        self.address = address

    def update_address(self, new_address: str):
        self.address = new_address


user = User(1, "Алиса", "ул. Ленина, 26")
user.update_address("ул. Ставропольская, 40")
```

### Стало: 

Неизменяемые объекты, которые создаются при каждом обновлении.

```python
from dataclasses import dataclass


@dataclass(frozen=True)
class User:
    user_id: int
    name: str
    address: str


@dataclass(frozen=True)
class UserChangeLog:
    user_id: int
    name: str
    address: str
    timestamp: str


class UserHistory:
    def __init__(self):
        self.history = []

    def update_user(self, user: User, new_address: str, timestamp: str) -> User:
        new_user = User(user.user_id, user.name, new_address)
        self.history.append(UserChangeLog(new_user.user_id, new_user.name, new_user.address, timestamp))
        return new_user


user = User(1, "Алиса", "ул. Ленина, 26")
history = UserHistory()
user = history.update_user(user, "ул. Ставропольская, 40", "2024-09-17T12:00:00")
user = history.update_user(user, "ул. Первомайская, 5", "2024-09-18T15:00:00")
```

Можно хранить и отслеживать все изменения без необходимости перезаписи объекта.


## Пример 3

### Было:

Изменение статуса заказа напрямую изменяет объект.

```python
class Order:
    def __init__(self, order_id: int, status: str):
        self.order_id = order_id
        self.status = status

    def update_status(self, new_status: str):
        self.status = new_status


order = Order(1, "Created")
order.update_status("Shipped")
order.update_status("Delivered")
```

### Стало: 

Неизменяемые объекты заказа, где каждое изменение создаёт новый заказ с новым статусом, а предыдущие состояния сохраняются.

```python
from dataclasses import dataclass
from typing import List


@dataclass(frozen=True)
class Order:
    order_id: int
    status: str
    timestamp: str


class OrderHistory:
    def __init__(self):
        self.history: List[Order] = []

    def update_order(self, order_id: int, new_status: str, timestamp: str):
        order = Order(order_id, new_status, timestamp)
        self.history.append(order)


history = OrderHistory()
history.update_order(1, "Created", "2024-09-17T12:00:00")
history.update_order(1, "Shipped", "2024-09-18T14:00:00")
history.update_order(1, "Delivered", "2024-09-19T16:00:00")

for order in history.history:
    print(order)
# Order(order_id=1, status='Created', timestamp='2024-09-17T12:00:00')
# Order(order_id=1, status='Shipped', timestamp='2024-09-18T14:00:00')
# Order(order_id=1, status='Delivered', timestamp='2024-09-19T16:00:00')
```

## Выводы:

До этого задания я в основном использовал изменяемые объекты. Это казалось нормальным, но теперь я вижу, как это создаёт скрытые зависимости. Когда объект можно изменить в любой части программы, легко запутаться, где и что меняется.

Когда при изменениях создаётся новый объект, старое состояние сохраняется, и это очень помогает при отладке или откате к предыдущим версиям. Также, тестировать код с иммутабельными объектами проще.

Для себя я понял, что в некоторых случаях лучше отказаться от передачи объектов по ссылке и вместо этого возвращать новый объект. Иммутабельность упрощает управление состоянием и уменьшает зависимость между компонентами системы.