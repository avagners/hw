# Декомпозиция большого интерфейса на набор небольших конкретных интерфейсов

## Пример 1: Cервис с методами для всех случаев жизни

Было: 
```python
class UserService:
    def get_user(self, user_id: int) -> User:
        pass
    
    def create_user(self, user_data: dict) -> User:
        pass
    
    def update_user(self, user_id: int, updates: dict) -> User:
        pass
    
    def delete_user(self, user_id: int) -> bool:
        pass
    
    def change_password(self, user_id: int, new_password: str) -> bool:
        pass
    
    def send_email(self, user_id: int, message: str) -> bool:
        pass  # 🤦 Это уже не ответственность UserService!


class UserProfileController:
    def __init__(self, user_service: UserService):  # Зависит от всех методов!
        self.user_service = user_service
    
    def get_profile(self, user_id: int):
        return self.user_service.get_user(user_id)
```

После: 
```python
class UserReader(ABC):
    @abstractmethod
    def get_user(self, user_id: int) -> User: ...

class UserWriter(ABC):
    @abstractmethod
    def create_user(self, user_data: dict) -> User: ...
    
    @abstractmethod
    def update_user(self, user_id: int, updates: dict) -> User: ...

class UserDeleter(ABC):
    @abstractmethod
    def delete_user(self, user_id: int) -> bool: ...

class PasswordManager(ABC):
    @abstractmethod
    def change_password(self, user_id: int, new_password: str) -> bool: ...

# Клиент зависят только от нужного
class UserProfileController:
    def __init__(self, user_reader: UserReader):  # Только чтение
        self.user_reader = user_reader
    
    def get_profile(self, user_id: int):
        return self.user_reader.get_user(user_id)
```

## Пример 2: Конфигурация "на все случаи"

До: 
```python
class AppConfig:
    def __init__(self):
        self.database_url: str
        self.redis_host: str
        self.smtp_server: str
        self.log_level: str
        self.cache_ttl: int
        self.analytics_enabled: bool
        ...

class DatabaseService:
    def __init__(self, config: AppConfig):  # Зависит от всех параметров
        self.connection_string = config.database_url
        # но не использует redis_host, smtp_server и т.д.
```

После: 
```python
class DatabaseConfig(ABC):
    @property
    @abstractmethod
    def database_url(self) -> str: ...

class CacheConfig(ABC):
    @property
    @abstractmethod
    def redis_host(self) -> str: ...

class EmailConfig(ABC):
    @property
    @abstractmethod
    def smtp_server(self) -> str: ...

class DatabaseService:
    def __init__(self, config: DatabaseConfig):  # Только то, что нужно!
        self.connection_string = config.database_url
```

## Пример 3: Репозиторий с CRUD со специфичными методами

До:
```python
class ProductRepository:
    def get_by_id(self, id: int) -> Product: ...
    def get_by_category(self, category: str) -> List[Product]: ...
    def search(self, query: str) -> List[Product]: ...
    def save(self, product: Product) -> None: ...
    def delete(self, id: int) -> None: ...
    def get_popular_products(self) -> List[Product]: ...  # Бизнес-логика
    def update_inventory(self, product_id: int, quantity: int) -> None: ...

# Клиент для поиска зависит от методов изменения
class ProductSearchService:
    def __init__(self, repo: ProductRepository):  # Видит save/delete
        self.repo = repo
    
    def search_products(self, query: str):
        return self.repo.search(query)
```

После: 
```python
class ProductReadRepository(ABC):
    def get_by_id(self, id: int) -> Product: ...
    def get_by_category(self, category: str) -> List[Product]: ...
    def search(self, query: str) -> List[Product]: ...

class ProductWriteRepository(ABC):
    def save(self, product: Product) -> None: ...
    def delete(self, id: int) -> None: ...

class ProductBusinessOperations(ABC):
    def get_popular_products(self) -> List[Product]: ...
    def update_inventory(self, product_id: int, quantity: int) -> None: ...

class ProductSearchService:
    def __init__(self, repo: ProductReadRepository):  # Только чтение
        self.repo = repo
    
    def search_products(self, query: str):
        return self.repo.search(query)
```

## Пример 4: Конфликт ISP и IoC

До:
```python
# IoC-контейнер требует один интерфейс на реализацию
class IDataService(ABC):
    @abstractmethod
    def read_data(self) -> List[Data]: ...
    
    @abstractmethod
    def write_data(self, data: Data) -> None: ...
    
    @abstractmethod
    def validate_data(self, data: Data) -> bool: ...
    
    @abstractmethod
    def export_to_csv(self, data: List[Data]) -> str: ...

# IoC навязывает зависимость от всех методов
class ReportGenerator:
    def __init__(self, data_service: IDataService):  # IoC инжектит все
        self.data_service = data_service
    
    def generate_report(self):
        data = self.data_service.read_data()  # Нужен только read
        # Но видит write_data, validate_data, export_to_csv...
```
После:
```python
# Разделяем интерфейсы, но сохраняем IoC-дружественность
class IDataReader(ABC):
    @abstractmethod
    def read_data(self) -> List[Data]: ...

class IDataWriter(ABC):
    @abstractmethod
    def write_data(self, data: Data) -> None: ...

class DataValidator(ABC):
    @abstractmethod
    def validate_data(self, data: Data) -> bool: ...

# Класс реализует несколько интерфейсов
class DataService(IDataReader, IDataWriter, DataValidator):
    def read_data(self) -> List[Data]: ...
    def write_data(self, data: Data) -> None: ...
    def validate_data(self, data: Data) -> bool: ...

# IoC контейнер может инжектить конкретные интерфейсы
class ReportGenerator:
    def __init__(self, data_reader: IDataReader):  # Чистый ISP
        self.data_reader = data_reader
    
    def generate_report(self):
        return self.data_reader.read_data()
```

## Пример 5: Сервис уведомлений с разными каналами

До:
```python
class NotificationService:
    def send_email(self, to: str, subject: str, body: str) -> bool: ...
    def send_sms(self, phone: str, message: str) -> bool: ...
    def send_push(self, device_id: str, title: str, body: str) -> bool: ...
    def send_slack(self, channel: str, message: str) -> bool: ...

# Клиент зависит от всех каналов
class OrderService:
    def __init__(self, notifier: NotificationService):
        self.notifier = notifier
    
    def confirm_order(self, order: Order):
        # Нужен только email, но видит SMS, push, slack...
        self.notifier.send_email(order.user_email, "Order Confirmed", "...")
```
После:
```python
class EmailNotifier(ABC):
    @abstractmethod
    def send_email(self, to: str, subject: str, body: str) -> bool: ...

class SMSNotifier(ABC):
    @abstractmethod
    def send_sms(self, phone: str, message: str) -> bool: ...

class PushNotifier(ABC):
    @abstractmethod
    def send_push(self, device_id: str, title: str, body: str) -> bool: ...

# Реализация может поддерживать несколько интерфейсов
class MultiChannelNotifier(EmailNotifier, SMSNotifier, PushNotifier):
    def send_email(self, to: str, subject: str, body: str) -> bool: ...
    def send_sms(self, phone: str, message: str) -> bool: ...
    def send_push(self, device_id: str, title: str, body: str) -> bool: ...

class OrderService:
    def __init__(self, email_notifier: EmailNotifier):  # Только email
        self.email_notifier = email_notifier
    
    def confirm_order(self, order: Order):
        self.email_notifier.send_email(order.user_email, "Order Confirmed", "...")
```

## Выводы

Раньше я думал: "Чем больше методов в интерфейсе - тем удобнее. Один большой интерфейс - это неплохо, всё в одном месте!". Плюс ты как-бы объединяешь методы в одном "модуле" - одном "классе".
Теперь понимаю: Я годами нарушал ISP, даже не подозревая об этом.  

Каждый класс должен получать только те методы, которые ему действительно нужны.
Раньше я мокал кучу ненужных методов и думал: "Ну да, так надо". Теперь понимаю - это было следствие плохого дизайна.

Теперь глядя на поля класса, я сразу вижу:
- `email_sender: EmailSender` - значит, только отправка email
- `data_reader: DataReader` - только чтение данных
- `cache: Cache` - только кэш

Раньше было: `service: SomeService` — а что он там делает? ХЗ, нужно лезть в код.

Я боялся, что мелкие интерфейсы сломают IoC-контейнеры. Оказалось - нет. Класс может реализовывать несколько интерфейсов, и контейнер спокойно инжектит нужные.

Что буду делать:
- Прежде чем создать интерфейс спрошу: "Какие именно операции нужны клиенту?"
- Разделю интерфейсы по ролям на `Reader`, `Writer`, `Validator`, `Notifier`.
- Буду использовать `abc.ABC` и `@abstractmethod` для явного указания контрактов.
- В тестах буду использовать spec= чтобы проверять, что мокаю только нужные методы.
- При рефакторинге легаси — начну с разделения интерфейсов, а не с изменения логики.

Теперь когда я вижу `SomeService` с 20+ методами, То у меня чешутся руки разделить его.

