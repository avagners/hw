# Ко-рекурсивный метод разработки

## Пример 1

```python
from datetime import datetime
from typing import List, Dict, Any

# Входные данные: список заказов
orders = [
    {"id": 1, "amount": 150, "date": "2024-01-10"},
    {"id": 2, "amount": 200, "date": "2024-01-15"},
]

# Определяем целевую структуру выходного отчёта
def generate_report(orders: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Формирование отчета о заказах в ко-рекурсивном стиле.
    """

    def generate_summary(orders):
        """Генерирует краткое резюме отчёта: общее число заказов и сумму."""
        return {
            "total_orders": len(orders),
            "total_amount": sum(order["amount"] for order in orders)
        }

    def generate_detailed_list(orders):
        """Генерирует детализированный список заказов с отформатированными датами."""
        return [
            {
                "id": order["id"],
                "amount": order["amount"],
                "formatted_date": datetime.strptime(order["date"], "%Y-%m-%d").strftime("%d-%m-%Y")
            }
            for order in orders
        ]

    def generate_metadata():
        """Добавляет метаданные отчёта (например, время генерации)."""
        return {
            "generated_at": datetime.now().isoformat()
        }

    # Собираем выходной результат, ориентируясь на структуру отчёта
    return {
        "summary": generate_summary(orders),
        "details": generate_detailed_list(orders),
        "metadata": generate_metadata()
    }


report = generate_report(orders)
print(report)
```

Cначала определяем структуру выходного отчёта и создаём отдельные функции для генерации каждого поля.

## Пример 2

```python
import json

# Входные данные: JSON-строка с профилем пользователя
json_data = '''
{
    "name": "John Doe",
    "age": 30,
    "address": {
        "city": "New York",
        "zip": "10001"
    },
    "preferences": {
        "newsletter": true,
        "notifications": false
    }
}
'''

class UserProfile:
    def __init__(self, name, age, city, zip_code, newsletter, notifications):
        self.name = name
        self.age = age
        self.city = city
        self.zip_code = zip_code
        self.newsletter = newsletter
        self.notifications = notifications

    def __repr__(self):
        return f"UserProfile({self.name}, {self.age}, {self.city}, {self.zip_code}, {self.newsletter}, {self.notifications})"

def parse_user_profile(json_string: str) -> UserProfile:
    """
    Построение объекта UserProfile на основе структуры выходных данных.
    """

    def parse_name(data):
        """Извлекаем имя пользователя."""
        return data["name"]

    def parse_age(data):
        """Извлекаем возраст пользователя."""
        return data["age"]

    def parse_address(data):
        """Извлекаем поля адреса."""
        return data["address"]["city"], data["address"]["zip"]

    def parse_preferences(data):
        """Извлекаем предпочтения пользователя."""
        return data["preferences"]["newsletter"], data["preferences"]["notifications"]

    data = json.loads(json_string)

    return UserProfile(
        name=parse_name(data),
        age=parse_age(data),
        city=parse_address(data)[0],
        zip_code=parse_address(data)[1],
        newsletter=parse_preferences(data)[0],
        notifications=parse_preferences(data)[1]
    )


profile = parse_user_profile(json_data)
print(profile)
```

Выходной результат — объект `UserProfile`, структура которого определена заранее.
Разделяем парсинг `JSON` на части: имя, возраст, адрес, предпочтения.
Каждая вспомогательная функция отвечает за создание отдельного компонента объекта.

## Пример 3

```python
from typing import Dict

# Входные данные: структура данных для HTML
page_data = {
    "title": "My Page",
    "header": "Welcome to My Page",
    "paragraphs": [
        "This is the first paragraph.",
        "Here is another paragraph."
    ]
}

def generate_html(data: Dict[str, Any]) -> str:
    """
    Создаёт HTML-страницу, следуя структуре выходных данных.
    """

    def generate_title(data):
        """Генерирует заголовок страницы."""
        return f"<title>{data['title']}</title>"

    def generate_header(data):
        """Генерирует заголовок H1."""
        return f"<h1>{data['header']}</h1>"

    def generate_paragraphs(data):
        """Генерирует параграфы в HTML."""
        return "".join(f"<p>{p}</p>" for p in data["paragraphs"])

    return f"""
    <html>
        <head>{generate_title(data)}</head>
        <body>
            {generate_header(data)}
            {generate_paragraphs(data)}
        </body>
    </html>
    """


html_page = generate_html(page_data)
print(html_page)
```

Исходная структура выходных данных — HTML-страница с тэгами.
Функции отдельно генерируют `<title>`, `<h1>`, `<p>`, что делает код гибким.
Итоговый `HTML` формируется по известной структуре, а не путём обработки входных данных напрямую.

## Итоги

Честно говоря, этот урок перевернул моё представление о том, как можно проектировать программы. Раньше я всегда начинал с анализа входных данных, пытаясь понять, как их обработать и преобразовать. Но подход, при котором структура программы следует за структурой выходных данных, оказался для меня настоящим откровением.  

Первое, что меня удивило — насколько это упрощает процесс мышления. Вместо того чтобы пытаться понять, как трансформировать входные данные, я теперь фокусируюсь на том, каким должен быть результат, и постепенно раскладываю его на части. Оказалось, что это не только облегчает написание кода, но и делает его более понятным и логичным.  

Разделение задачи на небольшие функции, каждая из которых отвечает за конкретную часть выходных данных, даёт ощущение чёткого порядка.
Например, при генерации отчёта мне было легко сначала определить структуру (summary, details, metadata), а затем просто написать функции, которые создают каждую часть. Это сделало код модульным, читаемым и гораздо легче тестируемым.  

Этот урок действительно заставил меня по-новому взглянуть на программирование и дал понимание, что важно не только как обработать входные данные, но и как проектировать, исходя из того, что ты хочешь получить в итоге.