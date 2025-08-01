# Отказ от хранения логических значений в базе

## Пример 1. Система управления пользователями (авторизация/верификация email‑адреса)

Вместо поля `is_email_verified BOOL` можно завести `email_verified_at TIMESTAMP NULL`.

При верификации пользователем почты в это поле пишется время подтверждения, а до того значением остаётся `NULL`.

Это дает историю верификаций (например, если понадобится повторная верификация через какое‑то время) и упрощаете логику (нет флага + дополнительного поля для даты).

## Пример 2. Функционал «удаления» (soft delete) в CRM

Вместо `is_deleted BOOL` заводим `deleted_at TIMESTAMP NULL`.

При удалении записи ставим текущую дату; при восстановлении либо обнуляем, либо сохраняем историю удалений, если важны повторные удаления/восстановления.

Такой подход упрощает аудит: мы видим не только факт удаления, но и когда оно произошло, без дополнительных таблиц-логов.

## Пример 3. Активность подписки на рассылку

Заменяем флаг `is_subscribed` на два поля: `subscribed_at TIMESTAMP` и `unsubscribed_at TIMESTAMP`.

Это позволяет не только узнать текущее состояние, но и анализировать динамику подписок/отписок, строить отчёты и автоматизировать сегментацию.

---
## Выводы

Я всегда хранил булевые флаги, типа `is_active`, `is_verified` и так далее — казалось, это просто и понятно. Но теперь понял, что это довольно ограниченный подход.

Временные метки — это не просто "да/нет", а ещё и "когда". Это сразу даёт больше гибкости. Например, не просто "подписан", а "подписан вот тогда-то", что полезно и для аналитики, и для логов, и для автоматизации.

Это не усложнение, а наоборот — упрощение жизни. Условие вроде `subscribed_at IS NOT NULL AND unsubscribed_at IS NULL` читается нормально, а пользы — намного больше, чем от `is_subscribed`.

Буду стараться больше думать событиями, а не состояниями.