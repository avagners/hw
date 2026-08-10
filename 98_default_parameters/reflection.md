# Дефлотные параметры -- зло 

## 1. Кэширование подключений к БД с мутабельным дефолтом

```python
# ПЛОХО: коннекшн пул расшарен между всеми вызовами
class DatabaseConnector:
    def __init__(self):
        self.pool = []
    
    def get_connection(self, connection_pool=[]):
        if not connection_pool:
            # Создаём новое подключение
            connection_pool.append(create_db_connection())
        return connection_pool[0]  # ❌ Все вызовы используют одно подключение

# В реальной работе:
conn1 = db.get_connection()  # Создаётся подключение
conn2 = db.get_connection()  # Используется то же подключение ❌
# Первое подключение могло упасть, а мы его всё ещё используем!
```

Исправление:
```python
class DatabaseConnector:
    def __init__(self):
        self.pool = []
    
    def get_connection(self, connection_pool=None):
        if connection_pool is None:
            connection_pool = []
        if not connection_pool:
            connection_pool.append(create_db_connection())
        return connection_pool[0]  # ✅ Безопасно
```

## 2. Аккумуляция данных в ETL-пайплайнах

```python
# ПЛОХО: накопление данных между вызовами
def process_batch(batch_data, accumulated=[]):
    accumulated.extend(batch_data)  # ❌ Старый список модифицируется
    return accumulated

# Паттерн обработки больших данных:
batch1 = [1, 2, 3]
batch2 = [4, 5, 6]
batch3 = [7, 8, 9]

result1 = process_batch(batch1)  # [1, 2, 3]
result2 = process_batch(batch2)  # [1, 2, 3, 4, 5, 6] ❌
result3 = process_batch(batch3)  # [1, 2, 3, 4, 5, 6, 7, 8, 9] ❌

# Ой! Мы случайно склеили все батчи, хотя хотели обрабатывать независимо
# При работе с Spark/Dask это может вызвать OOM ошибки!
```

Исправление:
```python
def process_batch_good(batch_data, accumulated=None):
    if accumulated is None:
        accumulated = []
    # Создаём КОПИЮ для агрегации
    new_accumulated = accumulated.copy()
    new_accumulated.extend(batch_data)
    return new_accumulated  # ✅ Каждый вызов возвращает новый список

result1 = process_batch_good([1, 2, 3])  # [1, 2, 3]
result2 = process_batch_good([4, 5, 6])  # [4, 5, 6]
```

## 3. Статические конфигурации партиционирования
```python
# ПЛОХО: партиции вычисляются один раз при деплое
from datetime import datetime, timedelta

def process_partition(
    partition_date=datetime.now().replace(day=1),  # ❌ Заморожено на момент деплоя
    days=30
):
    start_date = partition_date - timedelta(days=days)
    return query_data(start_date, partition_date)

# Запускаем сегодня (2026-08-10):
process_partition()  # Партиции: 2026-08-01 до 2026-08-31

# Запускаем через месяц (2026-09-10):
process_partition()  # ❌ Всё ещё 2026-08-01 до 2026-08-31!
```

Исправление:
```python
def process_partition_good(partition_date=None, days=30):
    if partition_date is None:
        partition_date = datetime.now().replace(day=1)  # ✅ Актуальная дата
    
    start_date = partition_date - timedelta(days=days)
    return query_data(start_date, partition_date)
```

Хорошие практики в работе дата-инженера

## 1. Дефолтные параметры для трансформаций схемы
```python
# ХОРОШО: прозрачные дефолты для ETL-преобразований
def transform_events(
    events_df,
    partition_cols=["year", "month", "day"],  # Дефолтная партиция
    format="parquet",
    mode="overwrite"
):
    """
    Партиционирует DataFrame по стандартной схеме
    """
    df = events_df.select(
        "*",
        year("timestamp").alias("year"),
        month("timestamp").alias("month"),
        day("timestamp").alias("day")
    )
    
    df.write \
      .partitionBy(*partition_cols) \
      .format(format) \
      .mode(mode) \
      .save("s3://bucket/events/")

# Использование:
df = spark.read.parquet("s3://bucket/raw/events/")
transform_events(df)  # Партиционирует по умолчанию

# Override только одного параметра:
transform_events(df, partition_cols=["date", "hour"])
```

## 2. Тестирование с постоянными дефолтами
```python
# ХОРОШО: стабильные дефолты для CI/CD тестов
def validate_quality(
    df,
    null_threshold=0.05,    # Максимум 5% null
    distinct_threshold=100, # Минимум 100 уникальных значений
    sample_size=1000        # Проверяем семпл из 1000 строк
):
    """
    Проверка качества данных с дефолтами, подходящими для CI
    """
    total_rows = df.count()
    sample_df = df.limit(sample_size)
    
    for col in df.columns:
        null_count = sample_df.filter(col(col).isNull()).count()
        null_ratio = null_count / sample_size
        
        if null_ratio > null_threshold:
            raise ValueError(f"Колонка {col} содержит {null_ratio*100:.1f}% null")
    
    return True

# В продакшене можно переопределить более строгие лимиты:
validate_quality(prod_df, null_threshold=0.01, sample_size=10000)

# В тестах - дефолты идеально подходят
def test_quality():
    test_df = generate_test_data()
    assert validate_quality(test_df) == True  # ✅ Понятно и предсказуемо
```

## 3. Параметры для дедупликации
```python
# ХОРОШО: понятная дедупликация с безопасными дефолтами
def deduplicate_records(
    df,
    id_col="user_id",
    order_col="event_timestamp",
    keep="last"  # Держим последнюю запись по времени
):
    """
    Дедупликация с дефолтной стратегией
    """
    from pyspark.sql import Window
    import pyspark.sql.functions as F
    
    window = Window.partitionBy(id_col).orderBy(
        F.desc(order_col) if keep == "last" else F.asc(order_col)
    )
    
    return df.withColumn("_row_num", F.row_number().over(window)) \
             .filter(F.col("_row_num") == 1) \
             .drop("_row_num")

# Использование:
events = spark.read.parquet("s3://bucket/events/")
deduped = deduplicate_records(events)  # Дефолтное поведение

# Для специфического кейса:
premium_deduped = deduplicate_records(
    events, 
    id_col="user_id", 
    order_col="purchase_amount",  # Держим самую дорогую покупку
    keep="first"
)
```

## 4. Параметры для логгирования в пайплайнах
```python
# ХОРОШО: удобные дефолты для мониторинга
def process_pipeline(
    data_path,
    batch_id=None,           # None = авто-генерация
    log_to_s3=True,          # По умолчанию логируем в S3
    log_level="INFO",
    retry_count=3,
    timeout_minutes=30
):
    """
    Дата-пайплайн с безопасными дефолтами
    """
    if batch_id is None:
        batch_id = f"batch_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    logger = configure_logging(log_to_s3, log_level)
    logger.info(f"Запуск пайплайна {batch_id}")
    
    for attempt in range(retry_count):
        try:
            result = process_data(data_path, timeout=timeout_minutes)
            logger.info(f"Успешно: {batch_id}")
            return result
        except Exception as e:
            logger.warning(f"Попытка {attempt+1} упала: {e}")
            if attempt == retry_count - 1:
                raise
    
    return None

# В крон-джобе:
process_pipeline("s3://bucket/raw/2026-08-10/")  # ✅ Просто и понятно

# В ручном запуске с кастомными параметрами:
process_pipeline(
    "s3://bucket/raw/2026-08-10/",
    log_to_s3=False,     # Для локального теста
    retry_count=5,
    timeout_minutes=60
)
```

## Выводы

Я обычно использовал дефолтные параметры не задумываясь. Но теперь я пересмотрел к этому свое отношение.

Я усвоил простое правило: для изменяемых объектов всегда нужно использовать `None` и создавать новое значение внутри функции. Такой подход спасает от неожиданных сюрпризов в продакшене и делает код гораздо более предсказуемым. При этом я понял, что иммутабельные дефолты - это мощный инструмент для упрощения интерфейсов, особенно когда речь идёт о строках, числах или булевых флагах. Но как только появляется хотя бы малейшее сомнение в мутабельности, я теперь без колебаний выбираю безопасный вариант с `None`. Это знание изменило моё отношение к, казалось бы, тривиальной возможности языка и заставило пересмотреть старые проекты.