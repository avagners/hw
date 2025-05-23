# Неочевидные проектные ошибки (3)

## Пример 1: Внедрение микросервисной архитектуры вместо монолита

В одном из проектов, изначально построенном как монолитное приложение, возникли сложности с масштабируемостью и поддержкой. К коду имели доступ различные команды, которые создавали различные фичи для своих задач. Стали возникать регулярные падения всего сервиса, так как код, внесенный одной из команд, неочевидным образом оказывал разрушающее влияние на весь сервис. На поиски причин падений уходило много времени.

Было принято решение перейти на микросервисную архитектуру, где каждый компонент системы стал отдельным сервисом с чётко определённым интерфейсом взаимодействия.

Теперь каждый микросервис отвечает за свою зону ответственности и разрабатывается и разворачивается независимо от остальных. У каждой команды появился свой отдельный пакет.

Это позволило командам быстрее внедрять новые функции, уменьшить количество багов и упростить тестирование.

## Пример 2: Вынос валидации данных в отдельный модуль

В одном из проектов на прошлой работе, посвященном обработке данных, я заметил, что различные модули часто повторяют одну и ту же логику валидации данных. Эта валидация включала проверку на корректность формата, допустимые диапазоны значений и обязательные поля. Логика валидации была разбросана по коду, что затрудняло её поддержку и расширение. Любое изменение требований к валидации требовало поиска всех мест, где она применялась, и внесения изменений в каждом из них.

Чтобы улучшить дизайн, я предложил вынести всю логику валидации в отдельный модуль. Я создал отдельный модуль `validators.py`, где поместил универсальные функции валидации данных. Этот модуль стал центральным местом для всех проверок данных, предоставляя единый интерфейс для вызова функций валидации. Теперь каждый раз, когда нужно было проверить данные, достаточно было обратиться к этому модулю, что значительно упростило код и сделало его более читаемым и поддерживаемым.

Это изменение позволило избежать дублирования кода и упростило добавление новых правил валидации. Этот рефакторинг позволил значительно упростить код в других частях системы.

---
## Выводы

Для молодого разработчика страшно подниматься на уровень дизайна в действующем проекте с целью его рефакторинга. 
Порой даже мысли не возникает, что можно внести такие существенные изменения. 

Но бывают настолько очевидные ситуации, как в примерах выше. Не сделать рефакторинг на уровне дизайна гораздо сложнее, чем пытаться вносить изменения в текущий дизайн. 

Поэтому для себя я решил, что стоит не бояться подниматься на уровень дизайна и архитектуры во время своей работы с целью внести изменения, которые могут значительно улучшить работу всей системы.