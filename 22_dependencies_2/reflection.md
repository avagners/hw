# Зависимости от зависимостей - 2

## 1. Зависимость от системы хранения данных (например, S3 или HDFS)
**Семантика**:

Тип данных: система хранения может поддерживать разнообразные форматы данных (CSV, JSON, Parquet и т.д.).  
Логическая структура: данные могут быть организованы в виде файловой системы или объектов (в случае S3).  
Взаимодействие: доступ через API для загрузки, выгрузки, модификации данных.  

**Ключевые свойства**:

Надежность: данные должны сохраняться и быть доступны даже при сбоях инфраструктуры.  
Производительность: скорость чтения и записи данных может сильно влиять на производительность.  
Масштабируемость: хранилище должно поддерживать рост объема данных и запросов без потери производительности.

**Пространство допустимых изменений**:

Можно изменить конкретное хранилище (например, заменить S3 на HDFS), но это потребует адаптации к API и возможным изменениям в форматах данных или скорости взаимодействия.
Ограничение по изменению базовой инфраструктуры — переход между различными типами хранилищ может затронуть код системы и логику обработки данных (например, управление частями больших данных при загрузке в распределённую файловую систему).

##  2. Зависимость от системы потоковой обработки данных (например, Apache Kafka)
**Семантика**:

Потоковые данные: данные передаются в виде сообщений, которые группируются в топики.
Обработка в реальном времени: платформа гарантирует доставку сообщений и их порядок.
Консьюмеры и продюсеры: приложение действует как продюсер данных или консьюмер, который потребляет потоковые данные.

**Ключевые свойства**:

Низкая задержка: данные должны обрабатываться в реальном времени или с минимальной задержкой.  
Гарантия доставки: данные не должны теряться, даже при сбоях.  
Масштабируемость: поддержка высокой пропускной способности для больших объёмов данных.

**Пространство допустимых изменений**:

Возможна замена платформы (например, на Apache Pulsar), но потребуется изменять механизмы взаимодействия с очередями, изменять логику продюсеров и консьюмеров.
Допустимо добавление ретеншен-политик для разных топиков или изменение уровня параллелизма, но это повлияет на производительность и поведение при потреблении данных.

## 3. Зависимость от системы управления потоками данных (например, Apache Airflow)
**Семантика**:

DAG (Directed Acyclic Graph): задачи в Airflow организуются в виде DAG-ов, что позволяет определять зависимости между шагами.  
Параллельные выполнения: поддержка выполнения нескольких задач параллельно или с зависимостями.  
Триггеры: задачи могут запускаться по расписанию или по событиям.  

**Ключевые свойства**:

Управление зависимостями: гарантируется выполнение задач в строго заданном порядке.  
Надежность: система должна корректно обрабатывать сбои и автоматические перезапуски задач.  
Расширяемость: возможность интеграции с внешними системами через хуки и операторы.  

**Пространство допустимых изменений**:

Можно перейти на другую оркестрационную систему (например, Luigi), но это повлечёт изменения в структуре DAG-ов и взаимодействии с задачами.
Допустимо изменение конфигурации выполнения задач (например, увеличение параллелизма), но это может привести к изменению времени выполнения задач или возникновению коллизий при доступе к ресурсам.

## 4. Зависимость от системы мониторинга данных (например, Prometheus или Grafana)
**Семантика**:

Сбор метрик: система собирает метрики работы приложений, серверов или баз данных в режиме реального времени.  
Хранение данных: данные метрик сохраняются в формате временных рядов для дальнейшего анализа.  
Визуализация и алерты: предоставляет интерфейс для построения графиков и создания уведомлений при нарушении установленных порогов.

**Ключевые свойства**:

Надежность сбора данных: метрики должны собираться без пропусков, особенно для критически важных процессов.  
Гибкость настройки: система должна поддерживать настройку метрик и уведомлений в зависимости от нужд проекта.  
Интеграция: возможность интеграции с различными системами (базы данных, веб-приложения, API) для мониторинга и отображения.

**Пространство допустимых изменений**:

Переход на другую систему мониторинга (например, с Prometheus на Datadog) потребует настройки новых агентов сбора метрик и пересмотра существующих дашбордов.
Можно добавить новые источники данных для мониторинга или изменить параметры алертов, что увеличит детализацию мониторинга, но может потребовать дополнительных ресурсов для хранения метрик.
Изменение частоты сбора метрик (увеличение или уменьшение) напрямую повлияет на количество данных, их точность и нагрузку на хранилище.

---
## Выводы

В результате выполнения этой работы я лучше понял важность и сложность управления зависимостями. 

Зависимости различаются по природе. Это могут быть хранилища данных, системы обработки потоков, ETL-инструменты, системы мониторинга и аналитические базы данных. 
Каждая из них требует особого подхода к управлению и изменению.  

Для каждой зависимости важно учитывать три ключевые характеристики: 
- её семантику (как она работает);
- ключевые свойства (что критично для её работы);
- пространство допустимых изменений (как можно модифицировать систему без потерь в качестве и производительности);

Изменения могут быть дорогостоящими. Замена одного компонента на другой часто требует пересмотра всей системы. Это подчёркивает необходимость тщательной планировки и анализа перед внесением изменений.

Важно выбирать такие решения и компоненты, которые позволяют легко адаптироваться к изменениям требований и масштабируемости системы.

Эти знания помогут мне лучше справляться с реальными задачами, связанными с архитектурой и разработкой систем.
