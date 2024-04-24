# Cтрока кода не соответствует принципу SRP

## 1.
```python
# До
...
df.select(*[c for c in df.columns if c != "dlk_cob_date"]).write.mode("overwrite").orc(path)
...
```

```python
# После
...
columns = [col for col in df.columns if c != "dlk_cob_date"]

df.select(*columns).write.mode("overwrite").orc(path)
...
```

## 2.

```python
# До
...
selected_files.append(self.get_last_files_in_month(self.formation_date + relativedelta(months=range_date * (-1))))
...
```

```python
# После
...
month_date = self.formation_date + relativedelta(months=range_date * (-1))
files = self.get_last_files_in_month(month_date)

selected_files.append(files)
...
```

## 3. 

```python
# До
def process_data(data):
    result = transform_data(clean_data(data))
    save_result_to_database(result)
```

```python
# После
def process_data(data):
    cleaned_data = clean_data(data)
    transformed_data = transform_data(cleaned_data)
    save_result_to_database(transformed_data)
```

## 4. 
```python
# До
...
if (x > 10 and y < 5) or (z == 0 and w != 0) or (a + b > c * d and e / f < g):
    ...
```

```python
# После
condition1 = x > 10 and y < 5
condition2 = z == 0 and w != 0
condition3 = a + b > c * d and e / f < g

if condition1 or condition2 or condition3:
    ...
```

## 5.

```python
# До
...
if new_file.file_ext == 'csv' and len(new_file.file_name) > 0 and date > self.settings.PROMO_DATE_START:
    ...
```

```python
# После
...
is_csv = new_file.file_ext == 'csv'
is_valid_name = len(new_file.file_name) > 0
is_valid_date = date > self.settings.PROMO_DATE_START

if is_csv and is_valid_name and is_valid_date:
    ...
```

---
## Выводы 

"Божественные линии кода" однозначно:
- ухудшают читаемость;
- сильно усложняют отладку;
- усложняется поддержка и будущее расширение (особенно если отсутствуют комментарии);

Перепроверил свой код. Хочу отметить, что в этом отношении у меня нет особенных проблем. Я стараюсь декомпозировать сложную логику на множество отдельных сущностей и не брезгую созданием очередной переменной.