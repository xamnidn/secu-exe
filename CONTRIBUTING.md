# Contributing

## Folder Rules

- core/ → cryptography logic
- ui/ → interface layer
- utils/ → reusable utilities
- tests/ → automated testing

## Architectural Rules

- crypto layer tidak boleh import tkinter
- UI layer tidak boleh menyimpan secret
- master password tidak boleh disimpan sebagai atribut objek; known limitation: string tetap di heap hingga GC setelah thread Argon2 selesai
- semua clipboard abstraction berada di utils/platform.py
