# Code Smell 2

### Пример 1.

```python
    async def create_task(
            self, cmd_plugin: str, cmd_name: str, cmd_args, initiator_id: ct.UserId, msg_payload: t.Dict,
            team_id: str = 'DLK'
    ) -> None:
        ev = None
        task = models.Task.create_epmty_task(initiator_id=initiator_id)
        try:
            command = models._Command(plugin=cmd_plugin, name=cmd_name, arguments=cmd_args)
            user_initiator = await self._user_repository.get_user_with_active_profile(initiator_id)
            team = (await self._team_repository.get_by_id(team_id) or
                    await self._team_command_repository.get_by_plugin_and_command(cmd_plugin, cmd_name) or
                    await self._team_command_repository.get_by_plugin(cmd_plugin) or
                    await self._team_repository.get_by_id('DLK'))
            if (user_initiator.can_independently_execute(plugin=cmd_plugin, cmd=cmd_name) or
                    await self.can_be_executed_independently(cmd_plugin=cmd_plugin, cmd_name=cmd_name,
                                                             cmd_args=cmd_args, msg_payload=msg_payload)) and \
                    not await self.is_under_freeze(cmd_plugin=cmd_plugin, cmd_name=cmd_name, cmd_args=cmd_args):
                # ... создание задачи для себя ...
                task = models.Task.create(...)
                ev = task.release_event(events.TaskForSelfCreated, ...)
            else:
                # ... создание задачи через дежурного ...
                duty_performer = await self._get_duty_performer_for(command, team) or models.User.create_empty_user()
                task = models.Task.create(...)
                ev = task.release_event(events.TaskCreated, ...)

            await self._task_repository.save(task)

        except (exceptions.CouldNotProcessingTask, exceptions.CouldNotProcessingUser, Exception) as e:
            ev = task.release_event(events.TaskProcessedError, ...)
        finally:
            self._dispatcher.dispatch(ev)
```

**Могу ли я чётко сформулировать, что этот код делает?**  
Нет. Метод пытается одновременно: определить команду, найти инициатора, найти команду (через 4 разных репозитория/метода), проверить права на самостоятельное выполнение, проверить "заморозку", создать задачу (в двух разных вариантах), сохранить её в локатор и в БД, выпустить событие и отправить его. Слишком много "если" и перескоков между уровнями абстракции.

**Похоже ли это на то, что должно занимать "10 строк и 2 условия"?**  
Нет. Сейчас это ~45 строк с глубокой вложенностью и сложной логикой выбора команды. Думаю это пример нарушения SRP.

### Пример 2. 
```python
    async def execute(self, task: models.Task) -> None:
        try:
            with paramiko.SSHClient() as ssh:
                cmd = f"{task.command_as_str},b64_payload={task.payload} 2>&1"
                ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                ssh.connect(**asdict(self._creds))
                stdin, stdout, stderr = ssh.exec_command(cmd)
                return_code = stdout.channel.recv_exit_status()
                if return_code == CommandReturnCodes.PLUGIN_NOT_FOUND:
                    raise exceptions.PluginNotFound(...)
                elif return_code == CommandReturnCodes.PLUGIN_CMD_NOT_FOUND:
                    raise exceptions.CommandNotFound(...)
                elif return_code == CommandReturnCodes.PLUGIN_CMD_EXECUTOR_ERROR:
                    stdout_str = stdout.read().decode()
                    if "validator" in task._command.name:
                        raise exceptions.TaskValidationError(stdout_str.split("[224]")[-1].strip())
                    elif "assignor" in task._command.name:
                        raise exceptions.CommandCannotBeSelfAssigned(...)
                    raise exceptions.CouldNotProcessingTask.because_execute_command_ended_with_error(...)
                elif return_code == CommandReturnCodes.INTERNAL_CORE_PLUGIN_ERROR:
                    raise exceptions.InternalPluginError(stdout.read().decode())
                elif return_code == CommandReturnCodes.OK:
                    return
                else:
                    raise exceptions.CouldNotProcessingTask.because_execute_command_ended_with_error(...)
        except (paramiko.AuthenticationException, ...) as e:
            raise exceptions.CouldNotProcessingTask.because_there_was_provider_error(...)
```

**Могу ли я чётко сформулировать, что этот код делает?**  
С трудом. Он выполняет SSH-команду, но внутри зашит блок обработки кодов возврата, который специфичен для разных типов команд (валидаторы, ассигноры). Код "знает" слишком много о внутреннем устройстве плагинов и их именовании (проверка `"validator" in task._command.name`).

**Похоже ли это на то, что должно занимать "10 строк и 2 условия"?**  
Нет. Логика обработки ошибок SSH и логика интерпретации бизнес-ошибок плагинов должны быть разделены. Сейчас это ~35 строк сетевых исключений и парсинга строк вывода.

### Пример 3.
```python
    def _parse_query(self, text: str) -> t.List[str]:
        query = re.findall(CREATE_TASK_RE, text)
        if len(query) < 3:
            raise exceptions.FillRequisitionError.because_requisition_is_not_filled_in_template()
        query[0] = query[0].lower().strip()
        query[1] = query[1].lower().strip()
        query[2] = ''.join([item.strip() for item in query[2].split(' ')]) # remove all spaces
        if len(query) == 3:
            query.append('DLK')
        return query
```

**Могу ли я чётко сформулировать, что этот код делает?**  
Да. Он извлекает параметры команды из текста сообщения с помощью регулярного выражения и нормализует их.

**Похоже ли это на то, что должно занимать "10 строк и 2 условия"?**  
Да. Это компактная вспомогательная функция. Однако она содержит "магические числа" (индексы 0, 1, 2) и жестко зашитую логику `team_id` по умолчанию, что делает её хрупкой.

### Пример 4.
```python
    def release_event(self, event_type: t.Type, description: str) -> events.AbstractTaskEvent:
        if events.TaskProcessedError == event_type:
            self.finalize()

        ev = event_type(
            task_id=str(self._id),
            initiator_id=str(self._initiator.user_id),
            initiator_name=self._initiator.user_nickname,
            command=str(self._command),
            performer_id=str(self._performer.user_id),
            performer_name=self._performer.user_nickname,
            duty_performer_id=str(self._duty_performer.user_id),
            duty_performer_name=self._duty_performer.user_nickname,
            duty_performer_login=self._duty_performer.user_name,
            task_created_at=self._created_at,
            task_closed_at=self._closed_at,
            chat_id=self.chat_id,
            created_at=datetime.now(),
            description=description)

        self._events_log.append(ev.to_orm(None))
        return ev
```

**Могу ли я чётко сформулировать, что этот код делает?**  
Да. Создает объект события на основе текущего состояния задачи, заполняя его данными из полей задачи, и добавляет его в лог событий.

**Похоже ли это на то, что должно занимать "10 строк и 2 условия"?**  
Нет. Метод занимает ~20 строк только на копирование полей из `self` в конструктор события. Это работа, которую можно автоматизировать или упростить, передавая саму задачу в событие.

### Пример 5.

```python
    async def get_by_command(self, plugin: str, command: str, arguments: str) -> t.Optional[models.Freeze]:
        now = datetime.now()
        async with self._async_session() as session:
            freeze_periods_stmt = select(orm.FreezePeriod).where(and_(
                orm.FreezePeriod.start_dttm <= now, orm.FreezePeriod.end_dttm >= now)
            ).order_by(orm.FreezePeriod.end_dttm.desc()).options(selectinload(orm.FreezePeriod.freeze))
            freeze_periods = [
                models.FreezePeriod.from_orm(fp)
                for fp in (await session.execute(freeze_periods_stmt)).scalars().all()
            ]

            for fp in freeze_periods:
                freeze_commands_stmt = select(orm.FreezeCommands).where(and_(
                    orm.FreezeCommands.freeze_id == fp.freeze_id,
                    orm.FreezeCommands.plugin == plugin,
                    or_(orm.FreezeCommands.command.is_(None), orm.FreezeCommands.command == command),
                    or_(orm.FreezeCommands.args_pattern.is_(None), text(f"'{arguments}' ~ args_pattern"))
                ))
                freeze_command = (await session.execute(freeze_commands_stmt)).scalars().first()
                if freeze_command:
                    return fp.freeze
            return None
```

**Могу ли я чётко сформулировать, что этот код делает?**  
Нет. Он выполняет сложный SQL-запрос для поиска активных периодов заморозки, а затем в цикле делает еще по одному запросу на каждый период, чтобы проверить соответствие плагина, команды и паттерна аргументов (используя регулярные выражения прямо в SQL).

**Похоже ли это на то, что должно занимать "10 строк и 2 условия"?**  
Нет. Проблема "N+1" запросов в цикле и сложная логика фильтрации делают этот код тяжелым для понимания. Это должно быть одним эффективным запросом.

### Выводы

Когда я попытался ответить на вопрос **"Что этот код делает?"**, я понял, что не могу сказать это одной фразой. В `create_task` я постоянно спотыкался: "так, тут мы ищем команду... а нет, тут мы проверяем права... подождите, а зачем тут опять репозиторий?". 

Правило **"10 строк и 2 условия"** сначала показалось мне каким-то странным. "Как можно создать задачу в 10 строк?!" Но посмотрев на `release_event`, я увидел, что мы тратим 20 строк просто на перекладывание данных из одного кармана в другой.

Неприятное было в `FreezeRepository`. Я не думал, что мы делаем запросы к базе в цикле. Я просто смотрел на код и думал: "ну, цикл и цикл".

Упражнение научило меня "видеть" сложность там, где я раньше видел "просто рабочий код". Теперь я буду каждый раз спрашивать себя: "Смогу ли я объяснить это за 5 секунд?" и "Не слишком ли много 'если' в этом коде?".