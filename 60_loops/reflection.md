# О циклах по умному

## Пример 1: Поиск первого подходящего элемента
Было (императивно, с флагом):

```python
found_element = None
for item in item_list:
    if item.price > 100 and item.is_available:
        found_element = item
        break

if found_element is None:
    raise ValueError("Item not found")
```
Проблемы: Мусорная переменная `found_element`, явный `break`, сложность восприятия.

Стало (декларативно, с `next`):
```python
try:
    found_element = next(item for item in item_list if item.price > 100 and item.is_available)
except StopIteration:
    raise ValueError("Item not found")
```
Выигрыш: Код выражает намерение ("найди первый элемент, удовлетворяющий условию"), а не механизм перебора. Исчезла переменная-флаг.

## Пример 2: Группировка объектов по критерию (grouping)
Было (императивно, со словарём):
```python
groups = {}
for user in users:
    key = user.department
    if key not in groups:
        groups[key] = []
    groups[key].append(user)
```
Проблемы: Мутация состояния внутри цикла, проверка наличия ключа.

Стало (декларативно, с `itertools.groupby`):
```python
from itertools import groupby

# Сначала сортируем
sorted_users = sorted(users, key=lambda u: u.department)
groups = {
    key: list(group)
    for key, group in groupby(sorted_users, key=lambda u: u.department)
}
```
Выигрыш: Нет мутации, чистая парадигма "трансформации данных". Код легче тестировать и рассуждать о нём.

## Пример 3: "Разворачивание" (unfold) конфигурации
Было (императивное построение списка):
```python
def generate_server_ips(base_ip, count):
    ips = []
    base_parts = list(map(int, base_ip.split('.')))
    for i in range(count):
        new_ip_parts = base_parts.copy()
        new_ip_parts[3] += i # Мутируем последний октет
        ips.append(".".join(map(str, new_ip_parts)))
    return ips
```
Проблемы: Мутация внутри цикла, явное управление индексами.

Стало (декларативно, с генератором):
```python
def generate_server_ips(base_ip, count):
    base_parts = list(map(int, base_ip.split('.')))
    for i in range(count):
        yield f"{base_parts[0]}.{base_parts[1]}.{base_parts[2]}.{base_parts[3] + i}"
```
Выигрыш: Ленивые вычисления (не выделяем память под весь список сразу), код чище и выразительнее. Это прямое применение паттерна `unfold`.

## Пример 4: Валидация всех элементов коллекции (all/any)
Было (цикл с флагом):
```python
all_valid = True
for document in documents:
    if not document.validate():
        all_valid = False
        break

if not all_valid:
    handle_invalid_docs()
```
Проблемы: Классический "код с флагом", который можно заменить одной встроенной функцией.

Стало (декларативно, с `all`):

```python
if all(document.validate() for document in documents):
    proceed()
else:
    handle_invalid_docs()
```
Выигрыш: Максимальная выразительность. Сразу понятно, что происходит. Исчезла целая переменная и управляющая логика.

## Пример 5: Преобразование и агрегация (map + reduce)
Было (монолитный цикл):
```python
total_price = 0.0
for order in orders:
    if order.is_completed(): # Фильтр
        for item in order.items: # Вложенный цикл
            total_price += item.price * item.quantity # Агрегация
```
Проблемы: Смешаны фильтрация, трансформация и агрегация. Сложно читать и тестировать.

Стало (декларативно, цепочка преобразований):
```python
from itertools import chain

completed_items = chain.from_iterable(
    order.items for order in orders if order.is_completed()
)
total_price = sum(
    item.price * item.quantity for item in completed_items
)
```
Выигрыш: Код разбит на логические этапы, каждый из которых можно тестировать отдельно. Чётко виден `pipeline` данных: фильтрация заказов -> разворот списков товаров -> агрегация цен. Это композиция абстракций.

## Выводы

Этот материал перевернул мое представление о коде. Я всегда считал циклы чем-то базовым и неизбежным, но теперь вижу: каждый цикл - это упущенная возможность для абстракции.

Теперь для меня циклы воспринимаются чем-то `low level`, что следует использовать в крайнем случае.

Раньше я видел задачи в терминах шагов: "взять элемент", "проверить условие", "добавить в результат". Теперь я пытаюсь сразу определить паттерн:

- Это преобразование? (`map`)
- Фильтрация? (`filter`)
- Агрегация? (`reduce/fold`)
- Генерация? (`unfold`, генераторы)
- Поиск? (`find, next`)

Оказалось, что большенство моих циклов — это комбинации этих паттернов. Писать `sum(x for x in items if x > 0)` не просто "короче" — это правильно, потому что код сразу сообщает о своем намерении.

Мой код полон примеров из статьи:
- Мутирующие состояния внутри циклов (как в примере с группировкой)
- Переменные-флаги (как `all_valid`), которые усложняли логику
- Вложенные циклы с сложной индексацией, где было легко ошибиться

Теперь я понимаю: каждый такой цикл — это место, где можно допустить ошибку. Абстракции типа `itertools.groupby` или `defaultdict` не просто удобны - они исключают целые классы ошибок.

