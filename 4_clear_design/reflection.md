# Увидеть ясную структуру дизайна

1) Пример 1  

Код, который был написан 5 месяцев назад. В классе реализована логика по "протяжке" данных на HDFS.  

В случае отсутствия партиции за определенный период по какой-либо причине, например, данные не были доступны на источнике, иногда требуется заполнить пробелы последней партицией.  

Нужно было реализовать:
- Копирование файлов на HDFS;
- Обновление метаданных в Hive;
- Обновление статистики Hive;
- Отправка статуса в Vita;
- Откат всех изменений в случае неудачи;

В рамках задания создал АТД, в котором описал требуемые методы для выполнения задачи с пред- и пост- условиями (описал дизайн).

До проделанной работы:
- не видно дизайн (структуры);
- все методы выглядят равноправными;
- не видно главную логику;
- нужно читать все методы, чтобы понять что происходит;
- нет пред- и пост- условий;

После: 
- видно дизайн (структуру);
- видна главная логика;
- методы разделены на основные и вспомогательные;
- есть пред- и пост- условия;

Сначала казалось, что данный пример не подходит. Думал, что здесь и так довольно хорошо видно структуру, плюс есть довольно подробный docstring. Но когда начал выполнять работу по созданию АТД, то понял свою ошибку. Работу можно было выполнить гораздо лучше. Например, после написания пред- и пост- условий в методе `copy_partition` напрашивается реализовать проверку наличия партиции на HDFS внутри метода (а не в методе "execute" сразу по всем новым партициям.)

Могу сказать однозначно, что после проделанной работы скорость и легкость понимания кода возрастает в разы (представлял себя на месте человека, который код будет смотреть впервые)). 

Много раз сталкивался с кодом, который сложно понять (хорошо, если есть какие-то комментарии). На понимание логики требуется очень много времени и сил. Нет уверенности, что реализация выполнена верно. Мне кажется это очень актуально во время ревью чужого кода - без АТД, без пред- и пост- условий, без написанных тестов крайне трудозатратно разобраться что вообще происходит (особенно если MR объемный). Время на ревью можно значительно сократить, если все будут практиковать написание АТД с указанием пред- и пост- условий, так как благодаря этому будет ясно видно структуру дизайна.

Так как код был мне хорошо знаком, то именно на выполнение задания ушло около 1,5 часов. Значительно больше времени потратил на поиск примера.

2) Пример 2

Небольшой класс по работе с API Gitlab для получения определенного набора данных из коммитов в репозиториях проекта.

Нужно было реализовать:
- получение всех данных по проектам в группе;
- получение всех данных по коммитам в проекте за период;
- парсинг необходимых данных из коммитов проекта;
- получение итогового набора данных по всем проектам;

После словесного описания логического дизайна напрашивается вынесение методов по получению кастомного набора данных в отдельный класс.
Если этого не сделать, то в будущем каждое добавление нового метода по сбору кастомного набора данных будет сильно запутывать этот класс. Таким образом получается иерархия классов `AbsGitlabSession -> GitlabSession -> AbsParser -> SomeParser`.

В АТД `AbsGitlabSession` описан дизайн работы с API. В классе GitlabSession выполнена реализация этого дизайна. Методы `parse_data` и `get_data` реализуют получение кастомного набора данных, который потребуется в разных задачах. Выносим их в дочерние классы (возможно, здесь лучше использовать композицию?). Создал АТД Parser, в котором описан дизайн парсера.

Таким образом мы обеспечиваем будущее безболезненное расширение класса `GitlabSession`, набором стандартных методов по работе с API (без внесения кастомной логики). АТД `Parser` и создаваемые дочерние классы-парсеры отделяют кастомную логику работы с полученными данными. Получение "сырых" данных теперь никак не связан с последующими операциями над ними. Получится универсальный модуль для работы с API Gitlab, который могут использовать и безболезненно расширять стандартными методами разные люди (сейчас же в кодовой базе я нашел несколько реализаций этого класса, которые создавались под узкие задачи - то есть присутствует дублирование кода). Проведение ревью будет значительно легче по сравнению с вариантом, когда есть один класс, который объединяет стандартные и кастомные методы.

На выполнение задания ушло около 3-х часов.

---
#### Итого:  
Задание для меня сначала показалось безумно сложным. Из-за нехватки практики программирования я думал, что у меня нет примеров, на которых мог бы его выполнить. Но даже на этих примерах увидел то, на что раньше не обращал никакого внимания. Точнее не мог этого увидеть (не умел). Во время словесного описания логической структуры дизайна практически сразу увидел минусы текущей реализации (особенно это ярко видно во 2-м примере). Напрашивается реализация дизайна, которая будет в будущем расширяема, при этом сложность понимания кода остается линейна.  

`До` - не задумываясь о дизайне, я просто последовательно реализовывал логику решения конкретной задачи.  

`После` - появились способности выделить главное, разделить универсальные методы от кастомных, главные от вспомогательных, предложить некоторую архитектуру. И главное думать о том, чтобы "дизайн был достаточно явно заметен и наглядно понятен".