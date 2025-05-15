# Избавляемся от условных инструкций

## Пример 1. Замена if на полиморфизм

До:
```python
def draw_shape(shape):
    if shape.type == "circle":
        draw_circle(shape)
    elif shape.type == "square":
        draw_square(shape)
```

После:
```python
class Shape:
    def draw(self): pass

class Circle(Shape):
    def draw(self): draw_circle(self)

class Square(Shape):
    def draw(self): draw_square(self)

def draw_shape(shape: Shape):
    shape.draw()
```

Приём: Полиморфизм.  
Комментарий: Убрали необходимость проверки типа, делегируя поведение объектам.  

## Пример 2. Null Object вместо проверки на None

До:
```python
def get_discount(user):
    if user is None:
        return 0
    return user.get_discount()
```

После:
```python
class NullUser:
    def get_discount(self): return 0

user = user or NullUser()
discount = user.get_discount()
```

Приём: Null Object Pattern  
Комментарий: Устранили условие, подменяя None на объект с предсказуемым поведением.  

## Пример 3. Удаление условия через map (таблица стратегий)

До:
```python
def handle_event(event_type):
    if event_type == "click":
        do_click()
    elif event_type == "hover":
        do_hover()
```

После:
```python
handlers = {
    "click": do_click,
    "hover": do_hover
}

handlers[event_type]()
```

Приём: Таблица стратегий  
Комментарий: Условие заменено диспетчеризацией по словарю.  

## Пример 4. Разделение функций с булевым флагом

До:
```python
def save(data, dry_run=False):
    if dry_run:
        print("Dry run: nothing saved")
    else:
        db.save(data)
```

После:
```python
def save(data):
    db.save(data)

def dry_run_save(data):
    print("Dry run: nothing saved")
```

Приём: Разделение функций по булевому флагу  
Комментарий: Упростили каждую функцию, убрав условие и повысив читаемость.  

## Пример 5. Вынесение логики в специализированный тип

До:
```python
def process_coordinates(lat, lon):
    if lat < -90 or lat > 90:
        raise ValueError("Invalid latitude")
    if lon < -180 or lon > 180:
        raise ValueError("Invalid longitude")
    return normalize(lat, lon)
```

После:
```python
class Coordinates:
    def __init__(self, lat, lon):
        if not (-90 <= lat <= 90):
            raise ValueError("Invalid latitude")
        if not (-180 <= lon <= 180):
            raise ValueError("Invalid longitude")
        self.lat = lat
        self.lon = lon

    def normalize(self):
        return normalize(self.lat, self.lon)
```

Приём: Инкапсуляция через специализированный тип (1-е мета-правило)  
Комментарий: Условие перемещено внутрь доменного объекта, больше не повторяется.  


# Вывод

Условные операторы `if` увеличивают сложность кода, мешают тестированию и читаемости, поэтому их стоит осознанно избегать.
Получается есть 2 основных подхода к устранению `if`:

1) Перенос условий туда, где они уже не нужны — например, валидировать данные на входе и далее использовать только корректные объекты.
2) Переписать код так, чтобы сам алгоритм не нуждался в условиях (например, через полиморфизм или `Null Object`).

Основное - это не просто убрать `if`, а избавиться от самой необходимости в условных развилках, делая код декларативным, предсказуемым и устойчивым к изменениям.