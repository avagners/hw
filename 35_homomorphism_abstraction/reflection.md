# Обобщаем проектные абстракции

## Примеры иерархий, которые можно сократить.

### Пример 1

Классы для работы с платежами (`Payment` -> `CreditCardPayment`, `PayPalPayment`, `CryptoPayment`)
Во многих системах платежей создают иерархию с базовым классом `Payment`, но на практике у разных платёжных систем совершенно разные `API`. Например:

`CreditCardPayment` требует обработки номера карты и `CVV`.
`PayPalPayment` работает через токены авторизации.
`CryptoPayment` использует блокчейн-транзакции.

Лучше сделать отдельные классы без общего родителя и реализовать общий интерфейс `ProcessablePayment`.

### Пример 2

Файловая система в операционной системе (`FileSystemObject` -> `File`, `Directory`)
В некоторых ОС (или на уровне библиотек) можно встретить общий класс `FileSystemObject`, от которого наследуются `File` и `Directory`. Но проблема в том, что файл и папка имеют мало общего:
- У файла есть содержимое и размер.
- У папки — список вложенных элементов.

Вместо жёсткого наследования можно использовать интерфейс `FileSystemItem` и делать композицию (например, `Directory` может просто содержать список `FileSystemItem`).

### Пример 3

Классы для обработки логов (`Logger` -> `FileLogger`, `ConsoleLogger`, `DatabaseLogger`)
Вместо наследования лучше использовать стратегию (`ILoggingStrategy`), где каждый логгер — это отдельная реализация интерфейса, а не жёсткая иерархия.

## Расширение подхода через `interface dispatch`

В `Python` подход, аналогичный `interface dispatch`, можно реализовать с помощью:
- Абстрактных базовых классов (`ABC`) для явного определения интерфейсов.
- Протоколов (начиная с `Python 3.8`) для неявного определения интерфейсов.
- Утиной типизации для гибкого определения поведения объектов.

Этот подход позволяет отказаться от жёсткой иерархии классов и сделать код более модульным, гибким и легко расширяемым.

### Пример 1

```python
from abc import ABC, abstractmethod

# Абстрактные интерфейсы
class Renderable(ABC):
    @abstractmethod
    def render(self):
        pass

class Movable(ABC):
    @abstractmethod
    def move(self):
        pass

class Attacker(ABC):
    @abstractmethod
    def attack(self):
        pass

class Collectible(ABC):
    @abstractmethod
    def collect(self):
        pass

# Классы, реализующие интерфейсы
class Player(Renderable, Movable, Attacker):
    def render(self):
        print("Player is rendering")

    def move(self):
        print("Player is moving")

    def attack(self):
        print("Player is attacking")

class Enemy(Renderable, Movable, Attacker):
    def render(self):
        print("Enemy is rendering")

    def move(self):
        print("Enemy is moving")

    def attack(self):
        print("Enemy is attacking")

class Weapon(Renderable, Collectible):
    def render(self):
        print("Weapon is rendering")

    def collect(self):
        print("Weapon is collected")

class Potion(Renderable, Collectible):
    def render(self):
        print("Potion is rendering")

    def collect(self):
        print("Potion is collected")
```

Теперь классы `Player`, `Enemy`, `Weapon` и `Potion` реализуют только те интерфейсы, которые им нужны. Если в будущем появится новый объект, например, `MovingTreasure`, он может реализовать интерфейсы `Movable` и `Collectible`:

```python
class MovingTreasure(Movable, Collectible):
    def move(self):
        print("MovingTreasure is moving")

    def collect(self):
        print("MovingTreasure is collected")
```

### Пример 2

Начиная с `Python 3.8`, можно использовать протоколы (из модуля `typing`), чтобы определить интерфейсы. Протоколы не требуют явного наследования, они проверяют наличие методов во время выполнения.

```python
from typing import Protocol

# Определение протоколов
class Drivable(Protocol):
    def drive(self):
        pass

class PassengerTransport(Protocol):
    def carry_passengers(self):
        pass

class Parkable(Protocol):
    def park(self):
        pass

# Классы, реализующие протоколы
class Sedan:
    def drive(self):
        print("Sedan is driving")

    def carry_passengers(self):
        print("Sedan is carrying passengers")

    def park(self):
        print("Sedan is parked")

class SUV:
    def drive(self):
        print("SUV is driving")

    def carry_passengers(self):
        print("SUV is carrying passengers")

    def park(self):
        print("SUV is parked")

class MountainBike:
    def drive(self):
        print("MountainBike is driving")

class RoadBike:
    def drive(self):
        print("RoadBike is driving")
```
Теперь классы `Sedan`, `SUV`, `MountainBike` и `RoadBike` реализуют только те протоколы, которые им нужны.

### Пример 3

В `Python` можно использовать `утиную типизацию`, чтобы определить, что объект реализует определённое поведение, без необходимости явного наследования от интерфейсов.

```python
# Функции, которые ожидают определённое поведение
def make_sound(sound_maker):
    sound_maker.make_sound()

def fly(flyable):
    flyable.fly()

def swim(swimmable):
    swimmable.swim()


# Классы, реализующие поведение
class Dog:
    def make_sound(self):
        print("Dog is barking")

    def swim(self):
        print("Dog is swimming")

class Cat:
    def make_sound(self):
        print("Cat is meowing")

class Eagle:
    def make_sound(self):
        print("Eagle is screeching")

    def fly(self):
        print("Eagle is flying")

class Sparrow:
    def make_sound(self):
        print("Sparrow is chirping")

    def fly(self):
        print("Sparrow is flying")

# Теперь можно использовать эти классы с функциями, которые ожидают определённое поведение
dog = Dog()
make_sound(dog)  # Dog is barking
swim(dog)        # Dog is swimming

eagle = Eagle()
make_sound(eagle)  # Eagle is screeching
fly(eagle)         # Eagle is flying
```

## Заключение

В ходе занятия пересмотрел иерархию классов, выявив случаи, где можно отказаться от промежуточных абстрактных классов, тем самым снизив когнитивную нагрузку. Далее заменил строгую иерархию на автономные интерфейсы, которые могут реализовываться независимыми классами. Такой подход сделал систему более гибкой, легко расширяемой и удобной для тестирования.

Такой принцип особенно полезен, когда требуется добавлять новые виды сущностей или изменять логику работы старых, не затрагивая существующий код. Это хорошо сочетается с чистой архитектурой, где чёткое разделение интерфейсов помогает снизить связанность модулей и упростить поддержку системы.

В результате мы не только упростили иерархию классов, но и увидели, как композиция, интерфейсы и минимизация связей делают код более масштабируемым и понятным.

Понял, что жёсткие иерархии — зло, а интерфейсы и композиция дают свободу.