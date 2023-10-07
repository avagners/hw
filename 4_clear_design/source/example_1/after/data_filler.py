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

    source_partition: str = None  # путь к партиции
    target_partition_values: str = None  # значения партиций ('YYYY-MM-DD YYYY-MM-DD')
    table_name: str = None  # наименование таблицы Hive (schema.table_name)
    dlk_ds_code: str = None
    host_api: str = None  # Хост API Vita

    # Команды:
    # постусловие: откат копирования партиции (партиция удалена)
    @abstractmethod
    def rollback_copy_partition(self, partitions: List[str]) -> None: ...

    # постусловие: откат метаданных по протянутой партиции (метаданные удалены)
    @abstractmethod
    def rollback_update_hive_metadata(self, partitions: List[str],
                                      table_name: str) -> None: ...

    # предусловие: target_partition отсутствует
    # постусловие: source_partition скопирована в target_partition
    @abstractmethod
    def copy_partition(self, source_partition: str,
                       target_partition: str) -> str: ...

    # постусловие: добавлены метаданные по всем новым партициям
    @abstractmethod
    def update_hive_metadata(self, partitions: List[str],
                             table_name: str) -> None: ...

    # постусловие: обновлена статистика Hive
    @abstractmethod
    def update_hive_statistics(self, partitions: List[str],
                               table_name: str) -> None: ...

    # постусловие: отправлен статус в Vita
    @abstractmethod
    def add_vita_status(self, partitions: List[str],
                        dlk_ds_code: str, host_api: str) -> None: ...


class DataFiller(AbsDataFiller, HDFSCommand):
    """
    Класс для реализации команды по "протяжке" данных в рамках задачи DLK-1.

    Логика данного класса вызывается командой "copy_partition".

    Реализованные шаги в рамках данного класса:
        - Копировать файлы на HDFS
        - Обновить метаданные в Hive
        - Обновить статистику Hive
        - Отправить статус в Vita

    В случае неуспешного выполнения одной из операций реализованы откаты:
        - _rollback_copy_partition() - удаление созданных партиций
        - _rollback_update_hive_metadata() - удаление метаданых Hive по новым партициям

    Абстрактный метод "execute" наследуется из родительского класса "HDFSCommand" -
    в нем необходимо реализовать всю логику команды.
    """

    source_partition: str = None  # путь к партиции
    target_partition_values: str = None  # значения партиций ('YYYY-MM-DD YYYY-MM-DD')
    table_name: str = None  # наименование таблицы Hive (schema.table_name)
    dlk_ds_code: str = None
    host_api: str = None  # Хост API Vita

    def _get_partition_key_value(self, partition: str) -> List[str]:
        partititon_name = Path(partition).stem.split('=')
        return [partititon_name[0], partititon_name[1]]

    def _bash_execute(self, command: Any, is_shell=False) -> dict:
        process = subprocess.Popen(
            command,
            shell=is_shell,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        stdout, stderr = process.communicate()
        return {
            'stdout': stdout,
            'stderr': stderr,
            'returncode': process.returncode
        }

    def _check_dir_not_exists(self, target_partitions: List[str]) -> None:
        for dir in target_partitions:
            logger.info(f'Checking target partition: {dir}')

            command = ['hadoop', 'fs', '-test', '-d', dir]
            process = self._bash_execute(command)
            if not process['returncode']:
                raise Exception(f'Partition already exists: {dir}. ' +
                                'Choose another target partition')

    def rollback_copy_partition(self, partitions: List[str]) -> None:
        logger.info('Rollback partition copying...')

        for partition in partitions:
            command = ['hadoop', 'fs', '-rm', '-R', partition]
            process = self._bash_execute(command)
            if process['returncode']:
                raise Exception(process['stderr'])
            logger.info(f'Deleted: {partition}')

    def rollback_update_hive_metadata(self, partitions: List[str],
                                      table_name: str) -> None:
        logger.info('Rollback update Hive metadata...')
        for partition in partitions:
            key, value = self._get_partition_key_value(partition)
            command = f'hive -e "alter table {table_name} '
            command += f'drop if exists partition ({key}=\'{value}\');"'
            process = self._bash_execute(command, is_shell=True)
            if process['returncode']:
                raise Exception(process['stderr'])
            logger.info(f'Metadata droped for partition: {partition}')

    def copy_partition(self, source_partition: str,
                       target_partition: str) -> str:
        logger.info(
            f'Start copying: {source_partition} -> {target_partition}'
        )
        command = ['hadoop', 'fs', '-cp', '-f', source_partition, target_partition]
        process = self._bash_execute(command)
        if process['returncode']:
            raise Exception(process['stderr'])
        logger.info(f'Success copy: {source_partition} -> {target_partition}')
        return target_partition.as_posix()

    def _create_hive_command_add_partition(self, partitions: List[str],
                                           table_name: str) -> str:
        command = f'hive -e "alter table {table_name} add '
        add_partititon_commands = []
        for partition in partitions:
            key, value = self._get_partition_key_value(partition)
            add_partititon_commands.append(
                f"partition ({key}=\'{value}\')"
            )
        add_partititons = (' ').join(add_partititon_commands)
        command += add_partititons + ';"'
        return command

    def update_hive_metadata(self, partitions: List[str], table_name: str) -> None:
        logger.info('Starting to update Hive metadata...')
        command = self._create_hive_command_add_partition(partitions, table_name)
        process = self._bash_execute(command, is_shell=True)
        if process['returncode']:
            raise Exception(process['stderr'])

        logger.info(
            f'Metadata Hive successfully updated for the partitions: {partitions}'
        )

    def update_hive_statistics(self, partitions: List[str], table_name: str) -> None:
        logger.info('Starting to update Hive statistics...')
        for partition in partitions:
            key, value = self._get_partition_key_value(partition)
            command = 'hive -e '
            command += f'"analyze table {table_name} '
            command += f'partition ({key}=\'{value}\') compute statistics;"'

            process = self._bash_execute(command, is_shell=True)
            if process['returncode']:
                raise Exception(process['stderr'])

            logger.info(
                f'Statistics successfully updated for the partition: {partition}'
            )

    def add_vita_status(self, partitions: List[str],
                        dlk_ds_code: str, host_api: str) -> None:
        for partition in partitions:
            key, value = self._get_partition_key_value(partition)
            execution_date = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S+00:00")
            json_data = {
                "dlk_ds_code": dlk_ds_code,
                "dlk_parts": [{"name": key, "value": value}],
                "status": "F",
                "execution_date": execution_date,
            }
            logger.info(f'Sending "F" status for {dlk_ds_code} ({key}={value})')
            response = requests.post(
                url=f'http://{host_api}:8002' + "/v2/add_status",
                json=json_data,
                headers={
                    "accept": "application/json",
                    "Content-Type": "application/json",
                }
            )
            if response.status_code != 200:
                raise Exception(f'Error: ({response.status_code}): {response.text}')

            logger.info(
                f'Status "F" has been sent for {dlk_ds_code} ({key}={value})'
            )
            logger.info(
                f'Response from Vita ({response.status_code}): {response.text}'
            )

    def _check_valid_attributes(self) -> None:
        logger.info('Checking arguments...')
        cls_attrs = [a for a, v in DataFiller.__dict__.items()
                     if not re.match('<function.*?>', str(v))
                     and not (a.startswith('__') and a.endswith('__'))
                     and not a.startswith('_')]
        obj_attrs = {a: v for a, v in self.__dict__.items()
                     if not re.match('<function.*?>', str(v))
                     and not (a.startswith('__') and a.endswith('__'))}
        for name_attr in cls_attrs:
            value = obj_attrs.get(name_attr)
            if not value:
                raise AttributeError(f'Please pass on the argument: "{name_attr}".')

    def _get_path_new_partitions(self, parent_dir: str,
                                 new_partition_values: List[str]) -> List[str]:
        key = self._get_partition_key_value(self.source_partition)[0]
        paths = []
        for partition_value in new_partition_values:
            partition_name = f'{key}={partition_value}'
            paths.append(parent_dir / partition_name)
        return paths

    def execute(self) -> None:
        """
        Реализация метода из родительского класса HDFSCommand.
        Здесь реализована вся логика команды "copy_partition".
        """
        logger.info('Application started')
        rollbacks = {}
        try:
            self._check_valid_attributes()
            parent_dir = Path(self.source_partition).parent
            new_partition_values = self.target_partition_values.split()
            path_new_partitions = self._get_path_new_partitions(parent_dir,
                                                                new_partition_values)
            self._check_dir_not_exists(path_new_partitions)
            created_partititons = []
            for partition in path_new_partitions:
                created_partition = self.copy_partition(self.source_partition,
                                                        partition)
                created_partititons.append(created_partition)
                rollbacks['rollback_copy_partition'] = created_partititons
            self.update_hive_metadata(created_partititons, self.table_name)
            rollbacks['rollback_update_hive_metadata'] = [created_partititons, self.table_name]
            self.update_hive_statistics(created_partititons, self.table_name)
            self.add_vita_status(created_partititons,
                                 self.dlk_ds_code,
                                 self.host_api)
        except Exception as err:
            for rollback_command, params in rollbacks.items():
                if rollback_command == 'rollback_update_hive_metadata':
                    self.rollback_update_hive_metadata(*params)
                if rollback_command == 'rollback_copy_partition':
                    self.rollback_copy_partition(params)
            raise err
        logger.info('Application finished')
