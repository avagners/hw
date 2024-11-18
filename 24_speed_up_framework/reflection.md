# Ускоряем код фреймворков в 100 раз

Django ORM реализует уровень абстракции над базой данных, превращая запросы в Python-коде в SQL. Основные шаги работы ORM:

**Создание моделей:** Каждая модель в Python представляет собой класс, который Django транслирует в SQL-таблицы. Например, поле `CharField` превращается в колонку типа `VARCHAR` в SQL.  

**Конструктор запросов (QuerySet):** Python-код вида `Model.objects.filter()` конструирует SQL-запросы. Они не выполняются сразу — ORM использует ленивую загрузку.  

**Генерация SQL:** При выполнении запросов Django использует SQL-синтаксис для взаимодействия с базой данных. Пример:

```python
# ORM
User.objects.filter(name='John')
```
```sql
-- Генерируемый SQL
SELECT * FROM user WHERE name = 'John';
```

## Способ обхода ORM

Для обхода ORM используем `django.db.connection`.

## Примеры

### Пример 1. Получение пользователей с ролями
Было:
```python
admins = User.objects.filter(role__name='Admin')
```
**Логика домена:** Найти всех пользователей с ролью "Администратор".  
**Производительность:** ORM делает 2 запроса (один для пользователей, один для ролей), что добавляет накладные расходы.

Стало:
```python
def get_admins():
    with connection.cursor() as cursor:
        cursor.execute("""
        SELECT user.id, user.name, role.name
        FROM user
        JOIN role ON user.role_id = role.id
        WHERE role.name = 'Admin'
        """)
        return cursor.fetchall()
```

**Результат:** Производительность улучшилась в 1.5–2 раза (меньше запросов).

### Пример 2. Агрегация данных
Было:
```python
total_sales = Sale.objects.aggregate(total=Sum('amount'))
```

**Логика домена:** Суммировать все продажи.  
**Производительность:** ORM создаёт дополнительную нагрузку для агрегации данных.
Стало:
```python
def get_total_sales():
    with connection.cursor() as cursor:
        cursor.execute("""
        SELECT SUM(amount) as total
        FROM sale
        """)
        return cursor.fetchone()
```
**Результат:** Ускорение при больших объёмах данных.

### Пример 3. Сложные выборки с фильтрацией
Было:
```python
recent_orders = Order.objects.filter(date__gte='2024-01-01').select_related('customer')
```

**Логика домена:** Выборка заказов за текущий год с данными о клиентах.  
**Производительность:** ORM может создать избыточные JOIN-ы.

Стало:
```python
def get_recent_orders():
    with connection.cursor() as cursor:
        cursor.execute("""
        SELECT order.id, order.date, customer.name
        FROM order
        JOIN customer ON order.customer_id = customer.id
        WHERE order.date >= '2024-01-01'
        """)
        return cursor.fetchall()
```
**Результат:** Уменьшение нагрузки на процессор и базу данных.


## Итог

Рефакторинг с использованием SQL вместо ORM даёт:
- Прямой контроль над запросами.
- Улучшение производительности, особенно при сложных выборках.