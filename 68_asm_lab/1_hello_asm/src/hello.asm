section .data
    message db 'Hello, World!', 0xA  ; Сообщение для вывода
    message_length equ $ - message   ; Длина сообщения

section .text
    global _start

_start:
    ; Системный вызов для записи (write)
    mov rax, 1          ; Номер системного вызова для write в x86-64
    mov rdi, 1          ; Дескриптор файла для stdout
    mov rsi, message    ; Указатель на строку для вывода
    mov rdx, message_length  ; Длина строки
    syscall             ; Вызов ядра (в x86-64 используется syscall вместо int 0x80)

    ; Системный вызов для выхода (exit)
    mov rax, 60         ; Номер системного вызова для exit в x86-64
    xor rdi, rdi        ; Код возврата 0
    syscall             ; Вызов ядра