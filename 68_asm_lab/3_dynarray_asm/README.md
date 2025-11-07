# Dynamic Array Implementation in x86-64 Assembly

A complete implementation of a dynamic array (similar to Python list) in x86-64 assembly language using NASM.

## 🚀 Features

- **Dynamic resizing** - automatically grows when full
- **Basic operations** - append, insert, delete, get
- **Utility functions** - find, contains, reverse, sum, min/max
- **Memory management** - proper allocation and deallocation
- **Error handling** - bounds checking

## 🛠️ Requirements

- **NASM** (Netwide Assembler) - for assembling
- **GCC** or **LD** - for linking
- **Linux** x86-64 environment

### Installation on Ubuntu/Debian:
```bash
sudo apt update
sudo apt install nasm gcc
```

## Compile the assembly code and run
```bash
# Compile to object file
nasm -f elf64 src/dynarray.asm -o dynarray.o

# Link with gcc
gcc -no-pie dynarray.o -o dynarray

# Run
./dynarray
```

## Expected Output
```bash
DEBUG: DynArray created

=== APPEND 10 ===
Count: 1
Capacity: 4
[0] = 10

=== APPEND 20 ===
Count: 2
Capacity: 4
[0] = 10
[1] = 20

=== APPEND 30 ===
Count: 3
Capacity: 4
[0] = 10
[1] = 20
[2] = 30

=== APPEND 40 ===
Count: 4
Capacity: 4
[0] = 10
[1] = 20
[2] = 30
[3] = 40

=== APPEND 50 ===
*** RESIZE: capacity changed from 4 to 8 ***
Count: 5
Capacity: 8
[0] = 10
[1] = 20
[2] = 30
[3] = 40
[4] = 50

=== APPEND 60 ===
Count: 6
Capacity: 8
[0] = 10
[1] = 20
[2] = 30
[3] = 40
[4] = 50
[5] = 60

=== APPEND 70 ===
Count: 7
Capacity: 8
[0] = 10
[1] = 20
[2] = 30
[3] = 40
[4] = 50
[5] = 60
[6] = 70

=== APPEND 80 ===
Count: 8
Capacity: 8
[0] = 10
[1] = 20
[2] = 30
[3] = 40
[4] = 50
[5] = 60
[6] = 70
[7] = 80

=== APPEND 90 ===
*** RESIZE: capacity changed from 8 to 16 ***
Count: 9
Capacity: 16
[0] = 10
[1] = 20
[2] = 30
[3] = 40
[4] = 50
[5] = 60
[6] = 70
[7] = 80
[8] = 90

=== INSERT 35 at position 3 ===
Count: 10
Capacity: 16
[0] = 10
[1] = 20
[2] = 30
[3] = 35
[4] = 40
[5] = 50
[6] = 60
[7] = 70
[8] = 80
[9] = 90

=== INSERT 5 at position 0 ===
Count: 11
Capacity: 16
[0] = 5
[1] = 10
[2] = 20
[3] = 30
[4] = 35
[5] = 40
[6] = 50
[7] = 60
[8] = 70
[9] = 80
[10] = 90

=== DELETE element at position 5 ===
Count: 10
Capacity: 16
[0] = 5
[1] = 10
[2] = 20
[3] = 30
[4] = 35
[5] = 50
[6] = 60
[7] = 70
[8] = 80
[9] = 90

=== DELETE element at position 0 ===
Count: 9
Capacity: 16
[0] = 10
[1] = 20
[2] = 30
[3] = 35
[4] = 50
[5] = 60
[6] = 70
[7] = 80
[8] = 90

=== DELETE element at position 8 ===
Count: 8
Capacity: 16
[0] = 10
[1] = 20
[2] = 30
[3] = 35
[4] = 50
[5] = 60
[6] = 70
[7] = 80

Element 35 found at position 3
Array contains 60: YES
Sum of elements: 355
Maximum element: 80
Minimum element: 10
Array reversed
Count: 8
Capacity: 16
[0] = 80
[1] = 70
[2] = 60
[3] = 50
[4] = 35
[5] = 30
[6] = 20
[7] = 10

Array cleared
Count: 0
Capacity: 16
Array is empty
```

## Testing
The program includes comprehensive tests that demonstrate:
- Array expansion (capacity increases from 4 → 8 → 16)
- Insert operations with element shifting
- Delete operations with element shifting
- Search and utility functions
- Memory management

## Key Functions
`dyn_array_append` - Add element to end
`dyn_array_insert` - Insert at specific position
`dyn_array_delete` - Remove from position
`dyn_array_get` - Get element by index
`dyn_array_resize` - Internal resize function
`dyn_array_find` - Search for element
`dyn_array_reverse` - Reverse array order