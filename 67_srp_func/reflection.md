# SRP с точки зрения ФП

## Пример 1. Обработка входящих сообщений (бот поддержки)

До (императивно):
```python
def handle_message(event):
    text = event["text"]
    user = event["user"]
    if "инструкция" in text:
        send_link(user, "https://wiki.company/platform/setup")
    elif "ошибка" in text:
        log_error(user, text)
        send_reply(user, "Передайте лог в поддержку")
    else:
        send_reply(user, "Не понимаю запрос")
```

Проблема: одна функция отвечает и за анализ текста, и за выбор реакции, и за отправку ответа.

После (SRP + ФП):
```python
def detect_intent(text: str) -> str:
    if "инструкция" in text:
        return "docs"
    if "ошибка" in text:
        return "error"
    return "unknown"

def build_response(intent: str) -> str:
    match intent:
        case "docs": return "Вот ссылка: https://wiki.company/platform/setup"
        case "error": return "Передайте лог в поддержку"
        case _: return "Не понимаю запрос"

def handle_message(event):
    user, text = event["user"], event["text"]
    intent = detect_intent(text)
    reply = build_response(intent)
    send_reply(user, reply)
```

Теперь каждая функция имеет одну ответственность:
- `detect_intent` - классифицирует сообщение,
- `build_response` - решает, что сказать,
- `handle_message` - лишь связывает их вместе.


## Пример 2. Генерация YAML-навыка

До:
```python
def create_skill_yaml(name, triggers, response):
    data = {"name": name, "triggers": triggers, "response": response}
    with open(f"{name}.yaml", "w") as f:
        yaml.dump(data, f)
    print(f"Skill {name} created!")
```

Здесь логика генерации, сериализации и побочного эффекта (I/O) смешаны.

После (SRP + ФП):
```python
import yaml
from pathlib import Path

def make_skill_spec(name: str, triggers: list[str], response: str) -> dict:
    return {"name": name, "triggers": triggers, "response": response}

def dump_yaml(data: dict) -> str:
    return yaml.safe_dump(data, sort_keys=False, allow_unicode=True)

def save_to_file(content: str, path: Path) -> None:
    path.write_text(content, encoding="utf-8")

def create_skill(name, triggers, response):
    spec = make_skill_spec(name, triggers, response)
    yaml_str = dump_yaml(spec)
    save_to_file(yaml_str, Path(f"{name}.yaml"))
```

Теперь каждая функция:
- создаёт данные,
- преобразует их,
- сохраняет результат - отдельно.

## Пример 3. Подготовка данных для аналитики

До:
```python
def prepare_data(df):
    df["date"] = pd.to_datetime(df["date"])
    df["month"] = df["date"].dt.month
    df = df[df["amount"] > 0]
    df["avg_per_user"] = df.groupby("user")["amount"].transform("mean")
    return df
```

Функция делает всё подряд - и фильтрацию, и трансформации.

После:
```python
def normalize_dates(df):
    df["date"] = pd.to_datetime(df["date"])
    return df

def filter_positive(df):
    return df[df["amount"] > 0]

def add_month_column(df):
    df["month"] = df["date"].dt.month
    return df

def add_avg_per_user(df):
    df["avg_per_user"] = df.groupby("user")["amount"].transform("mean")
    return df

def prepare_data(df):
    return add_avg_per_user(add_month_column(filter_positive(normalize_dates(df)))
```

Код стал декларативным:
"Возьми данные → нормализуй → отфильтруй → добавь месяц → добавь среднее".
Каждая функция имеет одну цель.

## Пример 4. Проверка качества данных

До:
```python
def check_table(table_name):
    rows = query(f"SELECT COUNT(*) FROM {table_name}")
    if rows == 0:
        print("Пустая таблица")
    elif rows > 1_000_000:
        print("Слишком большая таблица")
    else:
        print("ОК")
```

После:
```python
def get_row_count(table_name) -> int:
    return query(f"SELECT COUNT(*) FROM {table_name}")

def assess_table_size(rows: int) -> str:
    if rows == 0: return "empty"
    if rows > 1_000_000: return "large"
    return "ok"

def report_status(table_name, status: str):
    print(f"Table {table_name}: {status}")

def check_table(table_name):
    count = get_row_count(table_name)
    status = assess_table_size(count)
    report_status(table_name, status)
```

## Выводы

После этого упражнения я понял, что принцип SRP в функциональном подходе - это не про “делить классы”, а про чистоту смысла каждой функции.

Раньше я думал, что “одна ответственность” - значит “у класса мало методов”.
А теперь вижу, что в функциональном коде ответственность - это не “у кого”, а “что именно делает операция с данными”.
Функция должна отвечать за одно преобразование - не больше.

Когда я разбил одну большую функцию на 3–4 маленькие, весь код стал как цепочка из Lego:
читается сверху вниз, легко тестируется, можно переставлять блоки местами.

Разделение функций по смыслу помогает избавиться от скрытых сайд-эффектов.

Теперь, когда я пишу новую функцию, я автоматически задаю себе вопрос:
«Она делает одно преобразование данных или сразу три?»
Если три - значит, надо разбить.

Когда каждая функция - это один смысл, код становится не просто читаемым, а самообъясняющимся.
Я увидел, что мой код можно понять без контекста - просто глядя на названия функций и порядок их вызова.