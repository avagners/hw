# Правила простого проектного дизайна

## 1. Избавляться от точек генерации исключений, запрещая соответствующее ошибочное поведение на уровне интерфейса класса.

### Пример 1

До: 

Метод `fetch_data` принимает URL в качестве параметра и может привести к ошибкам, если URL неверный или сервер возвращает неуспешный статус-код.

```python
class DataFetcher:

    def fetch_data(self, url):
        response = requests.get(url)
        if response.status_code != 200:
            raise ValueError(f"Failed to fetch data: {response.status_code}")
        return response.json()
```

После:

```python
class InvalidURLError(Exception):
    pass

class URL:
    def __init__(self, url):
        result = urlparse(url)
        if not all([result.scheme, result.netloc]):
            raise InvalidURLError(f"Invalid URL: {url}")
        self.url = url

class DataFetcher:
    def fetch_data(self, url: URL):
        response = requests.get(url.url)
        if response.status_code != 200:
            raise ValueError(f"Failed to fetch data: {response.status_code}")
        return response.json()
```
Добавлен класс `URL`, который проверяет корректность URL на этапе создания.
Метод `fetch_data` принимает объект `URL`, что предотвращает ошибки, связанные с неправильными URL.
Неправильные вызовы теперь предотвращаются на уровне создания объектов.

### Пример 2

До:
Метод `add_user` принимает имя пользователя и может привести к ошибкам, если имя пользователя пустое или пользователь с таким именем уже существует.

```python
class UserManager:
    def __init__(self, db_url):
        self.engine = create_engine(db_url)
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)

    def add_user(self, username):
        if not username:
            raise ValueError("Username cannot be empty")
        session = self.Session()
        if session.query(User).filter_by(username=username).first():
            raise ValueError("User already exists")
        new_user = User(username=username)
        session.add(new_user)
        session.commit()
```

После:

```python
class InvalidUsernameError(Exception):
    pass

class Username:
    def __init__(self, username):
        if not username:
            raise InvalidUsernameError("Username cannot be empty")
        self.username = username

class UserManager:
    def __init__(self, db_url):
        self.engine = create_engine(db_url)
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)

    def add_user(self, username: Username):
        session = self.Session()
        if session.query(User).filter_by(username=username.username).first():
            raise ValueError("User already exists")
        new_user = User(username=username.username)
        session.add(new_user)
        session.commit()
```

Добавлен класс `Username`, который проверяет корректность имени пользователя на этапе создания.
Метод `add_user` принимает объект `Username`, что предотвращает ошибки, связанные с пустыми именами пользователей.
Неправильные вызовы предотвращаются на уровне создания объектов, что делает код более безопасным и надежным.


## 2. Отказ от дефолтных конструкторов без параметров

### Пример 1
В системе управления пользователями необходимо, чтобы объект пользователя всегда создавался с именем и электронной почтой.

До:

```python
class User:
    def __init__(self):
        self.name = ""
        self.email = ""

user = User()  # Не инициализированы имя и почта
```
После:

```python
class User:
    def __init__(self, name, email):
        self.name = name
        self.email = email

user = User("Alice", "alice@example.com")  # Теперь всегда требуется имя и почта
```
Объект пользователя теперь всегда создаётся с обязательными параметрами name и email, что предотвращает создание некорректных объектов.

### Пример 2
В системе управления заказами необходимо, чтобы каждый заказ создавался с уникальным идентификатором и списком товаров.

До:

```python
class Order:
    def __init__(self):
        self.order_id = None
        self.items = []

order = Order()  # Не инициализирован идентификатор заказа и список товаров пуст
```
После:

```python
class Order:
    def __init__(self, order_id, items):
        self.order_id = order_id
        self.items = items

order = Order("12345", ["item1", "item2"])  # Теперь всегда требуется идентификатор заказа и список товаров
```
Объект заказа теперь всегда создаётся с обязательными параметрами order_id и items, что предотвращает создание некорректных объектов.

## 3. Избегание увлечения примитивными типами данных

### Пример 1
До:

```python
def calculate_distance(lat1, lon1, lat2, lon2):
    # Некоторая логика для расчёта расстояния
    pass

distance = calculate_distance(51.5074, -0.1278, 40.7128, -74.0060)  # Сложно понять, какие параметры что означают
```
После:

```python
class Coordinates:
    def __init__(self, latitude, longitude):
        self.latitude = latitude
        self.longitude = longitude

def calculate_distance(coord1, coord2):
    # Некоторая логика для расчёта расстояния
    pass

coord1 = Coordinates(51.5074, -0.1278)
coord2 = Coordinates(40.7128, -74.0060)
distance = calculate_distance(coord1, coord2)  # Теперь параметры понятны
```
Использование класса `Coordinates` вместо отдельных чисел делает код более понятным и защищённым от ошибок.


### Пример 2

До:
```python
def add_product(name, price, quantity):
    # Логика для добавления продукта
    pass

add_product("Apple", 1.2, 10)  # Сложно понять, что означают параметры
```

После:
```python
class Product:
    def __init__(self, name, price, quantity):
        self.name = name
        self.price = price
        self.quantity = quantity

def add_product(product):
    # Логика для добавления продукта
    pass

product = Product("Apple", 1.2, 10)
add_product(product)  # Теперь параметры понятны
```
Использование класса `Product` вместо отдельных параметров делает код более понятным и защищённым от ошибок.


---
## Выводы 

На мой взгляд, если соблюдать данные 3 правила, то:
 - код становится более надёжным, легко читаемым и поддерживаемым, что делает его устойчивым к изменениям;
 - явные интерфейсы и проверки позволяют создавать болеe эффективные тесты;
 