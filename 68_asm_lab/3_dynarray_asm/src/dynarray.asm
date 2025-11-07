section .data
    ; Сообщения для отладки
    debug_created db "DEBUG: DynArray created", 10, 0
    debug_append db "=== APPEND %d ===", 10, 0
    debug_insert db "=== INSERT %d at position %d ===", 10, 0
    debug_delete db "=== DELETE element at position %d ===", 10, 0
    debug_count db "Count: %d", 10, 0
    debug_capacity db "Capacity: %d", 10, 0
    debug_element db "[%d] = %d", 10, 0
    debug_error db "DEBUG: Error occurred", 10, 0
    debug_empty db "Array is empty", 10, 0
    debug_found db "Element %d found at position %d", 10, 0
    debug_not_found db "Element %d not found", 10, 0
    debug_cleared db "Array cleared", 10, 0
    debug_reversed db "Array reversed", 10, 0
    debug_sum db "Sum of elements: %d", 10, 0
    debug_max db "Maximum element: %d", 10, 0
    debug_min db "Minimum element: %d", 10, 0
    debug_contains_yes db "Array contains %d: YES", 10, 0
    debug_contains_no db "Array contains %d: NO", 10, 0
    debug_resize db "*** RESIZE: capacity changed from %d to %d ***", 10, 0
    newline db 10, 0
    
    ; Константы - УМЕНЬШЕННЫЙ РАЗМЕР для демонстрации расширения
    INITIAL_CAPACITY equ 4

section .bss
    ; Глобальная переменная для нашего массива
    dyn_array resq 1

section .text
    global main
    extern malloc, free, printf

; ==================== ФУНКЦИЯ ИЗМЕНЕНИЯ РАЗМЕРА МАССИВА ====================
dyn_array_resize:
    push rbp
    mov rbp, rsp
    push r12
    push r13
    push r14
    push r15
    
    mov r12, rdi                ; указатель на DynArray
    mov r13, rsi                ; новое capacity
    
    ; Сохраняем старый capacity для отладки
    mov r14, [r12 + 8]          ; старый capacity
    
    ; Выделяем память для нового массива
    mov rdi, r13
    shl rdi, 3                  ; умножаем на 8 (размер указателя)
    call malloc
    test rax, rax
    jz .resize_error
    
    mov r15, rax                ; новый массив
    
    ; Копируем элементы из старого массива в новый
    mov rcx, [r12]              ; count
    test rcx, rcx
    jz .copy_done               ; если массив пустой, пропускаем копирование
    
    mov rsi, [r12 + 16]         ; старый массив
    xor r8, r8                  ; индекс

.copy_loop:
    cmp r8, rcx
    jge .copy_done
    
    mov r9, [rsi + r8*8]        ; элемент из старого массива
    mov [r15 + r8*8], r9        ; копируем в новый массив
    inc r8
    jmp .copy_loop

.copy_done:
    ; Освобождаем старый массив
    mov rdi, [r12 + 16]
    call free
    
    ; Обновляем указатель на массив и capacity
    mov [r12 + 16], r15
    mov [r12 + 8], r13
    
    ; Отладочная печать изменения capacity
    mov rdi, debug_resize
    mov rsi, r14                ; старое capacity
    mov rdx, r13                ; новое capacity
    xor rax, rax
    call printf
    
    pop r15
    pop r14
    pop r13
    pop r12
    pop rbp
    ret

.resize_error:
    mov rdi, debug_error
    call printf
    pop r15
    pop r14
    pop r13
    pop r12
    pop rbp
    ret

; ==================== ДОБАВЛЕНИЕ В КОНЕЦ ====================
dyn_array_append:
    push rbp
    mov rbp, rsp
    push rbx
    push r12
    push r13
    
    mov r12, rdi                ; указатель на DynArray
    mov r13, rsi                ; значение для добавления
    
    ; Получаем текущий count и capacity
    mov rbx, [r12]              ; count
    mov rax, [r12 + 8]          ; capacity
    
    ; Проверяем, нужно ли увеличивать capacity
    cmp rbx, rax
    jl .no_resize
    
    ; Увеличиваем capacity в 2 раза
    mov rsi, rax
    shl rsi, 1
    call dyn_array_resize

.no_resize:
    ; Добавляем элемент
    mov rax, [r12 + 16]         ; указатель на массив
    mov [rax + rbx*8], r13      ; array[count] = value
    
    ; Увеличиваем count
    inc qword [r12]
    
    pop r13
    pop r12
    pop rbx
    pop rbp
    ret

; ==================== ВСТАВКА ЭЛЕМЕНТА ====================
dyn_array_insert:
    push rbp
    mov rbp, rsp
    push rbx
    push r12
    push r13
    push r14
    push r15
    
    mov r12, rdi                ; указатель на DynArray
    mov r13, rsi                ; позиция для вставки
    mov r14, rdx                ; значение для вставки
    
    ; Проверка границ
    cmp r13, 0
    jl .error
    mov rax, [r12]              ; count
    cmp r13, rax
    jg .error
    
    ; Получаем текущий count и capacity
    mov rbx, [r12]              ; count
    mov rax, [r12 + 8]          ; capacity
    
    ; Проверяем, нужно ли увеличивать capacity
    cmp rbx, rax
    jl .no_resize
    
    ; Увеличиваем capacity в 2 раза
    mov rsi, rax
    shl rsi, 1
    call dyn_array_resize

.no_resize:
    ; Сдвигаем элементы вправо
    mov r15, [r12 + 16]         ; массив
    mov rcx, rbx                ; j = count (начинаем с конца)
    
.shift_loop:
    cmp rcx, r13
    jle .shift_done
    
    dec rcx
    mov rax, [r15 + rcx*8]      ; array[j]
    mov [r15 + rcx*8 + 8], rax  ; array[j+1] = array[j]
    jmp .shift_loop

.shift_done:
    ; Вставляем новый элемент
    mov [r15 + r13*8], r14
    
    ; Увеличиваем count
    inc qword [r12]
    
    pop r15
    pop r14
    pop r13
    pop r12
    pop rbx
    pop rbp
    ret

.error:
    mov rdi, debug_error
    call printf
    pop r15
    pop r14
    pop r13
    pop r12
    pop rbx
    pop rbp
    ret

; ==================== УДАЛЕНИЕ ЭЛЕМЕНТА ====================
dyn_array_delete:
    push rbp
    mov rbp, rsp
    push r12
    push r13
    push r14
    push r15
    
    mov r12, rdi                ; указатель на DynArray
    mov r13, rsi                ; позиция для удаления
    
    ; Проверка границ
    cmp r13, 0
    jl .error
    mov rax, [r12]              ; count
    cmp r13, rax
    jge .error
    
    ; Сдвигаем элементы влево
    mov r14, [r12 + 16]         ; массив
    mov r15, r13                ; j = pos
    
.shift_left_loop:
    mov rax, [r12]              ; count
    dec rax
    cmp r15, rax
    jge .shift_left_done
    
    mov rax, [r14 + r15*8 + 8]  ; array[j+1]
    mov [r14 + r15*8], rax      ; array[j] = array[j+1]
    
    inc r15
    jmp .shift_left_loop

.shift_left_done:
    ; Уменьшаем count
    dec qword [r12]
    
    pop r15
    pop r14
    pop r13
    pop r12
    pop rbp
    ret

.error:
    mov rdi, debug_error
    call printf
    pop r15
    pop r14
    pop r13
    pop r12
    pop rbp
    ret

; ==================== ПОИСК ЭЛЕМЕНТА ====================
; Вход: rdi = указатель на DynArray, rsi = значение для поиска
; Выход: rax = позиция или -1 если не найден
dyn_array_find:
    push rbp
    mov rbp, rsp
    push r12
    push r13
    push r14
    
    mov r12, rdi                ; указатель на DynArray
    mov r13, rsi                ; значение для поиска
    
    mov r14, [r12]              ; count
    test r14, r14
    jz .not_found
    
    mov rcx, [r12 + 16]         ; массив
    xor rax, rax                ; индекс

.search_loop:
    cmp rax, r14
    jge .not_found
    
    mov rdx, [rcx + rax*8]      ; текущий элемент
    cmp rdx, r13
    je .found
    
    inc rax
    jmp .search_loop

.found:
    pop r14
    pop r13
    pop r12
    pop rbp
    ret

.not_found:
    mov rax, -1
    pop r14
    pop r13
    pop r12
    pop rbp
    ret

; ==================== ПРОВЕРКА НАЛИЧИЯ ЭЛЕМЕНТА ====================
; Вход: rdi = указатель на DynArray, rsi = значение
; Выход: rax = 1 если есть, 0 если нет
dyn_array_contains:
    push rbp
    mov rbp, rsp
    
    call dyn_array_find
    cmp rax, -1
    je .not_contains
    
    mov rax, 1
    pop rbp
    ret

.not_contains:
    xor rax, rax
    pop rbp
    ret

; ==================== ОЧИСТКА МАССИВА ====================
dyn_array_clear:
    push rbp
    mov rbp, rsp
    
    mov qword [rdi], 0          ; count = 0
    
    pop rbp
    ret

; ==================== РЕВЕРС МАССИВА ====================
dyn_array_reverse:
    push rbp
    mov rbp, rsp
    push r12
    push r13
    push r14
    push r15
    
    mov r12, rdi
    mov r13, [r12]              ; count
    cmp r13, 1
    jle .reverse_done
    
    mov r14, [r12 + 16]         ; массив
    xor r15, r15                ; left index
    mov rcx, r13
    dec rcx                     ; right index

.reverse_loop:
    cmp r15, rcx
    jge .reverse_done
    
    ; Меняем местами array[left] и array[right]
    mov rax, [r14 + r15*8]      ; array[left]
    mov rdx, [r14 + rcx*8]      ; array[right]
    mov [r14 + r15*8], rdx
    mov [r14 + rcx*8], rax
    
    inc r15
    dec rcx
    jmp .reverse_loop

.reverse_done:
    pop r15
    pop r14
    pop r13
    pop r12
    pop rbp
    ret

; ==================== СУММА ЭЛЕМЕНТОВ ====================
dyn_array_sum:
    push rbp
    mov rbp, rsp
    push r12
    push r13
    push r14
    
    mov r12, rdi
    mov r13, [r12]              ; count
    test r13, r13
    jz .zero_sum
    
    mov r14, [r12 + 16]         ; массив
    xor rax, rax                ; сумма
    xor rcx, rcx                ; индекс

.sum_loop:
    add rax, [r14 + rcx*8]
    inc rcx
    cmp rcx, r13
    jl .sum_loop
    
    pop r14
    pop r13
    pop r12
    pop rbp
    ret

.zero_sum:
    xor rax, rax
    pop r14
    pop r13
    pop r12
    pop rbp
    ret

; ==================== МАКСИМАЛЬНЫЙ ЭЛЕМЕНТ ====================
dyn_array_max:
    push rbp
    mov rbp, rsp
    push r12
    push r13
    push r14
    
    mov r12, rdi
    mov r13, [r12]              ; count
    test r13, r13
    jz .error
    
    mov r14, [r12 + 16]         ; массив
    mov rax, [r14]              ; начальный максимум
    mov rcx, 1                  ; индекс

.max_loop:
    cmp rcx, r13
    jge .max_done
    
    mov rdx, [r14 + rcx*8]
    cmp rdx, rax
    jle .not_greater
    mov rax, rdx

.not_greater:
    inc rcx
    jmp .max_loop

.max_done:
    pop r14
    pop r13
    pop r12
    pop rbp
    ret

.error:
    xor rax, rax
    pop r14
    pop r13
    pop r12
    pop rbp
    ret

; ==================== МИНИМАЛЬНЫЙ ЭЛЕМЕНТ ====================
dyn_array_min:
    push rbp
    mov rbp, rsp
    push r12
    push r13
    push r14
    
    mov r12, rdi
    mov r13, [r12]              ; count
    test r13, r13
    jz .error
    
    mov r14, [r12 + 16]         ; массив
    mov rax, [r14]              ; начальный минимум
    mov rcx, 1                  ; индекс

.min_loop:
    cmp rcx, r13
    jge .min_done
    
    mov rdx, [r14 + rcx*8]
    cmp rdx, rax
    jge .not_less
    mov rax, rdx

.not_less:
    inc rcx
    jmp .min_loop

.min_done:
    pop r14
    pop r13
    pop r12
    pop rbp
    ret

.error:
    xor rax, rax
    pop r14
    pop r13
    pop r12
    pop rbp
    ret

; ==================== ПЕЧАТЬ ВСЕГО МАССИВА ====================
print_array:
    push rbp
    mov rbp, rsp
    push r12
    push r13
    push r14
    push r15
    
    mov r12, rdi                ; указатель на DynArray
    
    ; Печатаем count и capacity
    mov rdi, debug_count
    mov rsi, [r12]
    xor rax, rax
    call printf
    
    mov rdi, debug_capacity
    mov rsi, [r12 + 8]
    xor rax, rax
    call printf
    
    ; Получаем данные для печати
    mov r13, [r12]              ; count
    mov r14, [r12 + 16]         ; массив
    
    ; Проверяем, пуст ли массив
    cmp r13, 0
    je .empty_array
    
    xor r15, r15                ; индекс

.print_loop:
    cmp r15, r13
    jge .print_done
    
    ; Печатаем элемент
    mov rdi, debug_element
    mov rsi, r15                ; индекс
    mov rdx, [r14 + r15*8]      ; значение
    xor rax, rax
    call printf
    
    inc r15
    jmp .print_loop

.empty_array:
    mov rdi, debug_empty
    call printf

.print_done:
    mov rdi, newline
    call printf
    
    pop r15
    pop r14
    pop r13
    pop r12
    pop rbp
    ret

; ==================== ТЕСТИРОВАНИЕ С ПЕЧАТЬЮ ПОСЛЕ КАЖДОЙ ОПЕРАЦИИ ====================
main:
    push rbp
    mov rbp, rsp
    
    ; Выделяем память для структуры DynArray
    mov rdi, 24
    call malloc
    test rax, rax
    jz .main_error
    
    mov [dyn_array], rax        ; сохраняем указатель
    
    ; Инициализируем структуру вручную
    mov qword [rax], 0          ; count = 0
    mov qword [rax + 8], INITIAL_CAPACITY  ; capacity = 4
    
    ; Выделяем память для массива данных
    mov rdi, INITIAL_CAPACITY
    shl rdi, 3
    call malloc
    test rax, rax
    jz .main_error
    
    ; Сохраняем указатель на массив в структуре
    mov rcx, [dyn_array]
    mov [rcx + 16], rax
    
    mov rdi, debug_created
    call printf
    mov rdi, newline
    call printf
    
    ; ТЕСТ 1: Добавление элементов с печатью после каждой операции
    mov rdi, debug_append
    mov rsi, 10
    xor rax, rax
    call printf
    
    mov rdi, [dyn_array]
    mov rsi, 10
    call dyn_array_append
    mov rdi, [dyn_array]        ; ПЕЧАТЬ МАССИВА
    call print_array
    
    mov rdi, debug_append
    mov rsi, 20
    xor rax, rax
    call printf
    
    mov rdi, [dyn_array]
    mov rsi, 20
    call dyn_array_append
    mov rdi, [dyn_array]        ; ПЕЧАТЬ МАССИВА
    call print_array
    
    mov rdi, debug_append
    mov rsi, 30
    xor rax, rax
    call printf
    
    mov rdi, [dyn_array]
    mov rsi, 30
    call dyn_array_append
    mov rdi, [dyn_array]        ; ПЕЧАТЬ МАССИВА
    call print_array
    
    mov rdi, debug_append
    mov rsi, 40
    xor rax, rax
    call printf
    
    mov rdi, [dyn_array]
    mov rsi, 40
    call dyn_array_append
    mov rdi, [dyn_array]        ; ПЕЧАТЬ МАССИВА
    call print_array
    
    ; После 4-го элемента capacity должно увеличиться с 4 до 8
    mov rdi, debug_append
    mov rsi, 50
    xor rax, rax
    call printf
    
    mov rdi, [dyn_array]
    mov rsi, 50
    call dyn_array_append
    mov rdi, [dyn_array]        ; ПЕЧАТЬ МАССИВА
    call print_array
    
    ; Добавим еще, чтобы увидеть следующее расширение
    mov rdi, debug_append
    mov rsi, 60
    xor rax, rax
    call printf
    
    mov rdi, [dyn_array]
    mov rsi, 60
    call dyn_array_append
    mov rdi, [dyn_array]        ; ПЕЧАТЬ МАССИВА
    call print_array
    
    mov rdi, debug_append
    mov rsi, 70
    xor rax, rax
    call printf
    
    mov rdi, [dyn_array]
    mov rsi, 70
    call dyn_array_append
    mov rdi, [dyn_array]        ; ПЕЧАТЬ МАССИВА
    call print_array
    
    mov rdi, debug_append
    mov rsi, 80
    xor rax, rax
    call printf
    
    mov rdi, [dyn_array]
    mov rsi, 80
    call dyn_array_append
    mov rdi, [dyn_array]        ; ПЕЧАТЬ МАССИВА
    call print_array
    
    ; После 8-го элемента capacity должно увеличиться с 8 до 16
    mov rdi, debug_append
    mov rsi, 90
    xor rax, rax
    call printf
    
    mov rdi, [dyn_array]
    mov rsi, 90
    call dyn_array_append
    mov rdi, [dyn_array]        ; ПЕЧАТЬ МАССИВА
    call print_array
    
    ; Остальные тесты...
    ; ТЕСТ 2: Вставка элемента в середину с печатью
    mov rdi, debug_insert
    mov rsi, 35
    mov rdx, 3
    xor rax, rax
    call printf
    
    mov rdi, [dyn_array]
    mov rsi, 3                  ; позиция
    mov rdx, 35                 ; значение
    call dyn_array_insert
    mov rdi, [dyn_array]        ; ПЕЧАТЬ МАССИВА
    call print_array
    
    ; ТЕСТ 3: Вставка элемента в начало с печатью
    mov rdi, debug_insert
    mov rsi, 5
    mov rdx, 0
    xor rax, rax
    call printf
    
    mov rdi, [dyn_array]
    mov rsi, 0                  ; позиция
    mov rdx, 5                  ; значение
    call dyn_array_insert
    mov rdi, [dyn_array]        ; ПЕЧАТЬ МАССИВА
    call print_array
    
    ; ТЕСТ 4: Удаление элемента из середины с печатью
    mov rdi, debug_delete
    mov rsi, 5
    xor rax, rax
    call printf
    
    mov rdi, [dyn_array]
    mov rsi, 5                  ; позиция
    call dyn_array_delete
    mov rdi, [dyn_array]        ; ПЕЧАТЬ МАССИВА
    call print_array
    
    ; ТЕСТ 5: Удаление элемента из начала с печатью
    mov rdi, debug_delete
    mov rsi, 0
    xor rax, rax
    call printf
    
    mov rdi, [dyn_array]
    mov rsi, 0                  ; позиция
    call dyn_array_delete
    mov rdi, [dyn_array]        ; ПЕЧАТЬ МАССИВА
    call print_array
    
    ; ТЕСТ 6: Удаление элемента из конца с печатью
    mov rdi, debug_delete
    mov rsi, 8
    xor rax, rax
    call printf
    
    mov rdi, [dyn_array]
    mov rsi, 8                  ; позиция (последний элемент)
    call dyn_array_delete
    mov rdi, [dyn_array]        ; ПЕЧАТЬ МАССИВА
    call print_array
    
    ; ТЕСТ 7: Поиск элементов
    mov rdi, [dyn_array]
    mov rsi, 35
    call dyn_array_find
    cmp rax, -1
    je .not_found_35
    mov rdi, debug_found
    mov rsi, 35
    mov rdx, rax
    xor rax, rax
    call printf
    jmp .test_contains
.not_found_35:
    mov rdi, debug_not_found
    mov rsi, 35
    xor rax, rax
    call printf

.test_contains:
    ; ТЕСТ 8: Проверка наличия элементов
    mov rdi, [dyn_array]
    mov rsi, 60
    call dyn_array_contains
    test rax, rax
    jz .contains_no_60
    mov rdi, debug_contains_yes
    mov rsi, 60
    xor rax, rax
    call printf
    jmp .test_sum
.contains_no_60:
    mov rdi, debug_contains_no
    mov rsi, 60
    xor rax, rax
    call printf

.test_sum:
    ; ТЕСТ 9: Сумма элементов
    mov rdi, [dyn_array]
    call dyn_array_sum
    mov rdi, debug_sum
    mov rsi, rax
    xor rax, rax
    call printf

.test_max_min:
    ; ТЕСТ 10: Максимальный и минимальный элементы
    mov rdi, [dyn_array]
    call dyn_array_max
    mov rdi, debug_max
    mov rsi, rax
    xor rax, rax
    call printf
    
    mov rdi, [dyn_array]
    call dyn_array_min
    mov rdi, debug_min
    mov rsi, rax
    xor rax, rax
    call printf

.test_reverse:
    ; ТЕСТ 11: Реверс массива
    mov rdi, debug_reversed
    call printf
    mov rdi, [dyn_array]
    call dyn_array_reverse
    mov rdi, [dyn_array]        ; ПЕЧАТЬ МАССИВА
    call print_array

.test_clear:
    ; ТЕСТ 12: Очистка массива
    mov rdi, debug_cleared
    call printf
    mov rdi, [dyn_array]
    call dyn_array_clear
    mov rdi, [dyn_array]        ; ПЕЧАТЬ МАССИВА
    call print_array
    
    ; Освобождаем память
    mov rcx, [dyn_array]
    mov rdi, [rcx + 16]         ; освобождаем массив данных
    call free
    
    mov rdi, [dyn_array]        ; освобождаем структуру
    call free
    
    ; Успешное завершение
    mov rax, 60
    mov rdi, 0
    syscall

.main_error:
    mov rdi, debug_error
    call printf
    mov rax, 60
    mov rdi, 1
    syscall