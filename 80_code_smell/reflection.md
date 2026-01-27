# Code Smell

## 1. Дублирование кода

Классы `NotifyChannel`, `NotifyInitiator` и `NotifyPerformer` содержат значительное дублирование кода.  
**Запах**: Методы, такие как `when_task_assigned`, `when_task_success_executed`, `when_task_rejected` и т.д., имеют почти идентичную структуру.

#### ДО:
```python
class NotifyChannel:
    def when_task_assigned(self, event: ev.TaskAssigned) -> None:
        ...

class NotifyInitiator:
    def when_task_assigned(self, event: ev.TaskAssigned) -> None:
        ...
```

#### ПОСЛЕ:
```python
class BaseNotifyListener:
    def _handle_event(self, event, message_factory, listener_type, show_status_method, error_method):
        ...

class NotifyChannel(BaseNotifyListener):
    def when_task_assigned(self, event: ev.TaskAssigned) -> None:
        self._handle_event(
            ...
```
Напрашивается выделить общий базовый класс или вспомогательный класс для обработки логики уведомлений.


## 2. Большой класс/Божественный объект (Large Class/God Class)

**Запах**: Класс `TaskProcessing` несет слишком много ответственности.

#### ДО:
```python
class TaskProcessing:
    def __init__(self, ...): ...
    
    async def attempt_create_new_task(self, ...): ...
    async def validate_task(self, ...): ...
    async def create_task(self, ...): ...
    async def assign_task(self, ...): ...
    async def cancel_task(self, ...): ...
    async def reject_task(self, ...): ...
    async def execute_task(self, ...): ...
    async def _get_duty_performer_for(self, ...): ...
    async def is_under_freeze(self, ...): ...
```

#### ПОСЛЕ:
Можно разделить на сервисы.

```python
class TaskLifecycleService:
    """Создание и финализация задач"""
    async def create_task(self, ...): ...
    async def attempt_create_new_task(self, ...): ...

class TaskActionService:
    """Действия над задачами"""
    async def assign_task(self, ...): ...
    async def execute_task(self, ...): ...
    async def reject_task(self, ...): ...
    async def cancel_task(self, ...): ...

class DutyService:
    """Работа с дежурствами"""
    async def get_duty_performer(self, ...): ...

class AccessControlService:
    """Проверки прав и заморозок"""
    async def is_under_freeze(self, ...): ...
```

## 3. Длинный список параметров (Long Parameter List)
**Запах**: Множество аргументов в методах создания.

#### ДО:
```python
    @classmethod
    def create(cls, id_: ct.TaskId, command: _Command, initiator: User, performer: User,
               performer_channel: _Channel, duty_performer: User, team: Team,
               msg_payload: t.Optional[t.Dict] = None) -> 'Task':
        return cls._create(id_, command, initiator, performer, performer_channel, duty_performer, team,
                           msg_payload or {})
```

#### ПОСЛЕ:
Можно использовать Parameter Object.

```python
@dataclasses.dataclass
class TaskCreationContext:
    id: ct.TaskId
    command: _Command
    initiator: User
    performer: User
    performer_channel: _Channel
    duty_performer: User
    team: Team
    msg_payload: t.Optional[t.Dict] = None

class Task:
    @classmethod
    def create(cls, context: TaskCreationContext) -> 'Task':
        return cls._create(context.id, context.command, ...)
```

## 4. Одержимость примитивами (Primitive Obsession)
**Запах**: Аргументы хранятся и передаются как строки.

#### ДО:
```python
@dataclasses.dataclass
class _Command:
    plugin: str
    name: str
    arguments: str # Строка "key=value,key2=value2"

    def arguments_to_dict(self) -> t.Dict:
        return {item.split('=')[0]: item.split('=')[1] for item in self.arguments.split(',')}
```

#### ПОСЛЕ:
Можно инкапсулировать аргументы.

```python
class CommandArguments:
    def __init__(self, raw_args: str):
        self._args = self._parse(raw_args)
    
    def get(self, key: str) -> str: ...
    def to_dict(self) -> dict: ...

@dataclasses.dataclass
class _Command:
    plugin: str
    name: str
    arguments: CommandArguments # Объект
```

## 5. Зависть к функциональности (Feature Envy)


### `InitiatorBotPlugin`
**Запах**: Логика парсинга внутри плагина.

#### ДО:
```python
    def _parse_query(self, text: str) -> t.List[str]:
        query = re.findall(CREATE_TASK_RE, text)
        ... # логика очистки и валидации
        return query
```

#### ПОСЛЕ:
Можно вынести в отдельный парсер. Тогда `InitiatorBotPlugin` теперь `завидует` меньше. Он получает уже готовый, структурированный объект `CreateTaskRequest`.

```python
# В Application Layer
class CommandParser:
    def parse_create_request(self, text: str) -> CreateTaskRequest:
        ...

# В Plugin
    def create_task(self, message: Message):
        request = self._command_parser.parse_create_request(message.text)
```

## Выводы

Мне кажется работа над "запахом кода" может вестись непрерывно. Особенно когда у тебя не так много опыта и ты создаешь много "запаха" во время реализации первого релиза. Тебя подгоняют сроки. Регулярно я выполняю очередной коммит с мыслью, что после того, как выпустим проект в прод и пустим первых пользователей, то я обязательно вернусь и поработаю над этим "запахом". Мне практически ежедневно хочется вернуться и внести очередные изменения, которые устранят этот "запах". К слову сказать, я работу эту стараюсь вести и это приносит свои плоды. Я с каждым разом лучше понимаю проект, лучше ориентируюсь в кодовой базе и все время совершенствую свои навыки. Бывает даже в ходе такой работы удается выловить какие-то неявные ошибки. После каждого такого подхода уверенности в своих навыках становится больше.

Сегодня в тренде ИИ. В нашей компании его активно внедряют в работу всех сотрудников. Примерно пол года назад у меня была задача по устранению неявной ошибки в сервисе. Попробовал решить проблему с использованием LLM. Было предложено решение с добавлением нескольких десятков строк нового кода. Посмотрев на этот код, я почувствовал вот такой "запашок". Да, данный код устранял ошибку, но казался избыточным. Тогда я решил изучить документацию фреймворка, который там использовался. Потратив около 40 минут на изучение документации, я внес всего одну строчку кода, которая сбрасывала состояние объекта (что и требовалось для устрания ошибки). 
После данного случая я задумался о последствиях разработки с помощью ИИ-агентов. Да, LLM уже делают свою работу гораздо лучше, чем было еще год назад. И если такой код получается рабочим, но "запаха" у такого кода достаточно много. В принципе как и у людей когда мало опыта и подгоняют по срокам.