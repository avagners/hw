# Hаздутость кода

## Пример 1

Было:
```python
class User:
    def __init__(self, name, permissions):
        self.name = name
        self.permissions = permissions  # Массив, который может содержать и технические, и финансовые права

    def can_access_feature(self, feature):
        # В зависимости от контекста, permissions интерпретируются по-разному
        if feature == "financial_report":
            return "finance_view" in self.permissions or "admin" in self.permissions
        elif feature == "server_control":
            return "tech_admin" in self.permissions or "admin" in self.permissions
        else:
            return "admin" in self.permissions  # По умолчанию — проверка "admin"


user = User("Alice", ["finance_view", "tech_admin"])
print(user.can_access_feature("financial_report"))  # True
print(user.can_access_feature("server_control"))    # True
```
### Почему это раздутость?
- Смешение контекстов:  
Одно поле `permissions` используется для хранения двух разных типов данных: финансовых и технических прав.
- Усложнение условий:  
Логика проверки сильно зависит от контекста и дублируется.
- Нарушение принципа единственной ответственности (`SRP`):  
Один класс решает сразу две задачи: управление пользователем и проверку доступа.

Стало:
```python
class Permissions:
    def __init__(self, financial_permissions=None, technical_permissions=None):
        self.financial_permissions = financial_permissions or set()
        self.technical_permissions = technical_permissions or set()

    def has_financial_access(self, permission):
        return permission in self.financial_permissions

    def has_technical_access(self, permission):
        return permission in self.technical_permissions

class User:
    def __init__(self, name, permissions: Permissions):
        self.name = name
        self.permissions = permissions

    def can_access_financial_report(self):
        return self.permissions.has_financial_access("finance_view")

    def can_access_server_control(self):
        return self.permissions.has_technical_access("tech_admin")


permissions = Permissions(financial_permissions={"finance_view"}, technical_permissions={"tech_admin"})
user = User("Alice", permissions)
print(user.can_access_financial_report())  # True
print(user.can_access_server_control())    # True
```

### Почему стало лучше?  

- Явное разделение контекстов:  
Финансовые и технические права теперь разделены, исключён смешанный список.
- Меньше условий:  
Проверка доступа теперь вызывается через методы `has_financial_access` и `has_technical_access`.
- Простота расширения:  
Легко добавить новые права без изменения основного класса `User`.
- Принцип `SRP`:  
Класс `Permissions` отвечает только за управление правами, а `User` — за пользователя.

Теперь код чище, проще в поддержке и менее подверженным ошибкам.

## Пример 2

Было:
```python
class Order:
    def __init__(self, items, customer_type):
        self.items = items  # Список товаров в заказе
        self.customer_type = customer_type  # 'regular' или 'vip'

    def calculate_discount(self):
        # В зависимости от типа клиента, разная логика скидок + запутанное условие
        if self.customer_type == "vip" and len(self.items) > 5:
            return sum(item['price'] for item in self.items) * 0.2
        elif self.customer_type == "regular" and len(self.items) > 10:
            return sum(item['price'] for item in self.items) * 0.1
        else:
            return 0

    def calculate_total(self):
        total = sum(item['price'] for item in self.items)
        return total - self.calculate_discount()


order = Order([{'price': 100} for _ in range(12)], "regular")
print(order.calculate_total())  # Подсчёт с учётом скидки
```

### Почему это раздутость?

- Смешение условий:  
Логика скидок жёстко связана с проверками в одном методе `calculate_discount`.
- Нарушение `SRP`:  
Один метод одновременно отвечает за логику скидок и структуру заказа.
- Трудности с расширением:  
Добавление новых скидок потребует усложнения условия `if`.
- Магические числа:  
`0.2`, `5`, `0.1` используются без явных пояснений.

Стало:
```python
class DiscountStrategy:
    def calculate_discount(self, order):
        return 0  # Базовая стратегия без скидки


class RegularDiscount(DiscountStrategy):
    def calculate_discount(self, order):
        if len(order.items) > 10:
            return sum(item['price'] for item in order.items) * 0.1
        return 0


class VIPDiscount(DiscountStrategy):
    def calculate_discount(self, order):
        if len(order.items) > 5:
            return sum(item['price'] for item in order.items) * 0.2
        return 0


class Order:
    def __init__(self, items, discount_strategy: DiscountStrategy):
        self.items = items
        self.discount_strategy = discount_strategy

    def calculate_total(self):
        total = sum(item['price'] for item in self.items)
        discount = self.discount_strategy.calculate_discount(self)
        return total - discount


# Использование с разными стратегиями
regular_order = Order([{'price': 100} for _ in range(12)], RegularDiscount())
vip_order = Order([{'price': 100} for _ in range(6)], VIPDiscount())

print(regular_order.calculate_total())  # 1080 с учетом скидки 10%
print(vip_order.calculate_total())      # 480 с учетом скидки 20%
```

### Почему стало лучше?

- Разделение ответственности:  
Класс `Order` теперь отвечает только за структуру заказа, а скидки вынесены в отдельные классы (`DiscountStrategy`).
- Принцип открытости/закрытости (`OCP`):  
Добавить новую стратегию можно, просто создав новый класс.
- Минимизация условий:  
В каждом классе скидок только одно условие, специфичное для конкретного типа скидки.
- Понятность:  
Каждая часть системы выполняет свою задачу.

Теперь код проще расширять, тестировать и поддерживать.

## Пример 3

Было:
```python
class Employee:
    def __init__(self, name, role, salary):
        self.name = name
        self.role = role  # Может быть 'developer', 'manager' или 'intern'
        self.salary = salary

    def calculate_bonus(self):
        # Раздутость через повторяющиеся условия и магические числа
        if self.role == 'developer':
            return self.salary * 0.1
        elif self.role == 'manager':
            return self.salary * 0.2
        elif self.role == 'intern':
            return self.salary * 0.05
        else:
            return 0

    def calculate_tax(self):
        # Повторение условий
        if self.role == 'developer':
            return self.salary * 0.2
        elif self.role == 'manager':
            return self.salary * 0.25
        elif self.role == 'intern':
            return self.salary * 0.1
        else:
            return self.salary * 0.3

    def calculate_net_salary(self):
        return self.salary + self.calculate_bonus() - self.calculate_tax()


employee = Employee("Alice", "developer", 100000)
print(employee.calculate_net_salary())
```

### Почему это раздутость?  

- Повторяющиеся условия:  
Логика расчёта бонусов и налогов зависит от одних и тех же условий.
- Магические числа:  
Значения вроде `0.1`, `0.2` используются без явных констант или комментариев.
- Нарушение `SRP`:  
Класс `Employee` управляет как данными о сотруднике, так и логикой расчёта бонусов и налогов.

Стало:
```python
class BonusStrategy:
    def calculate_bonus(self, salary):
        return 0

class DeveloperBonus(BonusStrategy):
    def calculate_bonus(self, salary):
        return salary * 0.1

class ManagerBonus(BonusStrategy):
    def calculate_bonus(self, salary):
        return salary * 0.2

class InternBonus(BonusStrategy):
    def calculate_bonus(self, salary):
        return salary * 0.05

class TaxStrategy:
    def calculate_tax(self, salary):
        return 0

class DeveloperTax(TaxStrategy):
    def calculate_tax(self, salary):
        return salary * 0.2

class ManagerTax(TaxStrategy):
    def calculate_tax(self, salary):
        return salary * 0.25

class InternTax(TaxStrategy):
    def calculate_tax(self, salary):
        return salary * 0.1

class Employee:
    def __init__(self, name, salary, bonus_strategy: BonusStrategy, tax_strategy: TaxStrategy):
        self.name = name
        self.salary = salary
        self.bonus_strategy = bonus_strategy
        self.tax_strategy = tax_strategy

    def calculate_net_salary(self):
        bonus = self.bonus_strategy.calculate_bonus(self.salary)
        tax = self.tax_strategy.calculate_tax(self.salary)
        return self.salary + bonus - tax


developer = Employee("Alice", 100000, DeveloperBonus(), DeveloperTax())
manager = Employee("Bob", 120000, ManagerBonus(), ManagerTax())

print(f"Developer net salary: {developer.calculate_net_salary()}")
print(f"Manager net salary: {manager.calculate_net_salary()}")
```

### Почему стало лучше?  

- Разделение ответственности:  
Теперь бонусы и налоги разделены на отдельные стратегии (`BonusStrategy`, `TaxStrategy`).
- Устранение повторений:  
Повторяющиеся условия заменены полиморфными методами.
- Принцип открытости/закрытости (`OCP`):  
Добавить новый тип сотрудника можно, просто создав новые классы стратегий.
- Читабельность:  
Каждая часть кода отвечает за свою функцию, код стал проще понимать и расширять.

Теперь логика бонусов и налогов изолирована и расширяется без изменений в основном классе Employee.


## Выводы 

После этого упражнения я понял, насколько важно избегать раздутости кода. Раньше я часто смешивал несколько логик в одном методе, что усложняло понимание и поддержку кода.

Важно разделять ответственность, используя принципы SRP и полиморфизм. Чем проще структура, тем легче её расширять и тестировать.

Теперь буду уделять больше внимания читабельности кода и избегать контекстно-зависимых решений.