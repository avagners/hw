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
    subdir = None
    dag_id = None
    task_regex = None
    no_confirm = True
    downstream = True
    only_failed = False
    start_date = None
    end_date = None

    def _str_to_datetime(self, value: str):
        fmt = "%Y-%m-%d" if re.match(r"^\d{4}-\d{2}-\d{2}$", value) else "%Y-%m-%dT%H:%M"
        dt = datetime.strptime(value, fmt)
        return dt.replace(tzinfo=pytz.UTC)

    @property
    def start_date(self):
        return self._start_date

    @property
    def end_date(self):
        return self._end_date

    @start_date.setter
    def start_date(self, value):
        self._start_date = self._str_to_datetime(value)

    @end_date.setter
    def end_date(self, value):
        self._end_date = self._str_to_datetime(value)

    def __getattr__(self, item):
        return False


class ClearDagRunValidator(DlAutomationExecutor):

    def _execute(self, cmd: ClearDagRun):
        if cmd.dag_id.startswith(("imp_dlt.", "imp_dltc.")):
            raise AirflowCommandError(
                message="Перезапуск DLT/DLTC дагов не выполняется",
                return_code=ReturnCodes.BUSINESS_LOGIC_NOT_VALID
            )
        if not cmd.start_date:
            raise AirflowCommandError(
                message="Аргумент 'start_date' обязателен для заполнения",
                return_code=ReturnCodes.BUSINESS_LOGIC_NOT_VALID
            )
        if cmd.end_date and cmd.end_date < cmd.start_date:
            raise AirflowCommandError(
                message="Аргумент 'end_date' не может быть меньше 'start_date'",
                return_code=ReturnCodes.BUSINESS_LOGIC_NOT_VALID
            )
