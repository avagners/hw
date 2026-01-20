# Правильное проектирование на микро-уровне

## Пример 1
До: 
```python
TIME_THRESHOLD = timedelta(hours=1)

def message_filter(messages:  List[Message]) -> tuple:
    fresh = [msg for msg in messages if msg.timestamp >= TIME_THRESHOLD]
    old = [msg for msg in messages if msg.timestamp < TIME_THRESHOLD]
return fresh, old
```

После:

```python
def separate_messages(messages: List[Message]) -> Dict[str, List[Message]]:
    fresh_messages = []
    old_messages = []
    
    for msg in messages:
        if msg.timestamp >= TIME_THRESHOLD:
            fresh_messages.append(msg)
        else:
            old_messages.append(msg)
    
    return {
        'fresh_messages': fresh_messages,
        'old_messages': old_messages
    }
```

### Пример 2
До:
```python
MIN_ADULT_AGE = 18

def filer_user(users: List[User]) -> tuple:
    adults = [user for user in users if user.age >= MIN_ADULT_AGE]
    minors = [user for user in users if user.age < MIN_ADULT_AGE]
return adults, minors
```

После:
```python
def categorize_users(users: List[User]) -> Dict[str, List[User]]:
    minors = []
    adults = []
    
    for user in users:
        if user.age >= MIN_ADULT_AGE:
            adults.append(user)
        else:
            minors.append(user)
    
    return {
        'minors': minors,
        'adults': adults
    }
```

## Выводы

Если честно, то я не задумывался о таких мелочах. Теперь понимаю, насколько это было недальновидно. Особенно мне казалось использование словаря в подобных случаях избыточным. Теперь вижу, что `result['fresh_messages']` намного понятнее, чем `fresh, old = some_function()`. Не нужно держать в голове порядок возвращаемых элементов.

На будущее:
- Нужно регулярно задавать себе вопрос: "А не скрыта ли здесь логическая связь?"
- Чаще использовать словарь вместо кортежа.
