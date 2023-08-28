# Пример 1
## до (ЦС = 11)
```python
def _import_dict(self) -> None:
    if self.level == 'system':
        self.__import_dict(System)
    elif self.level == 'dataset':
        self.__import_dict(Dataset)
    elif self.level == 'chkpt_rule':
        self.__import_dict(ChkptRule)
    elif self.level == 'dag_etl':
        self.__import_dict(DagETL)
    elif self.level == 'external_point_type':
        self.__import_dict(ExternalPointType)
    elif self.level == 'external_point':
        self.__import_dict(ExternalPoint)
    elif self.level == 'dlk_schema':
        self.__import_dict(DlkSchema)
    elif self.level == 'dlk_layer':
        self.__import_dict(DlkLayer)
    elif self.level == 'rule_type':
        self.__import_dict(RuleType)
    elif self.level == 'table_references':
        self.__import_dict(TableReferences)
```

## после (ЦС = 1)
```python
# решение: избавился от условных операторов c помощью создания словаря
def _import_dict2(self) -> None:

    level_dict = {
        'system': Dataset,
        'dataset': Dataset,
        'chkpt_rule': ChkptRule,
        'dag_etl': DagETL,
        'external_point_type': ExternalPointType,
        'external_point': ExternalPoint,
        'dlk_schema': DlkSchema,
        'dlk_layer': DlkLayer,
        'rule_type': RuleType,
        'table_references': TableReferences
    }
    self.__import_dict(level_dict.get(self.level))
```