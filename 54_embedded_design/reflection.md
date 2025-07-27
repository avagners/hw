# Встраиваемое проектирование

## Пример 1: Функция process_order

До:
```python
def process_order(order):
    user = get_user(order.user_id)
    if not user.active:
        raise Exception("Inactive user")
    
    discount = get_discount(user)
    final_price = calculate_price(order.items, discount)
    
    if order.payment_method == "card":
        result = charge_card(user.card_info, final_price)
    else:
        result = charge_wallet(user.wallet_id, final_price)
    
    if result.success:
        order.status = "paid"
        save_order(order)

```
После:
```python
def process_order(order):
    # region Получение пользователя и проверка
    user = get_user(order.user_id)
    if not user.active:
        raise Exception("Inactive user")
    # endregion

    # region Расчёт итоговой стоимости
    discount = get_discount(user)
    final_price = calculate_price(order.items, discount)
    # endregion

    # region Оплата
    if order.payment_method == "card":
        result = charge_card(user.card_info, final_price)
    else:
        result = charge_wallet(user.wallet_id, final_price)
    # endregion

    # region Обновление статуса
    if result.success:
        order.status = "paid"
        save_order(order)
    # endregion
```

## Пример 2: Класс ReportGenerator
До:
```python
class ReportGenerator:
    def generate(self, data):
        validated = self._validate(data)
        transformed = self._transform(validated)
        report = self._render(transformed)
        return report
```
После:
```python
class ReportGenerator:
    def generate(self, data):
        # === Валидация входных данных ===
        validated = self._validate(data)
        
        # === Трансформация данных ===
        transformed = self._transform(validated)
        
        # === Рендер отчета ===
        report = self._render(transformed)
        
        return report
```

## Пример 3: Структура модуля auth.py
До:
```python
def login(): ...
def logout(): ...
def register(): ...
def reset_password(): ...
def verify_email(): ...
def change_password(): ...
```
После:
```python
# ==== Основная авторизация ====
def login(): ...
def logout(): ...
def register(): ...

# ==== Управление аккаунтом ====
def reset_password(): ...
def change_password(): ...
def verify_email(): ...
```

## Выводы

Данная тема для меня оказалась на удивление неожиданной. Принципы встраиваемого проектирования я применял неосознанно в самом начале своего пути. Тогда у меня были файлы с набором функций, которые я разбивал на блоки разделяя их соотвествующими комментариями. Со временем я стал стараться меньше использовать подобные комментарии и дробить длинные методы/функции, большие классы на более мелкие состовляющие. 

После изучения материала я понял несколько важных вещей:

1. Разбивать код - не всегда благо.
Раньше я по инерции старался разбить каждую крупную функцию на множество мелких. Это делало код "чистым" внешне, но при этом логика терялась между слоями абстракции, а параметры приходилось протаскивать повсюду. Теперь я вижу, что иногда проще и эффективнее сгруппировать код внутри одной функции, если смысл остаётся читаемым.

2. Комментарии и структура - это тоже инструмент.
Заголовки-комментарии (вроде # === Оплата ===) для логических блоков внутри функции - это реально помогает быстрее ориентироваться и понимать, что делает код, не отвлекаясь на детали.

3. Код стал подготовленным к рефакторингу.
Благодаря группировке я вижу, какие части кода уже готовы стать самостоятельными методами или модулями, если в будущем логика усложнится. Это как будто я "подсветил" возможные точки масштабирования.

4. Файлы и классы тоже стали проще.
Группировка функций в модуле по задачам (например, "Авторизация", "Управление аккаунтом") сделала структуру файла в разы понятнее. Больше не нужно долго листать и гадать, где какая функция.

5. Я перестал бояться "длинных" функций.
Раньше я автоматически считал функцию из 30 строк плохой. Сейчас понимаю, что главное — смысл и читаемость, а не длина. Иногда цельная функция с правильно оформленными блоками куда понятнее, чем 5 методов по 5 строк.

В целом, это задание научило меня думать о коде как о тексте для чтения, а не просто как о механизме выполнения. Принцип "встраиваемого проектирования" оказался неожиданно простым и мощным инструментом, который я точно буду использовать дальше.