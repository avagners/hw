# Извлекаем пользу из сторонних зависимостей

### 1. MobX (mobx@6.15.0)

**Как используется в проекте:**

```typescript
import { action, computed, makeObservable, observable } from 'mobx';

export class UserStoreImpl implements UserStore {
    @observable parsedToken: KeycloakTokenParsed | null = null;
    @observable token: string | null = null;
    
    @computed get currentOwnerId(): string | null { ... }
    
    constructor() { makeObservable(this); }
    
    @action setParsedToken = (...) => { ... }
}
```

**Что узнал из исходников:**

- `observable` - это фабрика с разными вариантами: `observable.ref`, `observable.shallow`, `observable.struct` для разных стратегий наблюдения
- Декораторы `@observable`, `@action`, `@computed` - это аннотации, которые `makeObservable` регистрирует через систему `Annotation`
- MobX использует механизм `IObservable` с `observers_` (`Set<IDerivation>`) для отслеживания зависимостей
- Система batch (`startBatch`/`endBatch`) предотвращает лишние перерасчёты

**Как использовать эффективнее:**

- Использовать `observable.shallow` для больших массивов/объектов, где не нужна глубокая реактивность
- Понимать, что `makeObservable(this)` обязателен в конструкторе - без него декораторы не работают

---

### 2. styled-components (styled-components@6.1.8)

**Как используется в проекте:**

```typescript
import styled from 'styled-components';

export const AppWrapper = styled.div`
    background-color: #f6f6f6;
    display: flex;
    flex-direction: column;
    flex: 1;
`;
```

**Что узнал из исходников:**

- `styled` - это конструктор, созданный через `constructWithOptions`, который возвращает функцию с методами `.attrs()` и `.withConfig()`
- Каждый HTML-тег (`div`, `span`, `svg` и т.д.) - это отдельная типизированная версия `Styled<R, Target, OuterProps>`
- Система поддерживает `as`-проп для изменения целевого элемента через `AttrsTarget`
- Типы `IStyledComponent`, `ExecutionProps`, `Interpolation` обеспечивают строгую типизацию стилей

**Как использовать эффективнее:**

- Использовать `.attrs()` для передачи `defaultProps` вместо обёрток
- Использовать `.withConfig({ componentId: '...' })` для стабильных CSS-классов в тестах
- Понимать, что `styled(Component)` работает с любыми React-компонентами, не только DOM-элементами

---

### 3. Redux Toolkit (@reduxjs/toolkit@2.2.1)

**Что из исходников:**

- `createSlice` генерирует `action creators` и `case reducers` автоматически из объекта `reducers`
- Поддерживает `"builder notation"` через `builder.addCase().addMatcher().addDefaultCase()` для сложной логики
- `createAsyncThunk` интегрирован через `reducers: { fetchUsers: thunk(...) }` с автоматическими состояниями `pending/fulfilled/rejected`
- Система `InjectIntoConfig` позволяет ленивую загрузку слайсов через `combineSlices`

**Как использовать эффективнее:**

- Использовать `builder`-нотацию для сложной логики с matcher'ами
- Использовать `slice.getSelectors((state) => state.sliceName)` для глобальных селекторов
- Понимать, что `createSlice` использует `Immer` внутри - можно мутировать состояние напрямую

---

## Вывод

Изучение исходников показало, что все три библиотеки:

- **Имеют продуманную архитектуру** - аннотации в MobX, конструкторы в styled-components, builder pattern в RTK
- **Предоставляют больше возможностей**, чем используется в проекте
- **Написаны чище**, чем средний код приложения - стоит брать паттерны на вооружение

В итоге я могу использовать эти библиотеки более осознанно и эффективно.
