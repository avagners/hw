# Абстракции против паттерна MVC

## Пример 1. ETL-процессор с интерфейсом 1:1

```python
from abc import ABC, abstractmethod
import pandas as pd
from typing import List, Dict

# Интерфейс 1:1 с реализацией
class IETLProcessor(ABC):
    @abstractmethod
    def extract(self, source: str) -> pd.DataFrame:
        """Извлечь данные из источника"""
        pass
    
    @abstractmethod
    def transform(self, df: pd.DataFrame) -> pd.DataFrame:
        """Трансформировать данные"""
        pass
    
    @abstractmethod
    def load(self, df: pd.DataFrame, target: str) -> None:
        """Загрузить данные в хранилище"""
        pass
    
    @abstractmethod
    def validate(self, df: pd.DataFrame) -> bool:
        """Проверить качество данных"""
        pass
    
    @abstractmethod
    def log_metrics(self, metrics: Dict) -> None:
        """Записать метрики"""
        pass

# Конкретная реализация
class ParquetToPostgresETL(IETLProcessor):
    def extract(self, source: str) -> pd.DataFrame:
        return pd.read_parquet(source)
    
    def transform(self, df: pd.DataFrame) -> pd.DataFrame:
        # Очистка, агрегация...
        return df.dropna()
    
    def load(self, df: pd.DataFrame, target: str) -> None:
        # Загрузка в Postgres
        pass
    
    def validate(self, df: pd.DataFrame) -> bool:
        return df.notnull().all().all()
    
    def log_metrics(self, metrics: Dict) -> None:
        print(f"Metrics: {metrics}")

# Data pipeline использует всё
class DataPipeline:
    def __init__(self, processor: IETLProcessor):
        self.processor = processor
    
    def run(self, source: str, target: str):
        df = self.processor.extract(source)
        if self.processor.validate(df):
            df_transformed = self.processor.transform(df)
            self.processor.load(df_transformed, target)
            self.processor.log_metrics({"rows": len(df_transformed)})
```

Проблемы:
- Клиент (`DataPipeline`) вынужден зависеть от `validate` и `log_metrics`, хотя они могут не понадобиться (например, для сырых данных).
- Нельзя использовать `read-only` реализацию (только `extract`).
- Нарушен ISP.

Исправленный вариант (ролевые протоколы + композиция):
```python
from typing import Protocol, Dict, Any, Optional
import pandas as pd

# Ролевые протоколы (вместо ABC)
class Extractor(Protocol):
    """Роль: извлечение данных"""
    def extract(self, source: str) -> pd.DataFrame:
        ...

class Transformer(Protocol):
    """Роль: трансформация данных"""
    def transform(self, df: pd.DataFrame) -> pd.DataFrame:
        ...

class Loader(Protocol):
    """Роль: загрузка данных"""
    def load(self, df: pd.DataFrame, target: str) -> None:
        ...

class Validator(Protocol):
    """Роль: валидация данных"""
    def validate(self, df: pd.DataFrame) -> bool:
        ...

class MetricsLogger(Protocol):
    """Роль: логирование метрик"""
    def log_metrics(self, metrics: Dict[str, Any]) -> None:
        ...

# Конкретные реализации ролей (можно переиспользовать)
class ParquetExtractor:
    def extract(self, source: str) -> pd.DataFrame:
        return pd.read_parquet(source)

class CSVExtractor:
    def extract(self, source: str) -> pd.DataFrame:
        return pd.read_csv(source)

class CleanTransformer:
    def transform(self, df: pd.DataFrame) -> pd.DataFrame:
        return df.dropna().drop_duplicates()

class AggregationTransformer:
    def transform(self, df: pd.DataFrame) -> pd.DataFrame:
        return df.groupby('category').agg({'value': 'sum'}).reset_index()

class PostgresLoader:
    def load(self, df: pd.DataFrame, target: str) -> None:
        # Логика загрузки в Postgres
        pass

class S3Loader:
    def load(self, df: pd.DataFrame, target: str) -> None:
        # Логика загрузки в S3 (parquet)
        pass

class SimpleValidator:
    def validate(self, df: pd.DataFrame) -> bool:
        return df.notnull().all().all()

class NoOpValidator:
    def validate(self, df: pd.DataFrame) -> bool:
        return True  # Для случаев, когда валидация не нужна

class PrintMetricsLogger:
    def log_metrics(self, metrics: Dict[str, Any]) -> None:
        print(f"Metrics: {metrics}")

# Data pipeline теперь использует только нужные роли
class DataPipeline:
    def __init__(
        self,
        extractor: Extractor,
        transformer: Transformer,
        loader: Loader,
        validator: Optional[Validator] = None,
        logger: Optional[MetricsLogger] = None
    ):
        self.extractor = extractor
        self.transformer = transformer
        self.loader = loader
        self.validator = validator or NoOpValidator()
        self.logger = logger or PrintMetricsLogger()
    
    def run(self, source: str, target: str):
        df = self.extractor.extract(source)
        
        if self.validator.validate(df):
            df_transformed = self.transformer.transform(df)
            self.loader.load(df_transformed, target)
            self.logger.log_metrics({
                "source_rows": len(df),
                "target_rows": len(df_transformed),
                "source": source,
                "target": target
            })

# Композиция под конкретную задачу
pipeline = DataPipeline(
    extractor=ParquetExtractor(),
    transformer=AggregationTransformer(),
    loader=PostgresLoader(),
    validator=SimpleValidator()
)

# Другой pipeline без валидации
fast_pipeline = DataPipeline(
    extractor=CSVExtractor(),
    transformer=CleanTransformer(),
    loader=S3Loader(),
    validator=NoOpValidator()
)
```

Преимущества:
- Каждый pipeline получает только нужные роли.
- Компоненты легко переиспользовать между разными ETL-задачами.
- Тестируемость: мокаем только один компонент.

## Пример 2. Репозиторий для работы с Data Lake (S3 + Glue)
```python
class IDataLakeRepository(ABC):
    @abstractmethod
    def read_parquet(self, path: str) -> pd.DataFrame:
        pass
    
    @abstractmethod
    def write_parquet(self, df: pd.DataFrame, path: str) -> None:
        pass
    
    @abstractmethod
    def read_csv(self, path: str) -> pd.DataFrame:
        pass
    
    @abstractmethod
    def write_csv(self, df: pd.DataFrame, path: str) -> None:
        pass
    
    @abstractmethod
    def list_files(self, prefix: str) -> List[str]:
        pass
    
    @abstractmethod
    def delete_file(self, path: str) -> None:
        pass
    
    @abstractmethod
    def get_file_size(self, path: str) -> int:
        pass

class S3DataLakeRepository(IDataLakeRepository):
    # Реализация всех методов...
    pass

# Контроллер/Orchestrator использует всё
class DataOrchestrator:
    def __init__(self, repo: IDataLakeRepository):
        self.repo = repo
    
    def process_monthly(self, month: str):
        files = self.repo.list_files(f"data/{month}/")
        for file in files:
            if file.endswith('.parquet'):
                df = self.repo.read_parquet(file)
                # обработка
                self.repo.write_parquet(df, f"processed/{month}/")
```

Исправленный вариант (ролевые интерфейсы + CQRS):
```python
from typing import Protocol, List, Optional

# Роли для чтения (Query)
class ParquetReader(Protocol):
    def read_parquet(self, path: str) -> pd.DataFrame:
        ...

class CSVReader(Protocol):
    def read_csv(self, path: str) -> pd.DataFrame:
        ...

class FileLister(Protocol):
    def list_files(self, prefix: str) -> List[str]:
        ...

class FileMetadataReader(Protocol):
    def get_file_size(self, path: str) -> int:
        ...

# Роли для записи (Command)
class ParquetWriter(Protocol):
    def write_parquet(self, df: pd.DataFrame, path: str) -> None:
        ...

class CSVWriter(Protocol):
    def write_csv(self, df: pd.DataFrame, path: str) -> None:
        ...

class FileDeleter(Protocol):
    def delete_file(self, path: str) -> None:
        ...

# Конкретная реализация может комбинировать роли
class S3DataLake:
    def read_parquet(self, path: str) -> pd.DataFrame:
        # Реализация с boto3 + pyarrow
        pass
    
    def write_parquet(self, df: pd.DataFrame, path: str) -> None:
        # Запись в S3
        pass
    
    def list_files(self, prefix: str) -> List[str]:
        # Список файлов
        pass
    
    # Реализует только нужные роли...

# Оркестратор для чтения данных (только Query)
class DataReaderOrchestrator:
    def __init__(
        self,
        reader: ParquetReader,
        lister: FileLister
    ):
        self.reader = reader
        self.lister = lister
    
    def load_all_parquets(self, prefix: str) -> pd.DataFrame:
        files = self.lister.list_files(prefix)
        dfs = []
        for f in files:
            if f.endswith('.parquet'):
                dfs.append(self.reader.read_parquet(f))
        return pd.concat(dfs, ignore_index=True)

# Оркестратор для записи (только Command)
class DataWriterOrchestrator:
    def __init__(
        self,
        writer: ParquetWriter,
        deleter: Optional[FileDeleter] = None
    ):
        self.writer = writer
        self.deleter = deleter
    
    def save_and_cleanup(self, df: pd.DataFrame, path: str, old_path: Optional[str] = None):
        self.writer.write_parquet(df, path)
        if self.deleter and old_path:
            self.deleter.delete_file(old_path)

# Использование
lake = S3DataLake()  # Реализует все роли

reader_orch = DataReaderOrchestrator(
    reader=lake,  # как ParquetReader
    lister=lake   # как FileLister
)

writer_orch = DataWriterOrchestrator(
    writer=lake,  # как ParquetWriter
    deleter=lake  # как FileDeleter
)

# А если нужен только read-only доступ (для аналитики)
class ReadOnlyS3DataLake:
    def read_parquet(self, path: str) -> pd.DataFrame:
        pass
    
    def list_files(self, prefix: str) -> List[str]:
        pass
    # Нет методов записи!

# Подставляем куда угодно, где нужны только чтение
reader_orch_readonly = DataReaderOrchestrator(
    reader=ReadOnlyS3DataLake(),
    lister=ReadOnlyS3DataLake()
)
```

## Пример 3. Data Quality Checker с generic-интерфейсами

```python
class IDataQualityChecker(ABC):
    @abstractmethod
    def check_null_values(self, df: pd.DataFrame, columns: List[str]) -> Dict:
        pass
    
    @abstractmethod
    def check_unique_values(self, df: pd.DataFrame, columns: List[str]) -> Dict:
        pass
    
    @abstractmethod
    def check_range(self, df: pd.DataFrame, column: str, min_val: float, max_val: float) -> Dict:
        pass
    
    @abstractmethod
    def check_data_type(self, df: pd.DataFrame, column: str, expected_type: str) -> Dict:
        pass
    
    @abstractmethod
    def run_all_checks(self, df: pd.DataFrame, rules: Dict) -> Dict:
        pass

class DQChecker(IDataQualityChecker):
    # Реализует всё
    pass

# Всякий раз тянется весь интерфейс
```

Исправленный вариант (generic ролевые интерфейсы):
```python
from typing import Protocol, Any, Dict, List, Optional, TypeVar, Generic
import pandas as pd

T = TypeVar('T')  # Для ковариантности

# Базовые роли для проверок
class NullChecker(Protocol):
    def check_nulls(self, df: pd.DataFrame, columns: List[str]) -> Dict[str, int]:
        """Проверка на null значения"""
        ...

class UniqueChecker(Protocol):
    def check_uniques(self, df: pd.DataFrame, columns: List[str]) -> Dict[str, int]:
        """Проверка уникальности"""
        ...

class RangeChecker(Protocol):
    def check_range(self, df: pd.DataFrame, column: str, min_val: float, max_val: float) -> bool:
        """Проверка диапазона"""
        ...

class DataTypeChecker(Protocol):
    def check_type(self, df: pd.DataFrame, column: str, expected_type: str) -> bool:
        """Проверка типа данных"""
        ...

# Generic интерфейс для композитных проверок
class CompositeChecker(Protocol[T]):
    def run_checks(self, data: T, rules: Dict[str, Any]) -> Dict[str, Any]:
        ...

# Конкретные реализации
class SimpleNullChecker:
    def check_nulls(self, df: pd.DataFrame, columns: List[str]) -> Dict[str, int]:
        return {col: df[col].isnull().sum() for col in columns}

class NoOpNullChecker:
    def check_nulls(self, df: pd.DataFrame, columns: List[str]) -> Dict[str, int]:
        return {}  # Если проверка не нужна

class AdvancedRangeChecker:
    def check_range(self, df: pd.DataFrame, column: str, min_val: float, max_val: float) -> bool:
        return df[column].between(min_val, max_val).all()

# Оркестратор проверок использует только нужные роли
class DataValidator:
    def __init__(
        self,
        null_checker: Optional[NullChecker] = None,
        unique_checker: Optional[UniqueChecker] = None,
        range_checker: Optional[RangeChecker] = None,
        type_checker: Optional[DataTypeChecker] = None
    ):
        self.null_checker = null_checker or NoOpNullChecker()
        self.unique_checker = unique_checker
        self.range_checker = range_checker
        self.type_checker = type_checker
    
    def validate(self, df: pd.DataFrame, rules: Dict) -> Dict:
        results = {}
        
        if 'nulls' in rules and self.null_checker:
            results['nulls'] = self.null_checker.check_nulls(df, rules['nulls'])
        
        if 'uniques' in rules and self.unique_checker:
            results['uniques'] = self.unique_checker.check_uniques(df, rules['uniques'])
        
        if 'range' in rules and self.range_checker:
            for col, (min_val, max_val) in rules['range'].items():
                results[f'range_{col}'] = self.range_checker.check_range(df, col, min_val, max_val)
        
        return results

# Использование: разные валидаторы для разных задач
strict_validator = DataValidator(
    null_checker=SimpleNullChecker(),
    unique_checker=SomeUniqueChecker(),
    range_checker=AdvancedRangeChecker()
)

fast_validator = DataValidator(
    null_checker=SimpleNullChecker()  # Только проверка null
)

# Для streaming данных - валидатор без хранения датафрейма
class StreamNullChecker:
    def check_nulls(self, df: pd.DataFrame, columns: List[str]) -> Dict[str, int]:
        # Оптимизированная проверка для потоков
        return {col: df[col].isna().sum() for col in columns}
```

## Выводы

Раньше я думал, что создавать интерфейс на каждый класс - это признак хорошего тона и залог тестируемости. Но теперь я понял, что это была иллюзия: интерфейс 1:1 с реализацией - это не абстракция, а просто дублирование кода. Такие интерфейсы не скрывают сложность, а добавляют её, заставляя всех клиентов тащить методы, которые им не нужны. Я осознал, что интерфейс должен рождаться не из структуры класса, а из потребностей клиента, который им пользуется. Клиент сам диктует, какие операции ему необходимы, и только тогда мы создаём интерфейс как обещание эти операции выполнять. Это перевернуло моё понимание принципов SOLID, особенно ISP: разделять надо не методы, а роли, которые объект играет во взаимодействии с разными клиентами. Один и тот же объект может быть читателем для одного сервиса, писателем для другого и администратором для третьего, реализуя несколько ролевых интерфейсов. Это делает систему гибкой и безопасной, позволяя легко подменять реализации, например, давая аналитикам только read-доступ без права удалять данные. Я перестал бояться generic-интерфейсов и понял, что они помогают избегать дублирования кода для типовых операций с разными сущностями. 

Я понял, что хороший интерфейс - это не список методов класса, а точное и минимальное обещание клиенту, которое легко понять, легко реализовать и легко заменить. И если интерфейс нужен только для того, чтобы замокать его в тесте - значит, он не нужен вовсе. В итоге я понял, что нужно не создавать искусственные абстракции вокруг классов, а нужно проектировать систему вокруг реальных взаимодействий.
