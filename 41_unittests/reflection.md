# Как правильно готовить юнит-тесты

Тестирование модуля для работы с пользовательскими профилями.

## 1. Тест для проверки хэширования пароля

Свойство: Пароль пользователя хранится в безопасном хэшированном виде.

```python
def test_password_is_hashed(self):
    # Свойство: Пароль хранится в хэшированном виде
    raw_password = "SecurePass123!"
    user = User(email="test@example.com", password=hash_password(raw_password))
    self.assertNotEqual(user.password, raw_password, "Пароль не хэширован")
    self.assertTrue(verify_password(raw_password, user.password), "Хэш не верифицируется")
```

## 2. Тест уникальности email

Свойство: Нельзя зарегистрировать два пользователя с одинаковым email.

```python
def test_unique_email_enforcement(self):
    # Свойство: Невозможно зарегистрироваться с существующим email
    email = "duplicate@example.com"
    User.create(email=email, password=hash_password("Pass1"))
    with self.assertRaises(IntegrityError):
        User.create(email=email, password=hash_password("Pass2"))
```

## 3. Тест обновления профиля

Свойство: Изменения в профиле сохраняются корректно.

```python
def test_profile_update_persistence(self):
    # Свойство: Изменения в профиле сохраняются корректно
    user = User.create(email="update@example.com", password=hash_password("Pass1"))
    new_name = "Updated Name"
    user.update(name=new_name)
    updated_user = User.get(user.id)
    self.assertEqual(updated_user.name, new_name, "Изменения не сохранены")
```

## 4. Тест входа с неверным паролем

Свойство: Система запрещает вход при неверном пароле.

```python
def test_login_with_wrong_password_fails(self):
    # Свойство: Вход с неверным паролем запрещен
    user = User.create(email="login@example.com", password=hash_password("CorrectPass"))
    with self.assertRaises(AuthenticationError):
        user.authenticate("WrongPass")
```

## 5. Тест доступности профиля после регистрации

Свойство: После успешной регистрации пользователь может войти.

```python
def test_successful_registration_grants_access(self):
    # Свойство: После регистрации возможен вход
    email = "new@example.com"
    password = "ValidPass123"
    User.create(email=email, password=hash_password(password))
    authenticated_user = User.authenticate(email, password)
    self.assertIsNotNone(authenticated_user, "Вход после регистрации не удался")
```

## Выводы

Раньше я особо не задумывался, а просто старался написать максимально возможное кол-во юнит-тестов для проверки конкретной реализации.

Для себя я понял, что важно проверять важные свойства системы, а не бесконечные комбинации действий. 
Прежде чем писать код для тестов, нужно четко определить, что делает систему корректной (определить свойства).

В примерах выше каждый тест опирается на явное свойство корректности, а не на случайные детали реализации. Например, тест на хэширование работает для любого пароля, а тест на уникальность email проверяет саму бизнес-логику, а не частный случай.
Если что-то поменяется в коде, выделенные свойства дадут понять, нужно ли менять тесты, или сломалась логика.

Юнит-тесты — это инструмент для гарантии качества через проверку ключевых свойств системы. Нужно развивать умение выделять эти свойства и выбирать подходящие методы тестирования.

Далее важно подумать и выбрать способ тестирования для кажлого свойства системы. Не все тесты должны быть модульными. Для некоторых свойств эффективнее фазз-тесты (генерация случайных данных) или ручные проверки (например, интеграция с внешними сервисами).

Не забываем итоговый алгоритм:
1. Подумать;
2. Написать список свойств, который задаёт корректность некоторой фичи;
3. По каждому свойству:
    - выбрать способ тестирования (модульный, фазз, ручной, обзор кода...)
    - реализовать