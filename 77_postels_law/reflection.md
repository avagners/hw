# Ослабление предусловий и усиление постусловий

## 1. Функция extractEventKeys

### До
Функция жестко требовала полный объект ответа от API. Если структура была нарушена или передавался null, код мог упасть. Дубликаты ключей не фильтровались.
```typescript
// Предусловие: { subscriptionData - валидный объект ответа API }
export const extractEventKeys = (subscriptionData: GetSubscriptionResponse): EventKey[] => {
    const eventKeys: EventKey[] = [];

    if (subscriptionData?.data?.subscription?.eventAttrGroups) {
        subscriptionData.data.subscription.eventAttrGroups.forEach((attrGroup) => {
            if (attrGroup.attrs) {
                attrGroup.attrs.forEach((attr) => {
                    if (attr.name) {
                        eventKeys.push({ key: attr.name });
                    }
                });
            }
        });
    }

    return eventKeys;
};
// Постусловие: { возвращает массив ключей, возможны дубликаты }
```
### После
**Ослабление предусловия:**  
Функция теперь принимает не только полный ответ, но и просто объект подписки, или даже `null/undefined`.
**Усиление постусловия:**  
Гарантируется уникальность ключей (используется `Set`) и возврат пустого массива вместо ошибки при некорректных входных данных.
```typescript
// Предусловие: { data - ответ API, объект подписки или null/undefined }
export const extractEventKeys = (data: GetSubscriptionResponse | Subscription | null | undefined): EventKey[] => {
    const eventKeys: EventKey[] = [];
    let subscription: Subscription | undefined;

    if (!data) return [];

    // Определяем, что нам передали: полный ответ или только подписку
    if ('data' in data && data.data?.subscription) {
        subscription = data.data.subscription;
    } else if ('eventAttrGroups' in data) {
        subscription = data as Subscription;
    }

    if (subscription?.eventAttrGroups) {
        const seenKeys = new Set<string>(); // Усиление: гарантия уникальности
        subscription.eventAttrGroups.forEach((attrGroup) => {
            if (attrGroup.attrs) {
                attrGroup.attrs.forEach((attr) => {
                    if (attr.name && !seenKeys.has(attr.name)) {
                        eventKeys.push({ key: attr.name });
                        seenKeys.add(attr.name);
                    }
                });
            }
        });
    }

    return eventKeys;
};
// Постусловие: { возвращает массив УНИКАЛЬНЫХ ключей, пустой массив если данных нет }
```

## 2. Функция formatDate

### До
Ожидалась только строка. Если передавалась некорректная строка даты, результат мог быть `Invalid Date` или ошибка в рантайме.
```typescript
// Предусловие: { dateString - непустая строка с валидной датой }
export const formatDate = (dateString: string): string => {
    if (!dateString) return 'Не указана';
    const date = new Date(dateString);
    return date.toLocaleDateString('ru-RU', {
        year: 'numeric',
        month: 'long',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit',
    });
};
// Постусловие: { возвращает отформатированную строку даты, может вернуть "Invalid Date" если строка некорректна }
```

### После
**Ослабление предусловия:**  
Принимаем `string`, `Date`, `null` или `undefined`.
**Усиление постусловия:**  
Явная проверка на валидность даты (`isNaN`). Гарантированный возврат читаемой строки "Не указана" в случае любых проблем.

```typescript
// Предусловие: { date - строка, Date, null или undefined }
export const formatDate = (date: string | Date | null | undefined): string => {
    if (!date) return 'Не указана';
    
    const d = typeof date === 'string' ? new Date(date) : date;
    // Усиление: Проверка на валидность даты
    if (isNaN(d.getTime())) {
        return 'Не указана';
    }

    return d.toLocaleDateString('ru-RU', {
        year: 'numeric',
        month: 'long',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit',
    });
};
// Постусловие: { возвращает отформатированную строку даты или "Не указана", никогда не падает }
```

## 3. Функция `formatStatus`

### До
Типизация подразумевала строку, но не обрабатывала `null` явно (хотя JS это пропустит).

```typescript
// Предусловие: { status - строка }
export const formatStatus = (status: string): string => {
    const statusMap: Record<string, string> = {
        ACTIVE: 'Активна',
        // ...
    };

    return statusMap[status] || status;
};
// Постусловие: { возвращает русское название статуса или исходную строку }
```

### После
**Ослабление предусловия:**  
Явно разрешены `null` и `undefined`.
**Усиление постусловия:**  
Возврат дефолтного значения "Неизвестно" для пустых данных.

```typescript
// Предусловие: { status - строка, null или undefined }
export const formatStatus = (status: string | null | undefined): string => {
    if (!status) return 'Неизвестно';

    const statusMap: Record<string, string> = {
        ACTIVE: 'Активна',
        // ...
    };
    // ...
// Постусловие: { возвращает русское название статуса, исходную строку или "Неизвестно" }
```

## 4. Функция `isTextRequiredForBlockType`

### До
Рассчитана только на валидные значения enum.

```typescript
// Предусловие: { blockType - валидное значение из enum TEMPLATE_BLOCK_TYPES }
export const isTextRequiredForBlockType = (blockType: TEMPLATE_BLOCK_TYPES): boolean => {
    switch (blockType) {
        case TEMPLATE_BLOCK_TYPES.SIMPLE_TEXT:
            return true;
        // ...
        default:
            return true;
    }
};
// Постусловие: { возвращает boolean }
```

### После
**Ослабление предусловия:**  
Принимает `null` или `undefined`.
**Усиление постусловия:**  
Безопасный возврат `false` для отсутствующего типа и `true` по умолчанию для безопасности (лучше потребовать поле, чем пропустить обязательное).

```typescript
// Предусловие: { blockType - значение из enum, null или undefined }
export const isTextRequiredForBlockType = (blockType: TEMPLATE_BLOCK_TYPES | null | undefined): boolean => {
    if (!blockType) return false;

    switch (blockType) {
        // ... cases
        default:
            return true; // По умолчанию считаем обязательным для безопасности
    }
};
// Постусловие: { возвращает boolean, false для null/undefined, true для неизвестных типов (безопасность) }
```

## 5. Функция `isTitleRequiredForBlockType`

### До
Аналогично предыдущей, жесткая привязка к `enum`.

```typescript
// Предусловие: { blockType - валидное значение из enum TEMPLATE_BLOCK_TYPES }
export const isTitleRequiredForBlockType = (blockType: TEMPLATE_BLOCK_TYPES): boolean => {
    switch (blockType) {
        // ... cases
        default:
            return false;
    }
};
// Постусловие: { возвращает boolean }
```

### После
**Ослабление предусловия:**  
Принимает `null` или `undefined`.
**Усиление постусловия:**  
Гарантированный `false` при отсутствии типа.

```typescript
// Предусловие: { blockType - значение из enum, null или undefined }
export const isTitleRequiredForBlockType = (blockType: TEMPLATE_BLOCK_TYPES | null | undefined): boolean => {
    if (!blockType) return false;

    switch (blockType) {
        // ... cases
        default:
            return false;
    }
};
// Постусловие: { возвращает boolean, всегда false для null/undefined }
```

---

## Итоги

Честно говоря, раньше я думал о коде в основном в контексте "счастливого пути" (`happy path`). Пишешь функцию, ожидаешь, что в неё придут правильные данные, и она вернет правильный результат. Если приходил `null` или что-то не то, я просто надеялся, что `TypeScript` меня спасет или "ну или там выше по стеку разберутся".

Прочитав материал про спецификации и логику Хоара, я понял, что мой код был хрупким. Я неявно накладывал кучу ограничений на того, кто вызывает мои функции (предусловия), но при этом давал слабые гарантии того, что верну (постусловия).

Выполняя это упражнение, я увидел паттерн:
1.  Ослабление предусловий делает функцию "всеядной". Она перестает капризничать: "Ой, ты дал мне null, я падаю". Вместо этого она говорит: "Окей, данных нет? Я справлюсь". Это делает компоненты гораздо легче переиспользуемыми. Мне не нужно теперь 10 раз проверять данные перед вызовом `formatDate`, я просто кидаю в неё что есть, и она работает.
2.  Усиление постусловий дает мне уверенность. Я теперь точно знаю, что `extractEventKeys` вернет уникальные ключи. Мне не нужно делать `.filter` или `new Set` каждый раз, когда я использую результат этой функции. Я перенес сложность внутрь функции, сделав жизнь вызывающего кода проще.

Это меняет мышление с "как мне написать этот алгоритм" на "какой контракт эта функция заключает с остальной системой". Кажется, именно это отличает просто работающий код от надежного инженерного решения.