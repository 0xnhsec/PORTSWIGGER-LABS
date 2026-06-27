# Business Logic Vulnerabilities — Dokumentasi Konsep

> Format: Penjelasan konsep + analogi + real world
> Tujuan: Paham WHY, bukan cuma HOW

---

## Apa itu Business Logic?

**Definisi simpel:**
> Business Logic = aturan cara kerja sebuah fitur aplikasi

Setiap aplikasi punya "aturan main" yang dibuat developer:
```
"Diskon hanya boleh dipakai sekali"
"Harga tidak boleh negatif"
"User harus konfirmasi sebelum bayar"
"Email harus diverifikasi sebelum dapat akses"
```

**Business Logic Vulnerability** = ketika aturan itu bisa di-abuse, di-bypass, atau di-manipulasi — bukan karena server-nya dibobol, tapi karena **logika aturannya cacat**.

---

## Perbedaan dengan Vuln Lain

```
XSS          = inject kode ke browser orang lain
BAC/IDOR     = akses resource yang bukan hak lo
SQLi         = inject query ke database
Business Logic = abuse cara kerja fitur yang LO BOLEH AKSES

Kunci: lo tidak "menerobos" — lo "memanfaatkan celah logika"
```

**Analogi kasir:**
```
SQLi         = lo hack sistem kasir
BAC          = lo masuk dapur yang harusnya staff only
Business Logic = lo bayar $10 tapi kasir salah kembalian $50
                 → lo tidak "hack" apapun, lo cuma manfaatin kesalahan prosedur
```

---

## Kenapa Susah Dideteksi?

```
XSS / SQLi  → ada pattern yang bisa di-scan otomatis
              scanner tahu payload-nya

Business Logic → tidak ada "payload" standar
                 setiap aplikasi punya logika berbeda
                 harus PAHAM flow aplikasi dulu
                 baru bisa abuse logikanya
```

Ini yang bikin business logic **high value di bug bounty** — scanner tidak bisa nemuin, cuma manual hunter yang paham flow.

---

## Kategori Business Logic Vulnerability

### 1. Trust Issues — Server Terlalu Percaya Client

```
Server seharusnya:
→ Validasi semua input di SERVER-SIDE
→ Tidak trust nilai yang dikirim client

Yang terjadi:
→ Harga di-trust dari request body (Lab 01)
→ Role di-trust dari cookie (BAC Lab 03)
→ Quantity negatif diterima (Lab 02)
```

**Pattern:**
```
Cari parameter yang seharusnya di-generate server,
tapi bisa lo manipulasi dari client:
price, discount, quantity, role, isAdmin, total
```

---

### 2. Assumption Errors — Developer Assume Terlalu Banyak

```
Developer assume:
"User pasti akan lewat step ini secara berurutan"
"User tidak akan input nilai negatif"
"User tidak akan pakai 2 coupon sekaligus"

Padahal:
HTTP stateless → tidak ada yang memaksa urutan
Attacker bisa kirim request apapun langsung
```

**Pattern:**
```
Cari flow yang punya urutan/step:
checkout → payment → confirm
register → verify → login

Test: skip step, ulangi step, balik ke step sebelumnya
```

---

### 3. Inconsistency — Validasi Tidak Konsisten

```
Registrasi: email diverifikasi ✅
Change email: email TIDAK diverifikasi ❌ (Lab 03)

POST /cart quantity=1: validasi ✅
POST /cart quantity=-99: tidak divalidasi ❌ (Lab 02)

Filter: replace('<') → hanya replace pertama ❌ (XSS Lab 13)
```

**Pattern:**
```
Temukan validasi di satu tempat
Test: apakah validasi yang sama ada di semua tempat terkait?
Change email / change password / change phone
```

---

### 4. Numeric Boundary Issues — Batas Angka Tidak Dihandle

```
Tidak ada batas minimum  → quantity negatif (Lab 02)
Tidak ada batas maksimum → integer overflow (Lab 05)
Tidak ada validasi range → discount 100% (API Lab 04)
```

**Test pattern:**
```
0, -1, -99999
99999, 2147483647 (max int32)
0.001, 99.99, 100.01
null, undefined, ""
```

---

### 5. State Machine Flaws — Kondisi Default Tidak Aman

```
Flow: login → role-selector → dashboard

Kalau role-selector di-skip:
→ Default role seharusnya: "user" (paling aman)
→ Bug: default role = "admin" (Lab 09)
```

**Pattern:**
```
Interrupt flow di tengah-tengah:
- Drop request (Burp intercept)
- Navigasi langsung ke URL tujuan
- Close browser di tengah flow
Cek apa yang terjadi dengan state aplikasi
```

---

### 6. Circular Logic — Siklus yang Bisa Di-profit

```
Beli gift card $10 dengan diskon 30% = bayar $7
Redeem gift card = dapat $10
Net profit: +$3 per siklus (Lab 10)

Cashback + purchase + refund:
Beli → dapat cashback → refund → cashback tidak di-revoke
```

**Pattern:**
```
Cari kombinasi fitur yang bisa menghasilkan:
- Net positive monetary value
- Free items
- Infinite credits/points
```

---

## Mental Model untuk Hunting Business Logic

### Step 1: Pahami Flow Normal

```
Browse aplikasi seperti user biasa
Catat semua "aturan" yang terlihat:
- "Coupon hanya berlaku sekali"
- "Minimum order $50 untuk free shipping"
- "Verifikasi email untuk akses fitur X"
- "Step 1 harus selesai sebelum Step 2"
```

### Step 2: Pertanyakan Setiap Aturan

```
Untuk setiap aturan yang lo temukan, tanya:
"Bagaimana kalau saya..."
→ ...input nilai di luar yang diharapkan?
→ ...skip step ini?
→ ...ulangi step ini berkali-kali?
→ ...lakukan di urutan berbeda?
→ ...lakukan dari dua akun bersamaan?
→ ...manipulasi parameter yang harusnya server yang set?
```

### Step 3: Test Batas

```
Setiap angka → test ekstrem (0, negatif, sangat besar)
Setiap flow → test skip dan repeat
Setiap validasi → test apakah ada di semua endpoint terkait
Setiap field → test apakah bisa di-inject dari client
```

---

## Contoh Real World — Ecommerce

### Fitur yang sering vulnerable:

```
Coupon/Voucher:
→ Bisa dipakai berkali-kali?
→ Bisa alternating 2 coupon?
→ Bisa dipakai setelah expired?
→ Bisa dipakai di akun berbeda tapi referral sama?

Checkout:
→ Bisa manipulasi harga di request?
→ Bisa skip payment step?
→ Bisa replay order confirmation?
→ Bisa tambah item setelah harga terkunci?

Refund:
→ Refund tanpa return item?
→ Refund lebih dari harga beli (karena diskon)?
→ Refund ke method berbeda?

Cashback/Points:
→ Dapat cashback → refund → cashback tidak hilang?
→ Points bisa di-transfer ke akun sendiri lalu refund?

Referral:
→ Refer diri sendiri dengan email berbeda?
→ Refer → dapat bonus → akun referee dihapus → bonus tetap ada?
```

---

## Tabel Lab vs Kategori

| Lab | Kategori | Inti Bug |
|---|---|---|
| 01 | Trust Issues | Server trust `price` dari client |
| 02 | Assumption Error | Assume quantity selalu positif |
| 03 | Inconsistency | Verify saat register, tidak saat change |
| 04 | Assumption Error | Assume coupon tidak bisa alternate |
| 05 | Numeric Boundary | Tidak handle integer overflow |
| 06 | Inconsistency | Validate before truncation, not after |
| 07 | Assumption Error | Assume `current-password` selalu ada |
| 08 | Assumption Error | Assume urutan step pasti diikuti |
| 09 | State Machine | Default state = admin (seharusnya user) |
| 10 | Circular Logic | Siklus gift card profit |
| 11 | Trust Issues | Expose encrypt/decrypt ke user |

---

## Satu Kalimat untuk Hafalan

> **Business Logic = developer punya aturan, lo cari celah di aturan itu**

Bukan soal inject payload — soal **berpikir seperti developer yang salah desain**, lalu **bertindak seperti user yang mau abuse sistem**.

---

## Next Labs yang Akan Lo Temukan Pattern Ini

```
CSRF    → abuse flow request yang legitimate
OAuth   → abuse trust antara dua sistem
Race Conditions → abuse TIMING di antara logika yang valid
```

Semuanya variasi dari business logic — "aturan ada, tapi ada celah di implementasinya."
