# Плохие моменты в проектировании иерархии классов

## 2. Уровень классов.

### 2.1. Класс слишком большой (нарушение SRP), или в программе создаётся слишком много его инстансов
```python
class Employee:
    def __init__(self, name, age, position, salary):
        self.name = name
        self.age = age
        self.position = position
        self.salary = salary
        self.department = None
        self.address = None
        self.email = None
        self.phone = None
        # Много других свойств и методов...

    def calculate_bonus(self):
        # Расчет бонуса сотрудника
        pass

    def update_salary(self, new_salary):
        # Обновление зарплаты сотрудника
        pass

    def assign_to_department(self, department):
        # Назначение сотрудника в отдел
        pass

    # Множество других методов, относящихся к сотруднику...

# Пример использования класса
employee1 = Employee("John Doe", 30, "Developer", 50000)
employee2 = Employee("Alice Smith", 35, "Manager", 70000)
# ...
```
Данный класс имеет много различных атрибутов и методов. Это усложняет его поддержку, понимание и тестирование.
Можно вынести дополнительные сведения, такие как адрес и контактная информация, в отдельные классы.

### 2.2. Класс слишком маленький или делает слишком мало.

```python
class Calculator:
    def add(self, x, y):
        return x + y

    def subtract(self, x, y):
        return x - y

# Пример использования класса
calc = Calculator()
result = calc.add(5, 3)
print("Результат сложения:", result)
```

Этот класс содержит только два метода, выполняющих базовые арифметические операции. Он не делает достаточно, чтобы оправдать свое существование как отдельная сущность `Calculator`. Вместо этого эти методы можно сделать функциями вне класса.

### 2.3. В классе есть метод, который выглядит более подходящим для другого класса.
```python
class StudentList:
    def __init__(self):
        self.students = []

    def add_student(self, name, age):
        self.students.append({"name": name, "age": age})

    def display_students(self):
        for student in self.students:
            print(f"Name: {student['name']}, Age: {student['age']}")

    def average_age(self):
        total_age = sum(student['age'] for student in self.students)
        return total_age / len(self.students)


class StudentAnalyzer:
    @staticmethod
    def average_age(students):
        total_age = sum(student['age'] for student in students)
        return total_age / len(students)

# Пример использования классов
student_list = StudentList()
student_list.add_student("Alice", 20)
student_list.add_student("Bob", 22)
student_list.add_student("Charlie", 21)

average_age = student_list.average_age()
print("Average Age (StudentList):", average_age)

# Использование StudentAnalyzer
student_data = [{"name": "Alice", "age": 20}, {"name": "Bob", "age": 22}, {"name": "Charlie", "age": 21}]
average_age = StudentAnalyzer.average_age(student_data)
print("Average Age (StudentAnalyzer):", average_age)
```

В данном примере метод `average_age` лучше вынести из класса `StudentList`, так как он не принадлежит непосредственно к списку студентов. Вместо этого его можно выделить в отдельный класс `StudentAnalyzer`, который отвечает за анализ данных о студентах. Это делает код более модульным и читаемым, разделяя логику хранения данных и логику их анализа.

### 2.4. Класс хранит данные, которые загоняются в него в множестве разных мест в программе.
```python
class Configuration:
    def __init__(self):
        self.settings = {}

    def set_setting(self, key, value):
        self.settings[key] = value

# Пример использования класса
config = Configuration()

# В разных частях программы устанавливаются настройки
config.set_setting("database_url", "localhost:5432")
# ...
config.set_setting("max_attempts", 5)

# В другом модуле или части программы также устанавливаются настройки
config.set_setting("logging_level", "DEBUG")
```

В этом примере класс `Configuration` хранит настройки программы, которые устанавливаются в разных частях кода. Это может привести к тому, что данные о настройках будут загружаться из различных источников и переписываться между различными частями программы. Это усложняет управление конфигурацией и может привести к конфликтам данных. Лучше было бы иметь единый механизм для управления настройками и передавать их в класс `Configuration` только тогда, когда это необходимо.

### 2.5. Класс зависит от деталей реализации других классов.

```python
class SmtpClient:
    def __init__(self, smtp_server):
        self.smtp_server = smtp_server

    def send_email(self, sender, recipient, subject, body):
        # Логика отправки письма через SMTP
        pass

class EmailSender:
    def __init__(self):
        self.smtp_client = SmtpClient("smtp.example.com")

    def send_email(self, sender, recipient, subject, body):
        self.smtp_client.send_email(sender, recipient, subject, body)

# Пример использования класса
email_sender = EmailSender()
email_sender.send_email("sender@example.com", "recipient@example.com", "Subject", "Body")
```

В этом примере класс `EmailSender` напрямую зависит от класса `SmtpClient`, используя его для отправки электронных писем через протокол `SMTP`. Это делает класс `EmailSender` тесно связанным с конкретной реализацией отправки писем. Лучше использовать абстракцию или интерфейс для `SmtpClient`, чтобы `EmailSender` зависел только от абстракции, а не от конкретной реализации. Таким образом, мы можем легко заменить `SmtpClient` другой реализацией без изменения кода `EmailSender`.

### 2.6. Приведение типов вниз по иерархии (родительские классы приводятся к дочерним).

```python
class Animal:
    def make_sound(self):
        return "Generic animal sound"

class Cat(Animal):
    def make_sound(self):
        return "Meow!"

def make_cat_sound(cat):
    if isinstance(cat, Cat):
        return cat.make_sound()
    else:
        raise ValueError("Expected object of type Cat")

# Пример использования функции
animal = Animal()
cat = Cat()

try:
    print(make_cat_sound(animal))  # Вызовет ошибку ValueError, так как передан объект animal, а не cat
except ValueError as e:
    print(e)

print(make_cat_sound(cat))  # Вернет "Meow!"
```
Здесь объект класса `Animal` пытается быть обработанным как объект класса `Cat`, что приводит к ошибке приведения типов, поскольку функция `make_cat_sound` ожидает объект типа `Cat`.

### 2.7. Когда создаётся класс-наследник для какого-то класса, приходится создавать классы-наследники и для некоторых других классов.

```python
class Animal:
    # Базовый класс Животное
    pass

class Dog(Animal):
    # Класс Собак, наследуется от Животного
    pass

class Cat(Animal):
    # Класс Кошек, наследуется от Животного
    pass

# Допустим, мы хотим добавить функциональность питомцев для собак и кошек

class Pet:
    # Класс Питомец
    def __init__(self, name):
        self.name = name

# Если мы просто наследуемся от класса Pet, мы потеряем связь с классом Animal
class PetDog(Pet, Dog):
    # Класс Питомец-Собака, наследуется от Питомца и Собаки
    def __init__(self, name):
        Dog.__init__(self)
        Pet.__init__(self, name)

class PetCat(Pet, Cat):
    # Класс Питомец-Кошка, наследуется от Питомца и Кошки
    def __init__(self, name):
        Cat.__init__(self)
        Pet.__init__(self, name)

# Теперь, если мы захотим добавить новую категорию животных, например, Птиц,
# мы не можем просто наследовать их от класса Animal. Нам также нужно будет создать
# дополнительный класс для питомцев-птиц.

class Bird(Animal):
    # Новый класс Птицы, наследуется от Животного
    pass

class PetBird(Pet, Bird):
    # Класс Питомец-Птица, наследуется от Питомца и Птицы
    def __init__(self, name):
        Bird.__init__(self)
        Pet.__init__(self, name)
```

Здесь мы видим, что наличие класса `Pet`, который не является частью общей иерархии `Animal`, приводит к избыточности: для каждого типа питомца нужно создавать отдельный класс-наследник, дублирующий функциональность класса `Pet`.

Это приводит к ситуации, где добавление нового типа животного требует создания еще одного соответствующего класса-наследника питомца, создавая излишне запутанную иерархию классов. Сложность растет с каждым новым видом животных, и это становится узким местом при дальнейшем расширении программы.

Чтобы упростить такую иерархию классов можно использовать композицию вместо наследования, введя концепцию ролей через интерфейсы. 

Например, 
```python
class Animal:
    # Базовый класс Животное
    pass

class Dog(Animal):
    # Класс Собак, наследуется от Животного
    pass

class Cat(Animal):
    # Класс Кошек, наследуется от Животного
    pass

class Bird(Animal):
    # Класс Птиц, наследуется от Животного
    pass

# Вместо создания наследника для каждого типа питомца, добавляем "роль" или поведение питомца.
class Pet:
    # Класс Питомец
    def __init__(self, animal, name):
        self.animal = animal  # Это животное, которое имеет роль питомца
        self.name = name  # Имя питомца

# Теперь мы можем создать питомца любого вида без необходимости создания дополнительных классов.
dog = Dog()
pet_dog = Pet(dog, "Рекс")

cat = Cat()
pet_cat = Pet(cat, "Мурзик")

bird = Bird()
pet_bird = Pet(bird, "Кеша")
```

Это позволяет нам управлять объектами `Pet` независимо от конкретного типа животного.

### 2.8. Дочерние классы не используют методы и атрибуты родительских классов, или переопределяют родительские методы.

```python
from abc import ABC, abstractmethod

class DataProcessor(ABC):
    @abstractmethod
    def read_data(self):
        pass

    @abstractmethod
    def process_data(self, data):
        pass

    @abstractmethod
    def write_data(self, data):
        pass

class CSVDataProcessor(DataProcessor):
    def read_data(self):
        print("Чтение данных из CSV-файла.")
        # Реализация чтения данных из CSV-файла
        return ['csv_data']  # Возвращаем пример данных

    def process_data(self, data):
        print("Обработка CSV данных.")
        # Реализация обработки данных
        processed_data = [d.upper() for d in data]  # Пример обработки данных
        return processed_data

    def write_data(self, data):
        print("Запись данных в CSV-файл.")
        # Реализация записи данных в CSV-файл

class JSONDataProcessor(DataProcessor):
    def read_data(self):
        print("Чтение данных из JSON файла.")
        # Реализация чтения данных из JSON файла
        return ['json_data']  # Возвращаем пример данных

    def process_data(self, data):
        print("Обработка JSON данных.")
        # Реализация обработки данных
        processed_data = [d.lower() for d in data]  # Пример обработки данных
        return processed_data

    def write_data(self, data):
        print("Запись данных в JSON файл.")
        # Реализация записи данных в JSON файл

# Пример использования
csv_processor = CSVDataProcessor()
csv_data = csv_processor.read_data()
processed_csv_data = csv_processor.process_data(csv_data)
csv_processor.write_data(processed_csv_data)

json_processor = JSONDataProcessor()
json_data = json_processor.read_data()
processed_json_data = json_processor.process_data(json_data)
json_processor.write_data(processed_json_data)
```

Когда дочерние классы не используют методы и атрибуты родительских классов или полностью их переопределяют, это может говорить о следующих проблемах:

-- Нарушение принципа подстановки Лисков (Liskov Substitution Principle, LSP): Этот принцип говорит, что объекты в программе должны быть заменяемы на экземпляры их подтипов без изменения корректности программы. Если дочерний класс переопределяет поведение базового класса так, что ожидания от поведения базового класса более не выполняются, это может вызвать непредсказуемое поведение.

-- Неспецифичное наследование: Если дочерний класс не использует функциональность родительского класса, вероятно, он не должен от него наследоваться.

Как улучшить код в указанном примере?

1. Разделить интерфейсы: Вместо того чтобы склонять к реализации всех методов в одном интерфейсе, можно разделить интерфейс на несколько специализированных частей. Таким образом, мы могли бы иметь отдельные интерфейсы для чтения данных (`DataReader`), обработки данных (`DataProcessor`) и записи данных (`DataWriter`).

2. Использовать композицию: Вместо наследования абстракции на все классы, можно воспользоваться композицией, где `DataProcessor` класс будет принимать объекты, реализующие соответствующий интерфейс чтения и записи данных.

```python
from abc import ABC, abstractmethod

class DataReader(ABC):
    @abstractmethod
    def read(self):
        pass

class DataWriter(ABC):
    @abstractmethod
    def write(self, data):
        pass

class CSVReader(DataReader):
    def read(self):
        print("Чтение данных из CSV-файла.")
        return ['csv_data']

class JSONReader(DataReader):
    def read(self):
        print("Чтение данных из JSON-файла.")
        return ['json_data']

class CSVWriter(DataWriter):
    def write(self, data):
        print("Запись данных в CSV-файл.")

class JSONWriter(DataWriter):
    def write(self, data):
        print("Запись данных в JSON-файл.")

class DataProcessor:
    def __init__(self, reader: DataReader, writer: DataWriter):
        self.reader = reader
        self.writer = writer

    def process_data(self):
        data = self.reader.read()
        print(f"Обработка данных: {data}")
        processed_data = [d.upper() for d in data]  # Пример обработки
        self.writer.write(processed_data)

# Использование классов с разделенными функциями чтения и записи:
csv_processor = DataProcessor(CSVReader(), CSVWriter())
csv_processor.process_data()

json_processor = DataProcessor(JSONReader(), JSONWriter())
json_processor.process_data()
```

В этом примере, обработчик данных (`DataProcessor`) может быть сконфигурирован с любым сочетанием средств чтения и записи данных, что делает систему более гибкой и расширяемой. Это также позволяет более легко тестировать каждый компонент раздельно, так как зависимости чётко выделены и могут быть легко заменены или замокированы.

## 3. Уровень приложения.

### 3.1. Одна модификация требует внесения изменений в несколько классов.

```python
class Window:
    def draw(self):
        # рисуем окно со стандартным бордюром
        print("Отрисовка окна со стандартным бордюром")

class DialogWindow(Window):
    def draw(self):
        # рисуем диалоговое окно
        super().draw()
        print("Отрисовка диалогового окна")

class PanelWindow(Window):
    def draw(self):
        # рисуем панельное окно
        super().draw()
        print("Отрисовка панельного окна")

class PopupWindow(Window):
    def draw(self):
        # рисуем всплывающее окно
        super().draw()
        print("Отрисовка всплывающего окна")
```

В данном примере подклассы реализуют метод `draw()` для отображения окна на экране.

Проблемы возникают если потребуется предоставить возможность настраивать отображение бордюра — в некоторых окнах его нужно убрать, а в других — изменить стиль. С текущей реализацией  придется вносить изменения в метод `draw()` каждого класса.

Чтобы избежать этого, можно было бы использовать композицию, создав класс `Border` и интегрировав его в классы окон. Это позволило бы инкапсулировать логику бордюра и проще управлять её изменениями.


### 3.2. Использование сложных паттернов проектирования там, где можно использовать более простой и незамысловатый дизайн.

```python
# Используем паттерн "Фабрика" для создания уведомлений разных типов
from abc import ABC, abstractmethod

class Notification(ABC):
    @abstractmethod
    def send(self):
        pass
    
class EmailNotification(Notification):
    def send(self):
        print("Отправка уведомления по электронной почте")
        
class SMSNotification(Notification):
    def send(self):
        print("Отправка уведомления по SMS")
        
class NotificationFactory:
    @staticmethod
    def get_notification(channel):
        if channel == 'email':
            return EmailNotification()
        elif channel == 'sms':
            return SMSNotification()
        else:
            raise ValueError("Неизвестный канал уведомления")
```

Если всё, что нам нужно — это просто отослать один или два типа уведомлений, мы можем обойтись без использования паттерна `Фабрика`.

Более простой дизайн:

```python
# Простые функции для отправки уведомлений
def send_email_notification():
    print("Отправка уведомления по электронной почте")

def send_sms_notification():
    print("Отправка уведомления по SMS")

# Непосредственное использование функций в коде
send_email_notification()
send_sms_notification()
```

В этом примере мы `просто используем функции` для отправки уведомлений в зависимости от потребностей приложения, без добавления дополнительной абстракции и сложности в виде паттерна `Фабрика`.

Использование сложных паттернов проектирования там, где это не требуется, приводит к:  
-- увеличение сложности;  
-- усложнение поддержки;  
-- ухудшение тестируемости. 

Важно помнить о принципе `KISS ("Keep It Simple, Stupid")` — нужно стремиться к максимальной простоте и избегать ненужной сложности.