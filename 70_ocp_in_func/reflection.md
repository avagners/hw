# OCP с т.зр. ФП
## 1. Конвейер обработки данных (Data Pipeline)

До:
```python
def process_user_data(data):
    # Все этапы обработки в одной функции
    data = clean_emails(data)
    data = validate_phones(data)
    data = enrich_with_geo(data)
    return data
```

После:
```python
# Базовые функции-процессоры
def clean_emails(data):
    return [item for item in data if '@' in item.get('email', '')]

def validate_phones(data):
    return [item for item in data if len(str(item.get('phone', ''))) >= 10]

def enrich_with_geo(data):
    for item in data:
        item['region'] = detect_region(item.get('ip', ''))
    return data

def remove_duplicates(data):
    seen = set()
    return [item for item in data if item['id'] not in seen and not seen.add(item['id'])]

# Универсальный конвейер
class DataPipeline:
    def __init__(self):
        self.processors = []
    
    def add_processor(self, processor_func):
        """Добавляем новый процессор без изменения конвейера"""
        self.processors.append(processor_func)
        return self
    
    def run(self, data):
        """Применяем все процессоры последовательно"""
        result = data
        for processor in self.processors:
            result = processor(result)
        return result

# Использование
pipeline = (DataPipeline()
    .add_processor(clean_emails)
    .add_processor(validate_phones)
    .add_processor(enrich_with_geo)
    .add_processor(remove_duplicates))

# Добавляем новый процессор без изменения кода
def filter_active_users(data):
    return [item for item in data if item.get('is_active')]

pipeline.add_processor(filter_active_users)

processed_data = pipeline.run(raw_data)
```

## 2. Система валидации данных

До:
```python
def validate_dataset(df, rules):
    errors = []
    if 'email' in rules:
        # проверка email...
    if 'age' in rules:
        # проверка age...
    # Добавить новое правило значит изменить функцию
```
После:
```python
# Библиотека валидаторов
def validate_email(df, column='email'):
    invalid_mask = ~df[column].str.contains('@', na=False)
    return df[invalid_mask][[column]].assign(
        error_type='invalid_email',
        rule='must_contain_at_symbol'
    )

def validate_range(df, column, min_val, max_val):
    invalid_mask = (df[column] < min_val) | (df[column] > max_val)
    return df[invalid_mask][[column]].assign(
        error_type='out_of_range',
        rule=f'between_{min_val}_and_{max_val}'
    )

def validate_required(df, column):
    invalid_mask = df[column].isna() | (df[column] == '')
    return df[invalid_mask][[column]].assign(
        error_type='missing_required',
        rule='field_required'
    )

# Система валидации
class DataValidator:
    def __init__(self):
        self.validators = {}
    
    def register_validator(self, name, validator_func):
        self.validators[name] = validator_func
    
    def validate(self, df, validation_config):
        """
        validation_config = [
            ('validate_email', {'column': 'email'}),
            ('validate_range', {'column': 'age', 'min_val': 0, 'max_val': 150}),
        ]
        """
        all_errors = []
        
        for validator_name, params in validation_config:
            if validator_name in self.validators:
                errors = self.validators[validator_name](df, **params)
                all_errors.append(errors)
        
        return pd.concat(all_errors, ignore_index=True) if all_errors else pd.DataFrame()

# Использование
validator = DataValidator()
validator.register_validator('validate_email', validate_email)
validator.register_validator('validate_range', validate_range)
validator.register_validator('validate_required', validate_required)

# Конфигурация валидации (можно менять без изменения кода)
config = [
    ('validate_email', {'column': 'user_email'}),
    ('validate_range', {'column': 'user_age', 'min_val': 18, 'max_val': 100}),
    ('validate_required', {'column': 'user_name'})
]

errors = validator.validate(df, config)

# Добавляем новый валидатор
def validate_unique(df, column):
    duplicates = df[df.duplicated(subset=[column])]
    return duplicates[[column]].assign(
        error_type='duplicate_value',
        rule='must_be_unique'
    )

validator.register_validator('validate_unique', validate_unique)
```

## 3. Система нотификаций

До:
```python
def send_notification(message, method):
    if method == "email":
        send_email(message)
    elif method == "slack":
        send_slack(message)
    elif method == "telegram":
        send_telegram(message)
```

После:
```python
# Функции-отправители
def send_email(message, config):
    # логика отправки email
    print(f"Email sent: {message}")
    return True

def send_slack(message, config):
    # логика отправки в Slack
    print(f"Slack sent: {message}")
    return True

def send_telegram(message, config):
    # логика отправки в Telegram
    print(f"Telegram sent: {message}")
    return True

def log_notification(message, config):
    # логирование уведомления
    print(f"Logged: {message}")
    return True

# Система нотификации
class NotificationSystem:
    def __init__(self):
        self.senders = {}
        self.default_config = {}
    
    def register_sender(self, name, sender_func, config=None):
        self.senders[name] = {
            'func': sender_func,
            'config': config or self.default_config
        }
    
    def send(self, message, methods=None):
        methods = methods or list(self.senders.keys())
        results = {}
        
        for method in methods:
            if method in self.senders:
                sender_info = self.senders[method]
                try:
                    results[method] = sender_info['func'](message, sender_info['config'])
                except Exception as e:
                    results[method] = f"Error: {e}"
        
        return results

# Использование
notifier = NotificationSystem()
notifier.register_sender('email', send_email, {'smtp_server': 'smtp.example.com'})
notifier.register_sender('slack', send_slack, {'webhook_url': 'https://...'})
notifier.register_sender('telegram', send_telegram, {'bot_token': '...'})
notifier.register_sender('log', log_notification)

# Отправка разными способами
results = notifier.send("Data processing completed", ['email', 'slack', 'log'])

# Добавляем новый способ нотификации
def send_webhook(message, config):
    import requests
    response = requests.post(config['url'], json={'message': message})
    return response.status_code == 200

notifier.register_sender('webhook', send_webhook, {'url': 'https://api.example.com/notify'})
```

## 4. Система трансформации данных

До:
```python
def transform_data(df, transformations):
    for transform in transformations:
        if transform['type'] == 'rename':
            df = df.rename(columns=transform['mapping'])
        elif transform['type'] == 'filter':
            df = df.query(transform['condition'])
```
После:
```python
# Функции-трансформеры
def rename_columns(df, mapping):
    return df.rename(columns=mapping)

def filter_rows(df, condition):
    return df.query(condition)

def add_calculated_column(df, column_name, expression):
    df[column_name] = df.eval(expression)
    return df

def change_types(df, type_mapping):
    return df.astype(type_mapping)

def drop_columns(df, columns):
    return df.drop(columns=columns)

# Система трансформации
class DataTransformer:
    def __init__(self):
        self.transformations = {}
    
    def register_transformation(self, name, transform_func):
        self.transformations[name] = transform_func
    
    def apply_transformations(self, df, transform_config):
        """
        transform_config = [
            ('rename_columns', {'mapping': {'old_name': 'new_name'}}),
            ('filter_rows', {'condition': 'age > 18'}),
        ]
        """
        result = df.copy()
        
        for transform_name, params in transform_config:
            if transform_name in self.transformations:
                result = self.transformations[transform_name](result, **params)
        
        return result

# Использование
transformer = DataTransformer()
transformer.register_transformation('rename_columns', rename_columns)
transformer.register_transformation('filter_rows', filter_rows)
transformer.register_transformation('add_calculated_column', add_calculated_column)
transformer.register_transformation('change_types', change_types)
transformer.register_transformation('drop_columns', drop_columns)

# Конфигурация трансформаций (можно менять без изменения кода)
config = [
    ('rename_columns', {'mapping': {'user_id': 'id', 'user_email': 'email'}}),
    ('filter_rows', {'condition': 'age >= 18'}),
    ('add_calculated_column', {'column_name': 'age_group', 'expression': 'age // 10 * 10'}),
    ('drop_columns', {'columns': ['temp_field']})
]

transformed_df = transformer.apply_transformations(raw_df, config)

# Добавляем новый трансформер
def normalize_column(df, column):
    df[column] = (df[column] - df[column].mean()) / df[column].std()
    return df

transformer.register_transformation('normalize_column', normalize_column)
```

## Выводы 

Раньше пытался всё запихнуть в классы с наследованием. Теперь вижу, что часто проще использовать обычные функции.

Теперь буду стараться проектировать системы так, чтобы новое поведение добавлялось через конфиги, а не правки кода.

Главный вывод - это то, что OCP не про идеальный дизайн, а про удобное и безопасное расширение.

Теперь перед написанием кода задаю себе вопрос:
"Что может измениться в будущем, и как сделать так, чтобы эти изменения не ломали существующий код?"

Думаю во многих случаях ответ почти всегда: "Вынести изменяющуюся часть в отдельные функции и сделать механизм композиции".

Это оказалось намного проще и практичнее, чем я думал.