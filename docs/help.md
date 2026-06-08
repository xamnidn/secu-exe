# SECU Help — Panduan Pengguna

## Cara Kerja

SECU adalah **deterministic password generator** — password yang sama selalu
dihasilkan dari input yang sama. Tidak ada password yang disimpan; semua
dihitung ulang setiap kali Anda menekan **Generate**.

### Alur Derivation

```
Master Password + Service Name + Version + [Device ID]
        │
        ▼
    ServiceNormalizer (NFC + lowercase + : guard)
        │
        ▼
    Salt: v1.3.0:{device}:{service}:{version}
        │
        ▼
    Argon2id(master, salt, time=3, mem=65536 KB, par=4)
        │
        ▼
    32-byte hash → SHA-256 expansion + rejection sampling
        │
        ▼
    Final password
```

### Komponen Input

| Input | Deskripsi |
|-------|-----------|
| **Master Password** | Frasa rahasia Anda. Jangan pernah membagikannya. |
| **Service / Website** | Nama unik untuk setiap layanan (mis. `google.com`). |
| **VER (Rotation Version)** | Naikkan angka ini saat sebuah situs memaksa Anda ganti password. |
| **Bind to Device** | Centang untuk mengikat password ke mesin tertentu. |

## Format Salt

Salt adalah fondasi determinisme SECU. Formatnya:

```
Portable:     v1.3.0::{service}:{version}
Device-bound: v1.3.0:{device_id}:{service}:{version}
```

**Peringatan:** Salt yang berbeda → password yang berbeda. Jika format salt
berubah, semua password yang ada akan **tidak bisa** diregenerasi.

## Device Bind

Saat **Bind to Device** aktif, SECU menyertakan `device_id` (64-char hex,
tersimpan lokal di `%APPDATA%/secu/device.json`) ke dalam salt. Password
hanya bisa diregenerasi di mesin yang sama.

Matikan untuk mode portabel — password bisa dihasilkan ulang di perangkat
mana pun selama master password dan service name sama.

## Karakter Parameters

| Opsi | Karakter |
|------|----------|
| A-Z Uppercase | `ABCDEFGHIJKLMNOPQRSTUVWXYZ` |
| a-z Lowercase | `abcdefghijklmnopqrstuvwxyz` |
| 0-9 Numbers | `0123456789` |
| Symbols | `!@#$%^&*()_+-=[]{}|;:,.<>?/~` |

Total charset maksimum: **90 karakter**.

## Rotasi Password

Jika sebuah situs meminta Anda mengubah password:
1. Naikkan **VER** (Version) sebesar 1.
2. Generate ulang.
3. Update password di situs tersebut.

Version sebelumnya tetap bisa digunakan untuk login lama (jika situs
menyimpan riwayat password).

## Keamanan Clipboard

- Password otomatis terhapus dari clipboard setelah **10 detik**.
- Clipboard ditimpa dengan data acak (48 byte) setelah masa berlaku habis.
- Jika Anda tidak menekan COPY, clipboard **tidak** akan disentuh.

## Parameter Kriptografi

| Parameter | Nilai |
|-----------|-------|
| Algoritma | Argon2id |
| Time cost | 3 iterasi |
| Memory cost | 64 MB (fixed) |
| Parallelism | 4 thread |
| Hash length | 32 bytes (256-bit) |
| Ekspansi | SHA-256 + rejection sampling |

## Tips Penggunaan

1. **Master password yang kuat** — gunakan frasa acak, minimal 4 kata.
2. **Service name yang konsisten** — selalu gunakan domain yang sama
   (mis. selalu `google.com`, bukan kadang `Google` kadang `google`).
3. **Backup device_id** — jika mengaktifkan Device Bind, backup file
   `device.json` Anda.
4. **Tidak ada koneksi jaringan** — SECU bekerja 100% offline.

## FAQ

**Q: Apa yang terjadi jika saya lupa master password?**  
A: Password tidak bisa dipulihkan. Tidak ada server, tidak ada backdoor.
Buat master password yang mudah diingat tapi sulit ditebak.

**Q: Apaman password saya aman di clipboard?**  
A: Clipboard otomatis dibersihkan setelah 10 detik. Namun, aplikasi lain
yang berjalan di sistem yang sama tetap bisa membaca clipboard selama
periode tersebut.

**Q: Apa bedanya VER dengan version aplikasi?**  
A: VER adalah nomor rotasi per-service, bukan versi aplikasi. Gunakan
untuk merotasi password satu layanan tanpa memengaruhi yang lain.

**Q: Bagaimana cara migrasi ke perangkat baru?**  
A: Untuk mode portable, cukup ingat master password dan service name.
Untuk mode device-bound, salin file `device.json` ke perangkat baru.
