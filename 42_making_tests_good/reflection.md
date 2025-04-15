# Делаем тесты хорошимиДелаем тесты хорошими

## Пример 1


**Абстрактный эффект:**  
После добавления пользователь должен быть доступен в репозитории.

До:
```python
def test_user_repository_adds_user():
    repo = UserRepository()
    user = User("Alice")
    repo.add(user)

    assert user in repo._users_list  # Завязка на внутреннюю структуру!
```
Тест привязан к приватному полю `_users_list`.

После:
```python
def test_user_is_accessible_after_add():
    repo = UserRepository()
    user = User("Alice")
    repo.add(user)

    assert repo.find_by_name("Alice") == user
```
Теперь проверяется поведение, а не конкретное хранилище (_users_list).
Моки не нужны, потому что проверяем чистый интерфейс.

## Пример 2

**Абстрактный эффект:**  
API возвращает данные о пользователе с ID и именем.

До:
```python
def test_api_returns_correct_json_structure():
    api = ApiClient()
    response = api.get_user(42)

    assert response == '{"id": 42,"name": "Alice"}'  # Плохо: жёстко фиксирует формат.
```
Тест проверяет формат сериализации, а не сам факт возвращения корректной информации.

После:
```python
def test_api_returns_correct_user_data():
    api = ApiClient()
    response = json.loads(api.get_user(42))

    assert response["id"] == 42
    assert "name" in response
```

Эффект теперь проверяется явно.
Моки не использованы, потому что API-ответ проверяется на уровне контракта.

## Пример 3

**Абстрактный эффект:**  
Пользователь должен быть сохранён в системе.

До:
```python
def test_user_saved_to_database():
    service = UserService()
    user = User("Bob")
    service.create_user(user)

    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE name='Bob'")
    assert cursor.fetchone() is not None
```

Тест проверяет, что конкретная таблица `users` содержит запись.
Если `storage` сменится с `SQLite` на `Redis` или `Postgres` — тест сломается.

После:
```python
from unittest.mock import MagicMock

def test_user_saved_via_repository():
    mock_repo = MagicMock()
    service = UserService(repository=mock_repo)
    user = User("Bob")

    service.create_user(user)

    mock_repo.save.assert_called_once_with(user)
```

- Мы не лезем в базу;
- Не зависим от формата хранения (SQL, Redis, S3, JSON... неважно!);
- тест проверяет именно то, что метод `create_user()` вызывает `repo.add(user)`.

Моки используются, потому что тест проверяет не то, как именно пользователь хранится, а то, что произошло взаимодействие между бизнес-логикой (`UserService`) и хранилищем (`UserRepository`).

## Пример 4

**Абстрактный эффект:**  
Событие логирования произошло.

До:
```python
def test_logger_writes_specific_message():
    logger = Logger()
    logger.log("User created: Alice")

    with open("app.log") as f:
        logs = f.read()

    assert "User created: Alice" in logs  # Завязка на файл и формат
```
Проверяем побочный эффект слишком низкого уровня (файл).

После:
```python
from unittest.mock import MagicMock

def test_user_creation_triggers_logging():
    logger = MagicMock()
    service = UserService(logger)
    user = User("Alice")
    service.create_user(user)

    logger.log.assert_called_with("User created: Alice")
```

Проверяется абстрактный эффект: лог был вызван с нужным сообщением, а не где он сохранился.
Моки используются, потому что проверяется событие, а не файл.

## Пример 5

**Абстрактный эффект:**  
После регистрации отправлено приветственное письмо.

```python
def test_email_sent_on_registration():
    service = UserService()
    user = User("Alice")
    service.register(user)

    with open("/var/mail/outbox") as f:
        emails = f.read()

    assert "Welcome Alice" in emails  # Жёстко завязано на реализацию!
```

Тест проверяет факт наличия письма в конкретной файловой очереди — завязка на реализацию.

После:
```python
from unittest.mock import MagicMock

def test_email_notification_triggered_on_registration():
    mailer = MagicMock()
    service = UserService(mailer)
    user = User("Alice")
    service.register(user)

    mailer.send_email.assert_called_once()
```

Проверяем именно абстрактный эффект: функция отправки была вызвана.
Моки обязательно используются. Без моков тест бы зависел от почтового сервера.

## Выводы

Самое важное - тест должен проверять абстрактные эффекты.
Например: "пользователь зарегистрирован", "письмо отправлено", "объект доступен" — а не "в какой таблице это лежит" или "в каком файле записано".

Моки — важный инструмент для изоляции и проверки именно этих абстрактных эффектов, особенно когда код взаимодействует с внешними системами.
В чём сила моков:
- Быстро — не ждём настоящих сетевых операций.
- Надёжно — тест проверяет не "работает ли SMTP-сервер", а "вызывается ли отправка письма".
- Чисто — тест фокусируется на бизнес-логике, а не на инфраструктуре.

Тест с моками не доказывает, что письмо реально ушло.
Тест доказывает: "Код попытался отправить письмо".
А значит — абстрактный эффект "письмо отправлено" реализован.

Тесты = доказательства корректности фичи, а не "галочка для покрытия". Нужно всегда помнить про проверку ключевых свойств системы.

И не забываем итоговый алгоритм тестирования:
1. Подумать;
2. Написать список свойств, который задаёт корректность некоторой фичи;
3. По каждому свойству:
    - выбрать способ тестирования (модульный, фазз, ручной, обзор кода...)
    - реализовать
