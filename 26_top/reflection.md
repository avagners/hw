# Безошибочный код с помощью Typestate-Oriented Programming (TOP)

## Пример 1
До:
```python
class File:
    def __init__(self, filename: str):
        self.filename = filename
        self.is_open = False
        self.mode = None  # 'r' or 'w'

    def open(self, mode: str) -> None:
        if self.is_open:
            raise ValueError("File is already open.")
        self.is_open = True
        self.mode = mode

    def read(self) -> str:
        if not self.is_open or self.mode != 'r':
            raise ValueError("File is not open for reading.")
        return "data from file"

    def close(self) -> None:
        if not self.is_open:
            raise ValueError("File is already closed.")
        self.is_open = False
```

Такой подход требует многочисленных проверок и допускает ситуации, например, попытки вызова `commit` без открытой транзакции.

После:

```python
from abc import ABC


# АТД
class DBState(ABC):
    pass


# Состояние: База данных отключена
class DBDisconnected(DBState):
    def connect(self) -> "DBConnected":
        print("Connecting to database...")
        return DBConnected()


# Состояние: База данных подключена
class DBConnected(DBState):
    def begin_transaction(self) -> "DBTransaction":
        print("Starting transaction...")
        return DBTransaction()

    def disconnect(self) -> DBDisconnected:
        print("Disconnecting from database...")
        return DBDisconnected()


# Состояние: В процессе транзакции
class DBTransaction(DBState):
    def commit(self) -> DBConnected:
        print("Committing transaction...")
        return DBConnected()

    def rollback(self) -> DBConnected:
        print("Rolling back transaction...")
        return DBConnected()


if __name__ == "__main__":
    # Пример использования
    db: DBState = DBDisconnected()                  # Изначальное состояние
    connected_db = db.connect()                     # Переход к состоянию "подключено"
    transaction = connected_db.begin_transaction()  # Начало транзакции
    connected_after_commit = transaction.commit()   # Коммит
    db = connected_after_commit.disconnect() 
```

Преимущества:
- **Изоляция операций:** Невозможно выполнить `commit` без предварительного начала транзакции, так как метод доступен только в состоянии `Transaction`.
- **Чёткий контроль переходов:** Например, нельзя отключиться от базы в состоянии транзакции, не завершив её.
- **Простота использования:** Разработчик опирается на подсказки типов для выбора доступных методов в текущем состоянии.

## Пример 2

До:
```python
class File:
    def __init__(self, filename: str):
        self.filename = filename
        self.is_open = False
        self.mode = None  # 'r' or 'w'

    def open(self, mode: str) -> None:
        if self.is_open:
            raise ValueError("File is already open.")
        self.is_open = True
        self.mode = mode

    def read(self) -> str:
        if not self.is_open or self.mode != 'r':
            raise ValueError("File is not open for reading.")
        return "data from file"

    def close(self) -> None:
        if not self.is_open:
            raise ValueError("File is already closed.")
        self.is_open = False
```
Такой класс требует дополнительной логики проверок и допускает неправильное использование, например, вызов `read` на закрытом файле.

После:
```python
from abc import ABC


# Базовый абстрактный класс для состояния файла
class FileState(ABC):
    pass


# Закрытое состояние файла
class ClosedFile(FileState):
    def __init__(self, filename: str):
        self.filename = filename

    def open(self, mode: str) -> "OpenFile":
        if mode not in ['r', 'w']:
            raise ValueError("Invalid mode. Use 'r' for reading or 'w' for writing.")
        return OpenFile(self.filename, mode)


# Открытое состояние файла
class OpenFile(FileState):
    def __init__(self, filename: str, mode: str):
        self.filename = filename
        self.mode = mode

    def read(self) -> str:
        if self.mode != 'r':
            raise ValueError("File is not open for reading.")
        return "data from file"

    def write(self, data: str) -> None:
        if self.mode != 'w':
            raise ValueError("File is not open for writing.")
        print(f"Writing '{data}' to file.")

    def close(self) -> "ClosedFile":
        return ClosedFile(self.filename)


if __name__ == "__main__":
    # Пример использования
    file = ClosedFile("example.txt")  # Файл начинается в закрытом состоянии
    open_file = file.open('r')        # Переход в состояние "Открыт для чтения"
    data = open_file.read()           # Операция чтения
    closed_file = open_file.close()   # Возврат в состояние "Закрыт"
```

## Пример 3

До:
```python
class Payment:
    def __init__(self, amount: float):
        self.amount = amount
        self.state = "created"
        print(f"Payment initialized in state: {self.state}")

    def authorize(self, card_number: str):
        if self.state != "created":
            raise ValueError("Payment can only be authorized from the 'created' state.")
        if not card_number.isdigit() or len(card_number) != 16:
            raise ValueError("Invalid card number.")
        self.state = "authorized"
        print(f"Payment authorized for amount: {self.amount} using card: {card_number}")

    def complete(self):
        if self.state != "authorized":
            raise ValueError("Payment can only be completed from the 'authorized' state.")
        self.state = "completed"
        print(f"Payment of {self.amount} has been completed successfully.")

    def cancel(self):
        if self.state != "authorized":
            raise ValueError("Payment can only be canceled from the 'authorized' state.")
        self.state = "created"
        print("Payment authorization canceled. Returning to 'created' state.")

    def get_state(self):
        return self.state
```
Такой класс требует дополнительной логики проверок и допускает неправильное использование.

После: 
```python
from abc import ABC

# Базовый абстрактный класс для состояний платежа
class PaymentState(ABC):
    pass

# Состояние: Платеж создан
class PaymentCreated(PaymentState):
    def __init__(self, amount: float):
        self.amount = amount
        print(f"Payment created with amount: {self.amount}")

    def authorize(self, card_number: str) -> "PaymentAuthorized":
        if not card_number.isdigit() or len(card_number) != 16:
            raise ValueError("Invalid card number.")
        print(f"Payment authorized for amount: {self.amount} using card: {card_number}")
        return PaymentAuthorized(self.amount)

# Состояние: Платеж авторизован
class PaymentAuthorized(PaymentState):
    def __init__(self, amount: float):
        self.amount = amount

    def complete(self) -> "PaymentCompleted":
        print(f"Payment of {self.amount} has been completed successfully.")
        return PaymentCompleted(self.amount)

    def cancel(self) -> "PaymentCreated":
        print("Payment authorization canceled. Returning to created state.")
        return PaymentCreated(self.amount)

# Состояние: Платеж завершен
class PaymentCompleted(PaymentState):
    def __init__(self, amount: float):
        self.amount = amount


if __name__ == "__main__":
    # Пример использования
    payment = PaymentCreated(100.0)  # Создаем платеж
    authorized_payment = payment.authorize("1234567812345678")  # Авторизуем
    completed_payment = authorized_payment.complete()           # Завершаем
```

**Преимущества разделения на классы**

1) **Контроль вызовов методов:**
В состоянии `PaymentCreated` нельзя вызвать `complete()` или `cancel()`.  
В состоянии `PaymentCompleted` нельзя выполнить `authorize()` или `cancel()`.

2) **Ясность:**
Переходы между состояниями явно описаны. Например, `authorize` возвращает объект `PaymentAuthorized`, а `complete` возвращает объект `PaymentCompleted`.

3) **Расширяемость:**
Легко добавить новое состояние, например, `PaymentFailed`, если потребуется, с отдельной логикой обработки ошибок.

4) **Безопасность:**
Исключены ситуации, когда вызовы методов нарушают логику состояния (например, завершение неавторизованного платежа).

## Итоги:

Для меня данной урок оказал сильное влияние. Я был крайне удивлен удобству и возможностям, которые дает Typestate-Oriented Programming (TOP).

Всеми привычные универсальные классы имеют следующие ограничения:

- **Слабая типизация:**
Нельзя использовать статический анализатор, чтобы проверить правильный порядок вызова методов.

- **Потенциальная путаница:**
Если метод вызван не в том состоянии, будет выброшено исключение, вместо того чтобы сделать вызов невозможным на уровне интерфейса.

- **Увеличение сложности по мере роста функциональности:**
Если логика состояний и допустимые действия усложнятся, класс станет трудно поддерживать.

В свою очередь разделение `универсального класса` на отдельные классы состояний предоставляет слудующие преимущества:

1. **Повышение строгой типизации:**
Используя отдельные классы для каждого состояния, мы можем строго контролировать доступные методы для каждого состояния.
Это улучшает поддержку инструментов статического анализа и IDE, которые могут предупреждать о некорректных вызовах ещё до запуска программы.

2. **Ясность и явность:**
Разделение на состояния делает интерфейс более очевидным. Пользователи класса могут сразу понять.
Логика программы становится более читаемой, так как состояние файла определяется явно через тип объекта, а не через внутренние флаги (например, `is_open`).

3. **Безопасность и предотвращение ошибок:**
Программа автоматически предотвращает вызовы методов, которые не соответствуют текущему состоянию файла.
Это снижает вероятность ошибок.

4. **Упрощение реализации:**
Каждое состояние имеет чётко определённые обязанности и ответственность. Код становится проще, поскольку не нужно постоянно проверять состояние (if file.is_open:) внутри методов.
Разделение снижает когнитивную нагрузку при поддержке кода.

5. **Расширяемость:**
Добавление новых состояний (например, "Открыт в режиме редактирования" или "Файл заблокирован") становится проще. Мы можем создать новый класс и определить его интерфейс, не затрагивая существующие состояния.
Это также упрощает изменение логики для определённых состояний без риска нарушить работу других.

6. **Принципы объектно-ориентированного проектирования:**  
**Принцип единственной ответственности (SRP):** Каждый класс отвечает только за действия в одном конкретном состоянии.  
**Принцип открытости/закрытости (OCP):** Новые состояния можно добавлять без изменения существующего кода.  
**Принцип подстановки Лисков (LSP):*** Каждый класс-состояние ведёт себя как отдельный, независимый объект.