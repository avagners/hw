# Что такое баг?

## 1. Это не баг
### Пример 1  

В веб-приложении кнопка меняет цвет с синего на зелёный при наведении курсора, хотя ожидается, что она должна оставаться синей. Технически это не баг, потому что поведение не нарушает функциональности системы, но выглядит нелогично с точки зрения дизайна.

### Пример 2  

В мобильном приложении пользователю нужно нажимать на кнопку «сохранить» два раза для завершения действия. Код работает как задумано, но дизайн делает это поведение раздражающим и неудобным для пользователя. Это проблема интерфейса, а не баг.

## 2. Это не баг (а что-то другое)  
### Пример 1  

В проекте используются устаревшие библиотеки с потенциальными уязвимостями, но они пока не вызывают проблем. Это не баг, а технический долг, который рано или поздно потребует устранения, чтобы избежать рисков безопасности.

### Пример 2  

Названия переменных в коде не следуют каким-либо соглашениям (например, переменные с однобуквенными именами), из-за чего код становится трудно читаемым. Это не ошибка, но плохая практика, которая усложняет поддержку проекта.

## 3. Это сбивает людей с толку
### Пример 1 

В коде логическая переменная isActive на самом деле означает, что объект деактивирован (false = активен). Это приводит к путанице при чтении кода, особенно для новых разработчиков.

### Пример 2  

В проекте используется необычный порядок аргументов функций, например, вместо привычного x, y используется y, x. Это сбивает разработчиков с толку при интеграции новых функций и легко приводит к ошибкам.

## 4. Это хрупкость
### Пример 1  

В старом коде веб-приложения постоянно используется глобальное состояние для хранения данных о сессии пользователя. Пока это работает, но внедрение новой функциональности или обновление архитектуры может легко привести к непредсказуемым сбоям из-за неявного изменения этого состояния.

### Пример 2  

В сложной системе расчетов есть зависимость от сторонней библиотеки, которая давно не обновлялась и может перестать работать в будущем при изменениях в операционной системе или среде исполнения.

## 5. Не соответствует требованиям OSHA
### Пример 1  

В коде сохраняются временные пароли для пользователей в виде незашифрованного текста. Работая с кодом, можно легко добавить новые места, где пароли сохраняются небезопасно, даже не осознавая, насколько это опасно.

### Пример 2  

Логика работы с правами доступа в системе неявная, и разработчики часто добавляют новые роли без должного понимания, как это может повлиять на безопасность системы, что создаёт риск уязвимостей в будущем.

---
## Выводы

После выполнения этого упражнения я понял, что ошибки в коде могут принимать различные формы и не всегда проявляются как баги, которые сразу видны или мешают работе системы. Часто проблемы могут быть не в неправильной работе программы, а в том, как код написан, насколько он понятен другим разработчикам и насколько он устойчив к будущим изменениям. Ошибки, которые не сразу проявляются, могут сделать код хрупким и затруднить его дальнейшую поддержку.