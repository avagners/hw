# **Fuzz-тестирование с atheris**

Знакомство с fuzz-тестированием оказалось сложным и трудозатратным.  
Так как я пишу на Python было решено найти фаззер для этого языка.  
  
Поисковик предложил **Atheris** от google.  
Первые трудности были связаны с установкой фаззера на рабочий MacBook (хотел протестировать рабочий код).  
  
Для установки требуется полноценный Clang, который содержит **libFuzzer** (как понял на Mac стоит урезанная версия Apple Clang).  
Для решения данного вопроса потребовалось установить **LLVM**. Установить с первого раза не удалось. Потребовалось несколько вечеров, чтобы настроить окружение для установки **Atheris.**

Далее было довольно сложно разобраться как работает фаззер и как я могу протестировать какие-нибудь рабочие библиотеки.  
Подробных пошаговых гайдов с примерами крайне мало. Большинство ограничивается демонстрацией элементарного запуска фаззера без конкретного примера тестирования библиотеки. Также обратил внимание, что есть ряд репозиториев на GitHub, в которых тоже делают проверки с помощью **Atheris,** где прописан один тест-пустышка с комментарием, что фазз-тестирование у них только внедряется. =) Но коммит с данным комментарием добавлен несколько лет назад и более никаких изменений связанных с фазз-тестированием не вносилось.  
Также подавляющее большинство тестирует буквально один метод или функцию. За все время изучения нашел один довольно большой фазз-тест библиотеки из репозитория Samsung (он реально большой и сложный).  
  
За время поиска дополнительной информации нашел интересный репозиторий на GitHub [https://github.com/haydentherapper/oss-fuzz](https://github.com/haydentherapper/oss-fuzz)  
На июль 2022 года они нашли более 40 тысяч багов в 650 open source проектах. Впечатляет.  
  
Что пробовал:  
1) Сделать элементарный запуск на предмет генерации определенного слова фаззером.  
Работал около часа. Так и не дождался завершения (должен был сгенерировать ключевое слово и завершиться).  
Думал что я сделал что-то не так и нужно добавлять какие-то параметры для запуска. Например, пытался ограничить длину генерируемых входных данных с помощью **-max_len**. Не помогло. Прочитал где-то о том, что фазз-тестирование может быть длительной процедурой. Встречал рекомендации запускать тестирование на несколько часов или даже дней.  
  
2) Запустить пример из [https://github.com/haydentherapper/oss-fuzz](https://github.com/haydentherapper/oss-fuzz) с тестированием **airflow**.  
Не смог поднять докер-контейнер на рабочем ноутбуке из-за сетевых ограничений. Как обойти ограничение придумать пока не смог.  
  
3) Протестировать рабочие пакеты.  
Не хватает элементарного понимания как правильно писать функцию-обертку. Вроде делаю все по примеру, но фазз-тест падает на первом кейсе.  
  
4) Запустить фазз-тест пакета **jsonpickle** (тест взял из официального репозитория)  
Для того, чтобы хоть как-то познакомиться и выполнить успешное тестирование взял уже написанный тест пакета **jsonpickle**.
Тест длился очень долго - более 6-х часов. Дождаться завершения не смог - нужно было идти домой. =(
  
5) Запустить фазз-тест пакета **markdown-it-py 3.0.0** (тест взял из официального репозитория)  
Когда понял, что тест **jsonpickle** длится очень долго, решил параллельно запустить еще тест с надеждой, что один из них завершится успешно до конца рабочего дня. Но не свершилось. Тест длился более 4-х часов. Завершение теста дождаться не смог.
Как понял, если фазз-тестирование длится очень долго и не завершается с ошибками, то можно сделать вывод о том, что тест пройден успешно или криво написан тест.

## Итоги
Потратил на знакомство с данным видом тестирования довольно много времени. Понял что нужно глубже погружаться в тему и пробовать идти от простого к сложному. Нужно понимать что хочешь протестировать, и важно уметь пользоваться самим фаззером. За время, которое удалось уделить на эту тему, освоить **Atheris** так и не удалось.