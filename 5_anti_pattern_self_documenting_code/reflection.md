# Совмещаем несовместимое

1) Пример 1

```python
"""
Класс "DataFiller" реализует команду "сopy_partition" в
пакете dl_automation.plugin.hdfs, с помощью которой можно
произвести "протяжку" партиций на HDFS.

Команда доступна через:
- cli-команду после установки пакета на сервер;
- джобу в rundeck;
- команду бота в MM;
"""

import logging
import re
import subprocess
from abc import ABC, abstractmethod
from datetime import datetime
from pathlib import Path
from typing import Any, List

import requests

from .base import HDFSCommand

logger = logging.getLogger()


class AbsDataFiller(ABC):
    ...
```

2) Пример 2

```python
"""
SparkSubmitOperatorExt позволяет использовать различные СПУЗы в дагах Airflow 1.

Решена проблема падения тасок из-за ошибки kerberos-аутентификации (GSS).
"""

from airflow.contrib.operators.spark_submit_operator import SparkSubmitOperator

from dlk_airflow_common.hooks.spark_submit_hook_ext import SparkSubmitHookExt
from dlk_airflow_common.library.run_as_user import update_popen_krb5ccname, default_krb5ccname_func


class SparkSubmitOperatorExt(SparkSubmitOperator):
    ...
```

3) Пример 3.

```python
"""
Реализация команды "clear" пакета "dl_automation.plugins.airflow".
Команда позваляет очищать даграны в дагах Airflow 1.

Доступна через:
- cli-команду после установки пакета на сервер;
- команду бота в MM;
"""

from datetime import datetime
import re
import pytz

from dl_automation.plugins.core.application import DlAutomationExecutor
from dl_automation.plugins.core.domain.dlautomationcommand import DlAutomationCommand
from ..exceptions import AirflowCommandError, ReturnCodes


class ClearDagRun(DlAutomationCommand):
    ...
```

---

## Выводы
По итогам выполнения задания пришел к однозначному выводу, что `комментарии, содержащие информацию глобального характера, обязательны в работе`. 

`До` - код содержал комментарии, которые касаются только реализации логики, но ничего не говорят о том, где этот код используется, для чего он был в принципе написан. 

`После` - прочитав комментарии, содержащие информацию глобального характера, можно сразу понять где он используется (в каких модулях, программах) и для чего был написан данный код.

Например, в библиотеке уже был оператор `SparkSubmitOperator`. Было не понятно для каких целей был создан его наследник `SparkSubmitOperatorExt` (по факту эта информация передавалась из уст в уста среди разработчиков). После добавления комментария вопросы становятся излишними.

В примерах 1 и 3 было не понятно, где используются данные команды (особенно для новичков в команде). Да, есть реализация. Да, есть некоторые комментарии к этой реализации. Но место этих команд в общей системе было не понятно. 
Теперь достаточно просто прочитать несколько строк.

В процессе поиска примеров много раз натыкался на различные и довольно сложные модули, которые не содержат никаких комментариев глобального характера.
Место и роль этих модулей в общей системе, не обращаясь к их разработчикам, выяснить довольно сложно. Отсутствует тот самый контекст, который есть у разработчиков этих модулей.

Также, обратил внимания на эмоции, которые получал открывая тот или иной модуль. 

`Легкость, радость, благодарность` - код содержит комментарии глобального характера. Прочитал описание и постепенно спускаюсь в детали, расширяя представление общей системы. Уровень сложности понимая общей системы остается линейным.

`Злость, негодование` - код не содержит комментариев глобального характера. Ты открываешь очередной модуль/пакет и не понимаешь для чего он был создан и какое место занимает в общей системе. Из-за этого нет желания спускаться в детали реализации. Понимание общей системы сильно усложняется.