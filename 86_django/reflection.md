# Разрываем скрытые зависимости в Django

## 1. Что это за скрытая связь?

Класс `filebased.EmailBackend` наследуется от `console.EmailBackend`.

Эта связь мешает нескольким модификаций:
- изменение формата вывода в console, так это автоматически сломает filebased;
- изменение логики send_messages в console. Например, если понадобится добавить логирование, то логирование будет и для filebased;


## 2. Выполните рефакторинг этих методов, чтобы устранить скрытую связь.

Оба бэкенда должны наследоваться от `BaseEmailBackend` независимо, дублируя общую логику в `send_messages` или выделяя её в миксин.

Ниже выполнен рефакторинг класса `filebased.EmailBackend`. В итоге класс теперь полностью независим от `console.EmailBackend`. Скрытая связь через наследование устранена.

```python
# django/core/mail/backends/filebased.py
"""Email backend that writes messages to a file."""

import datetime
import os
import threading

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.core.mail.backends.base import BaseEmailBackend


class EmailBackend(BaseEmailBackend):

    def __init__(self, *args, file_path=None, **kwargs):
        # Вызываем базовый класс напрямую, а не console.EmailBackend
        super().__init__(*args, **kwargs)
        self._fname = None
        self.stream = None
        # Свой lock, т.к. больше не наследуемся от console
        self._lock = threading.RLock()
        if file_path is not None:
            self.file_path = file_path
        else:
            self.file_path = getattr(settings, "EMAIL_FILE_PATH", None)
        self.file_path = os.path.abspath(self.file_path)
        try:
            os.makedirs(self.file_path, exist_ok=True)
        except FileExistsError:
            raise ImproperlyConfigured(
                "Path for saving email messages exists, but is not a directory: %s"
                % self.file_path
            )
        except OSError as err:
            raise ImproperlyConfigured(
                "Could not create directory for saving email messages: %s (%s)"
                % (self.file_path, err)
            )
        # Make sure that self.file_path is writable.
        if not os.access(self.file_path, os.W_OK):
            raise ImproperlyConfigured(
                "Could not write to directory: %s" % self.file_path
            )

    def write_message(self, message):
        self.stream.write(message.message().as_bytes() + b"\n")
        self.stream.write(b"-" * 79)
        self.stream.write(b"\n")

    def _get_filename(self):
        """Return a unique file name."""
        if self._fname is None:
            timestamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
            fname = "%s-%s.log" % (timestamp, abs(id(self)))
            self._fname = os.path.join(self.file_path, fname)
        return self._fname

    def open(self):
        if self.stream is None:
            self.stream = open(self._get_filename(), "ab")
            return True
        return False

    def close(self):
        try:
            if self.stream is not None:
                self.stream.close()
        finally:
            self.stream = None

    # Реализуем send_messages самостоятельно, т.к. больше не наследуемся от console
    def send_messages(self, email_messages):
        if not email_messages:
            return
        msg_count = 0
        with self._lock:
            try:
                stream_created = self.open()
                for message in email_messages:
                    self.write_message(message)
                    self.stream.flush()  # flush после каждого сообщения
                    msg_count += 1
                if stream_created:
                    self.close()
            except Exception:
                if not self.fail_silently:
                    raise
        return msg_count
```

## Выводы

Классное упражнение, которое показывает что в таких популярных и общепризнанных проектах как Django, можно встретить ошибки подобного рода. Разработчики Django сэкономили около 15 строк кода, чтобы переиспользовать `send_messages()`. Но из-за этого:
- нельзя изменить `console.EmailBackend`, не рискуя сломать `filebased`;
- невозможно добавить фичу в один бэкенд без побочных эффектов в другом;
- тестирование усложнилось, так как изменения в базовом классе влияют на оба;

Для себя понял, что есть "хорошее" дублирование кода. Метод `send_messages()` теперь дублируется в обоих бэкендах. Но теперь каждый  бэкенд владеет своей логикой полностью и они полностью независимы (то есть нет скрытых связей). Изменения в одном не влияют на другой.
