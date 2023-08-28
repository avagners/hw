# Пример 2
### до (ЦС = 16)
```python
def main():
    params = get_params()

    for log_level in LogLevel:
        if params.verbosity == log_level.name:
            os.environ[DLK_LOG_LEVEL_KEY] = str(log_level.value)
            break
    logger = Logger('FILES_MERGER')
    logger.log('Application started')

    tables = Table.get_from(
        params.metastore,
        params.user,
        params.password,
    )
    logger.log('Tables read')

    if params.table is not None and params.table != '':
        might_be_compacted_tables = tables_from_pattern(params.table, tables)
    elif params.area is not None and params.area != '':
        might_be_compacted_tables = tables_from_area(params.area, params.input, tables)
    else:
        raise RuntimeError('No tables for merging')
    start_dttm = datetime.now()
    plan_stop_dttm = start_dttm + timedelta(minutes=int(params.limit))
    logger.log(f'Planned time to stop is {plan_stop_dttm.strftime("%Y-%m-%d %H:%M:%S")}')

    max_files_per_minute = int(params.rate)
    max_files_per_minute_text = f'{max_files_per_minute} files/minute' if max_files_per_minute > 0 else 'unlimited'
    logger.log(f'Max rate is {max_files_per_minute_text}')

    finished_control_file = init_finished_control_file()

    exec_id = start_dttm.strftime("%Y%m%d%H%M%S")
    spark = create_spark_session(exec_id)

    msck_control_file = init_msck_control_file(spark, logger)

    webhdfs = WebHdfsConnection(params.webhdfs)
    vita = Vita(params.vita)
    merge_statistics = []
    progress_logger = ProgressLogger('FILES_MERGER_PROGRESS', len(might_be_compacted_tables))
    progress_logger.set(0)

    for table in might_be_compacted_tables:
        logger.log(f'Merge table {table.db_table_name} started')
        table_directory = TableDirectory(
            table,
            f'/tmp/files_merger/{exec_id}',
            spark,
            webhdfs,
            vita,
        )
        merge_statistic = table_directory.merge(
            plan_stop_dttm,
            max_files_per_minute,
            finished_control_file,
            msck_control_file,
        )

        if merge_statistic.is_files_changed:
            message = statistic_to_message(
                merge_statistic.files_count_before,
                merge_statistic.total_size_before,
                merge_statistic.files_count_after,
                merge_statistic.total_size_after,
                merge_statistic.elapsed_time,
            )
            logger.log(message)
            merge_statistic.log_to_files('/tmp/merge_hdfs_files_statistic', exec_id)
        merge_statistics.append(merge_statistic)

        if datetime.now() > plan_stop_dttm:
            logger.warn(f'Job duration exceeds planned time, soft finishing...')
            break
        logger.log(f'Merge table {table.db_table_name} finished')
        progress_logger.add(1)
    logger.log('=== Merged tables are listed below ===')

    for ms in merge_statistics:
        if ms.succeeded:
            status = '[OK]  '
        elif ms.failed:
            status = '[FAIL]'
        else:
            status = '[SKIP]'

        if ms.is_files_changed:
            message = statistic_to_message(
                ms.files_count_before,
                ms.total_size_before,
                ms.files_count_after,
                ms.total_size_after,
                ms.elapsed_time,
            )
        else:
            message = 'No files merged'
        logger.log_raw(f'{status} {ms.db_table_name}: => {message}')

    if len(merge_statistics) > 0 and any([ms.is_files_changed for ms in merge_statistics]):
        logger.log('=== TOTAL ===')
        files_count_before = sum([s.files_count_before for s in merge_statistics])
        files_count_after = sum([s.files_count_after for s in merge_statistics])

        if files_count_before != files_count_after:
            total_size_before = sum([s.total_size_before for s in merge_statistics])
            total_size_after = sum([s.total_size_after for s in merge_statistics])
            elapsed_time = timedelta()

            for s in merge_statistics:
                if s.elapsed_time is not None:
                    elapsed_time += s.elapsed_time
            message = statistic_to_message(
                files_count_before,
                total_size_before,
                files_count_after,
                total_size_after,
                elapsed_time,
            )
            logger.log_raw(message)
        else:
            logger.log('No files merged')
    spark.stop()
    logger.log('Application finished')
```

### после (ЦС "main" функции = 3)
```python
# решение: вынес 4 блока кода в отдельные функции,
# избавился от else и излишних if-ов, использовал тернарные операторы
...
def get_tables_for_compacted(params, tables) -> list:
    if params.table and params.table != '':
        return tables_from_pattern(params.table, tables)
    if params.area and params.area != '':
        return tables_from_area(params.area, params.input, tables)
    raise RuntimeError('No tables for merging')


def compact_files(params, tables, spark, start_dttm, logger) -> list:
    plan_stop_dttm = start_dttm + timedelta(minutes=int(params.limit))
    logger.log(f'Planned time to stop is {plan_stop_dttm.strftime("%Y-%m-%d %H:%M:%S")}')

    max_files_per_minute = int(params.rate)
    max_files_per_minute_text = f'{max_files_per_minute} files/minute' if max_files_per_minute > 0 else 'unlimited'
    logger.log(f'Max rate is {max_files_per_minute_text}')

    finished_control_file = init_finished_control_file()

    exec_id = start_dttm.strftime("%Y%m%d%H%M%S")

    msck_control_file = init_msck_control_file(spark, logger)

    webhdfs = WebHdfsConnection(params.webhdfs)
    vita = Vita(params.vita)
    merge_statistics = []
    progress_logger = ProgressLogger('FILES_MERGER_PROGRESS', len(tables))
    progress_logger.set(0)

    for table in tables:
        logger.log(f'Merge table {table.db_table_name} started')
        table_directory = TableDirectory(
            table,
            f'/tmp/files_merger/{exec_id}',
            spark,
            webhdfs,
            vita,
        )
        merge_statistic = table_directory.merge(
            plan_stop_dttm,
            max_files_per_minute,
            finished_control_file,
            msck_control_file,
        )

        if merge_statistic.is_files_changed:
            message = statistic_to_message(
                merge_statistic.files_count_before,
                merge_statistic.total_size_before,
                merge_statistic.files_count_after,
                merge_statistic.total_size_after,
                merge_statistic.elapsed_time,
            )
            logger.log(message)
            merge_statistic.log_to_files('/tmp/merge_hdfs_files_statistic', exec_id)
        merge_statistics.append(merge_statistic)

        if datetime.now() > plan_stop_dttm:
            logger.warn(f'Job duration exceeds planned time, soft finishing...')
            break
        logger.log(f'Merge table {table.db_table_name} finished')
        progress_logger.add(1)
    logger.log('=== Merged tables are listed below ===')
    return merge_statistics


def print_statistics_by_table(merge_statistics, logger) -> None:
    for ms in merge_statistics:
        if not ms.is_files_changed:
            message = 'No files merged'
        status = '[OK]  ' if ms.succeeded else '[FAIL]' if ms.failed else '[SKIP]'  # использование тернарного оператора
        message = statistic_to_message(
            ms.files_count_before,
            ms.total_size_before,
            ms.files_count_after,
            ms.total_size_after,
            ms.elapsed_time,
        )
        logger.log_raw(f'{status} {ms.db_table_name}: => {message}')


def print_total_statistics(merge_statistics, logger) -> None:
    logger.log('=== TOTAL ===')
    files_count_before = sum([s.files_count_before for s in merge_statistics])
    files_count_after = sum([s.files_count_after for s in merge_statistics])

    if files_count_before == files_count_after:
        logger.log('No files merged')
    
    total_size_before = sum([s.total_size_before for s in merge_statistics])
    total_size_after = sum([s.total_size_after for s in merge_statistics])
    elapsed_time = timedelta()

    for s in merge_statistics:
        if s.elapsed_time:
            elapsed_time += s.elapsed_time
    message = statistic_to_message(
        files_count_before,
        total_size_before,
        files_count_after,
        total_size_after,
        elapsed_time,
    )
    logger.log_raw(message)


def main():
    params = get_params()

    for log_level in LogLevel:
        if params.verbosity == log_level.name:
            os.environ[DLK_LOG_LEVEL_KEY] = str(log_level.value)
            break
    logger = Logger('FILES_MERGER')
    logger.log('Application started')

    tables = Table.get_from(
        params.metastore,
        params.user,
        params.password,
    )
    logger.log('Tables read')

    might_be_compacted_tables = get_tables_for_compacted(params=params, tables=tables)

    start_dttm = datetime.now()
    spark = create_spark_session(start_dttm.strftime("%Y%m%d%H%M%S"))

    merge_statistics = compact_files(params, might_be_compacted_tables, spark, start_dttm, logger)

    print_statistics_by_table(merge_statistics, logger)
    print_total_statistics(merge_statistics, logger)

    spark.stop()
    logger.log('Application finished')
```