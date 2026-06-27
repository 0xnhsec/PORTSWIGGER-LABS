source: https://portswigger.net/web-security/race-conditions
# Race Conditions (Kondisi Balapan)

Race conditions adalah jenis kerentanan umum yang berkaitan erat dengan celah logika bisnis (*business logic flaws*). Kerentanan ini terjadi ketika situs web memproses permintaan (*request*) secara konkuren (bersamaan) tanpa adanya pengamanan yang memadai. Hal ini dapat menyebabkan beberapa *thread* berinteraksi dengan data yang sama pada saat yang sama, menghasilkan "tabrakan" (*collision*) yang menyebabkan perilaku tidak terduga pada aplikasi. Serangan *race condition* menggunakan *request* yang diatur waktunya secara cermat untuk sengaja memicu tabrakan dan mengeksploitasi perilaku tidak terduga ini untuk tujuan berbahaya. 

Rentang waktu di mana tabrakan dapat terjadi dikenal sebagai "jendela balapan" (*race window*). Jendela ini bisa berupa sepersekian detik antara dua interaksi dengan database, sebagai contoh.

Seperti celah logika lainnya, dampak dari *race condition* sangat bergantung pada aplikasi dan fungsi spesifik tempat kerentanan tersebut terjadi.

Di bagian ini, Anda akan mempelajari cara mengidentifikasi dan mengeksploitasi berbagai jenis *race condition*. Kami akan mengajarkan cara menggunakan alat bawaan Burp Suite untuk mengatasi tantangan dalam melakukan serangan klasik, serta metodologi teruji yang memungkinkan Anda mendeteksi kelas baru *race condition* dalam proses tersembunyi multi-tahap (*hidden multi-step processes*). Hal ini melampaui batas *limit overrun* yang mungkin sudah Anda kenal sebelumnya. 

### Riset PortSwigger
Seperti biasa, kami juga menyediakan sejumlah lab yang sengaja dibuat rentan untuk melatih apa yang telah Anda pelajari secara aman pada target yang realistis. Banyak dari lab ini didasarkan pada riset asli PortSwigger yang pertama kali dipresentasikan di Black Hat USA 2023.

Untuk detail lebih lanjut, silakan baca artikel pendamping (*whitepaper*): [Smashing the state machine: The true potential of web race conditions](https://portswigger.net/research/smashing-the-state-machine)

---

## Limit Overrun Race Conditions (Kondisi Balapan Melampaui Batas)

Jenis *race condition* yang paling terkenal adalah yang memungkinkan Anda melampaui batas tertentu yang ditetapkan oleh logika bisnis aplikasi.

Sebagai contoh, bayangkan sebuah toko online yang memungkinkan Anda memasukkan kode promosi saat checkout untuk mendapatkan diskon sekali pakai pada pesanan Anda. Untuk menerapkan diskon ini, aplikasi mungkin melakukan langkah-langkah tingkat tinggi berikut:
1. Memeriksa apakah Anda sudah pernah menggunakan kode tersebut.
2. Menerapkan diskon ke total pesanan.
3. Memperbarui catatan di database untuk menandai bahwa kode tersebut telah digunakan.

Jika Anda mencoba menggunakan kembali kode tersebut nanti, pemeriksaan awal pada awal proses akan mencegah Anda melakukannya:

![[RaCo1.png]]

Sekarang bayangkan apa yang terjadi jika pengguna yang belum pernah menggunakan kode diskon ini mencoba menerapkannya dua kali pada waktu yang hampir bersamaan:

![[RaCo2.png]]

Seperti yang Anda lihat, aplikasi bertransisi melalui sub-status sementara; yaitu keadaan yang dimasuki lalu ditinggalkan kembali sebelum pemrosesan *request* selesai. Dalam hal ini, sub-status dimulai ketika server mulai memproses *request* pertama, dan berakhir ketika memperbarui database untuk menunjukkan bahwa Anda telah menggunakan kode ini. Hal ini memicu *race window* kecil di mana Anda dapat mengklaim diskon berulang kali sebanyak yang Anda inginkan.

Ada banyak variasi dari jenis serangan ini, antara lain:

- Menebus kartu hadiah (*gift card*) berkali-kali.
- Memberikan rating pada produk berkali-kali.
- Menarik atau mentransfer uang melebihi saldo akun Anda.
- Menggunakan kembali satu solusi CAPTCHA.
- Membypass batas laju anti-brute-force (*rate limit*).

*Limit overrun* adalah sub-tipe dari apa yang disebut celah "time-of-check to time-of-use" (TOCTOU). Nanti dalam topik ini, kita akan melihat beberapa contoh kerentanan *race condition* yang tidak termasuk dalam kedua kategori tersebut.

### Mendeteksi dan Mengeksploitasi Limit Overrun dengan Burp Repeater

Proses pendeteksian dan eksploitasi *limit overrun* relatif sederhana. Secara garis besar, yang perlu Anda lakukan adalah:

1. Identifikasi *endpoint* sekali pakai atau yang dibatasi lajunya yang memiliki dampak keamanan atau kegunaan lainnya.
2. Kirim beberapa *request* ke *endpoint* ini secara berurutan dengan cepat untuk melihat apakah Anda dapat melampaui batas tersebut.

Tantangan utamanya adalah menyinkronkan waktu *request* agar setidaknya dua *race window* sejajar dan menyebabkan tabrakan. Jendela ini seringkali hanya berlangsung beberapa milidetik bahkan bisa lebih pendek.

Bahkan jika Anda mengirim semua *request* pada saat yang persis sama, dalam praktiknya ada berbagai faktor eksternal yang tidak dapat dikendalikan dan diprediksi yang memengaruhi kapan server memproses setiap *request* dan dalam urutan apa.

![[RaCo3.png]]

[Burp Suite 2023.9](https://portswigger.net/burp/releases#professional) menambahkan kemampuan baru yang canggih ke Burp Repeater untuk mengirim sekelompok *request* secara paralel dengan cara meminimalkan dampak dari salah satu faktor tersebut, yaitu *network jitter* (fluktuasi latensi jaringan). Burp secara otomatis menyesuaikan teknik yang digunakannya agar sesuai dengan versi HTTP yang didukung oleh server:

- Untuk **HTTP/1**, ia menggunakan teknik sinkronisasi bita terakhir (*last-byte synchronization*).
- Untuk **HTTP/2**, ia menggunakan teknik serangan paket tunggal (*single-packet attack*), yang pertama kali didemonstrasikan oleh PortSwigger Research di Black Hat USA 2023.

Serangan paket tunggal (*single-packet attack*) memungkinkan Anda menetralkan interferensi dari *network jitter* sepenuhnya dengan menggunakan satu paket TCP untuk menyelesaikan 20-30 *request* secara bersamaan.

![[RacO4.png]]

Meskipun Anda seringkali hanya membutuhkan dua *request* untuk memicu eksploitasi, mengirimkan banyak *request* seperti ini membantu mengurangi latensi internal (disebut juga *server-side jitter*). Ini sangat berguna selama fase penemuan awal (*initial discovery*). Kita akan membahas metodologi ini secara lebih rinci.

#### Baca Lebih Lanjut

- Untuk detail tentang cara menggunakan fitur baru Burp Repeater untuk mengirim beberapa *request* secara paralel, lihat [Sending requests in parallel](https://portswigger.net/burp/documentation/desktop/tools/repeater/send-group#sending-requests-in-parallel).
- Untuk wawasan teknis tentang mekanisme dasar serangan paket tunggal dan metodologi yang lebih detail, baca artikel pendamping (*whitepaper*): [Smashing the state machine: The true potential of web race conditions](https://portswigger.net/research/smashing-the-state-machine)

### Mendeteksi dan Mengeksploitasi Limit Overrun dengan Turbo Intruder

Selain dukungan bawaan untuk *single-packet attack* di Burp Repeater, kami juga telah meningkatkan ekstensi Turbo Intruder untuk mendukung teknik ini. Anda dapat mengunduh versi terbaru dari [BApp Store](https://portswigger.net/bappstore/9abaa233088242e8be252cd4ff534988).

Turbo Intruder memerlukan keahlian dalam bahasa Python, tetapi sangat cocok untuk serangan yang lebih kompleks, seperti serangan yang membutuhkan beberapa kali percobaan ulang (*retries*), pengaturan waktu *request* yang bertahap, atau jumlah *request* yang sangat banyak.

Untuk menggunakan *single-packet attack* di Turbo Intruder:

1. Pastikan target mendukung HTTP/2. Serangan paket tunggal tidak kompatibel dengan HTTP/1.
2. Atur opsi konfigurasi engine ke `engine=Engine.BURP2` dan `concurrentConnections=1`.
3. Saat mengantrekan *request*, kelompokkan mereka dengan memasukkannya ke gerbang (*gate*) bernama menggunakan argumen `gate` pada metode `engine.queue()`.
4. Untuk mengirim semua *request* dalam grup tertentu, buka gerbang tersebut menggunakan metode `engine.openGate()`.

```python
def queueRequests(target, wordlists):
    engine = RequestEngine(
        endpoint=target.endpoint,
        concurrentConnections=1,
        engine=Engine.BURP2
    )
    
    # antrekan 20 request di gate '1'
    for i in range(20):
        engine.queue(target.req, gate='1')
        
    # kirim semua request di gate '1' secara paralel
    engine.openGate('1')
```

Untuk detail lebih lanjut, lihat templat `race-single-packet-attack.py` yang disediakan di direktori contoh bawaan Turbo Intruder.

---

## Hidden Multi-Step Sequences (Urutan Multi-Langkah Tersembunyi)

Dalam praktiknya, satu *request* dapat memicu seluruh urutan multi-langkah di balik layar, memindahkan aplikasi melalui beberapa status tersembunyi yang dimasuki lalu ditinggalkan sebelum pemrosesan *request* selesai. Kita akan menyebut status sementara ini sebagai "sub-status" (*sub-states*).

Jika Anda dapat mengidentifikasi satu atau beberapa *request* HTTP yang memicu interaksi dengan data yang sama, Anda dapat memanfaatkan sub-status ini untuk mengungkap variasi sensitif-waktu dari jenis celah logika yang umum terjadi pada alur kerja multi-langkah (*multi-step workflows*). Hal ini memungkinkan eksploitasi *race condition* yang jauh melampaui sekadar *limit overrun*.

Sebagai contoh, Anda mungkin sudah tidak asing lagi dengan alur kerja Multi-Factor Authentication (MFA) yang cacat yang memungkinkan Anda melakukan bagian pertama dari login menggunakan kredensial yang valid, lalu langsung menavigasi ke halaman dalam aplikasi via *forced browsing*, secara efektif membypass MFA sepenuhnya.

#### Catatan

Jika Anda belum terbiasa dengan eksploitasi ini, silakan coba lab *2FA simple bypass* di topik kerentanan Otentikasi (*Authentication vulnerabilities*).

Kode semu (*pseudo-code*) berikut menunjukkan bagaimana sebuah situs web dapat rentan terhadap variasi *race condition* dari serangan ini:

```python
session['userid'] = user.userid
if user.mfa_enabled:
    session['enforce_mfa'] = True
    # buat dan kirim kode MFA ke pengguna
    # arahkan browser ke formulir penginputan kode MFA
```

Seperti yang Anda lihat, ini sebenarnya adalah urutan multi-langkah dalam rentang pemrosesan satu *request*. Yang paling penting, sistem melewati sub-status di mana pengguna sementara memiliki sesi masuk (*logged-in*) yang valid, namun MFA belum diwajibkan (*enforced*). Penyerang dapat mengeksploitasi ini dengan mengirimkan *request* login bersamaan dengan *request* ke *endpoint* terotentikasi yang sensitif.

Kita akan melihat contoh lain dari urutan multi-langkah tersembunyi nanti, dan Anda akan dapat mempraktikkan eksploitasinya di lab interaktif kami. Namun, karena kerentanan ini sangat spesifik untuk tiap aplikasi, penting untuk memahami metodologi umum yang perlu diterapkan agar dapat mengidentifikasinya dengan efisien.

---

## Metodologi

Untuk mendeteksi dan mengeksploitasi urutan multi-langkah tersembunyi, kami merekomendasikan metodologi berikut, yang dirangkum dari *whitepaper* [Smashing the state machine: The true potential of web race conditions](https://portswigger.net/research/smashing-the-state-machine) oleh PortSwigger Research.

![[RaCo5.png]]

### 1 - Prediksi Potensi Tabrakan (Predict Potential Collisions)

Menguji setiap *endpoint* adalah hal yang tidak praktis. Setelah memetakan situs target seperti biasa, Anda dapat mempersempit jumlah *endpoint* yang perlu diuji dengan menanyakan beberapa hal berikut kepada diri sendiri:

- **Apakah endpoint ini krusial secara keamanan?** Banyak *endpoint* tidak menyentuh fungsionalitas kritis, jadi tidak layak untuk diuji.
- **Apakah ada potensi tabrakan?** Untuk tabrakan yang sukses, biasanya Anda memerlukan dua atau lebih *request* yang memicu operasi pada baris/catatan (*record*) yang sama. Sebagai contoh, pertimbangkan variasi implementasi reset kata sandi berikut:

![[RaCo6.png]]

Pada contoh pertama, meminta reset kata sandi secara paralel untuk dua pengguna yang berbeda tidak mungkin menyebabkan tabrakan karena memodifikasi dua catatan yang berbeda. Namun, implementasi kedua memungkinkan Anda mengedit catatan yang sama dengan *request* untuk dua pengguna berbeda.

### 2 - Cari Petunjuk (Probe for Clues)

Untuk mengenali petunjuk, pertama-tama Anda perlu melakukan tolok ukur (*benchmark*) bagaimana perilaku *endpoint* dalam kondisi normal. Anda dapat melakukannya di Burp Repeater by mengelompokkan semua *request* Anda dan memilih opsi **Send group in sequence (separate connections)**. Untuk informasi lebih lanjut, lihat [Sending requests in sequence](https://portswigger.net/burp/documentation/desktop/tools/repeater/send-group#sending-requests-in-sequence).

Selanjutnya, kirim kelompok *request* yang sama sekaligus menggunakan *single-packet attack* (atau *last-byte sync* jika HTTP/2 tidak didukung) untuk meminimalkan *network jitter*. Anda dapat melakukannya di Burp Repeater dengan memilih opsi **Send group in parallel**. Untuk informasi lebih lanjut, lihat [Sending requests in parallel](https://portswigger.net/burp/documentation/desktop/tools/repeater/send-group#sending-requests-in-parallel). Sebagai alternatif, Anda dapat menggunakan ekstensi Turbo Intruder yang tersedia di [BApp Store](https://portswigger.net/bappstore/9abaa233088242e8be252cd4ff534988).

Apa pun bisa menjadi petunjuk. Cari saja penyimpangan (*deviation*) dari apa yang Anda amati selama pembandingan (*benchmarking*). Hal ini mencakup perubahan pada satu atau beberapa respons, tetapi jangan lupakan efek tingkat kedua (*second-order effects*) seperti konten email yang berbeda atau perubahan perilaku aplikasi yang terlihat setelahnya.

### 3 - Buktikan Konsepnya (Prove the Concept)

Cobalah untuk memahami apa yang terjadi, hapus *request* yang tidak diperlukan, dan pastikan Anda masih dapat mereplikasi dampaknya.

*Race condition* tingkat lanjut dapat menghasilkan primitif yang tidak biasa dan unik, sehingga jalan menuju dampak maksimum tidak selalu terlihat jelas sejak awal. Mungkin membantu jika Anda memikirkan setiap *race condition* sebagai kelemahan struktural, bukan sekadar kerentanan yang terisolasi.

#### Riset PortSwigger
Untuk metodologi yang lebih detail, silakan baca artikel pendamping lengkapnya: [Smashing the state machine: The true potential of web race conditions](https://portswigger.net/research/smashing-the-state-machine)

---

## Multi-Endpoint Race Conditions (Kondisi Balapan Multi-Endpoint)

Bentuk *race condition* yang paling intuitif adalah yang melibatkan pengiriman *request* ke beberapa *endpoint* berbeda secara bersamaan.

Bayangkan celah logika klasik di toko online di mana Anda menambahkan barang ke keranjang belanja, membayarnya, lalu menambahkan lebih banyak barang ke keranjang sebelum melakukan *forced browsing* ke halaman konfirmasi pesanan.

#### Catatan

Jika Anda belum terbiasa dengan eksploitasi ini, silakan pelajari lab *Insufficient workflow validation* dari topik celah Logika Bisnis (*Business logic vulnerabilities*).

Variasi dari kerentanan ini dapat terjadi ketika validasi pembayaran dan konfirmasi pesanan dilakukan selama pemrosesan satu *request*. *State machine* untuk status pesanan mungkin terlihat seperti ini:

![[RaCo7.png]]

Dalam kasus ini, Anda berpotensi menambahkan lebih banyak barang ke keranjang selama *race window* antara saat pembayaran divalidasi dan saat pesanan akhirnya dikonfirmasi.

### Menyelaraskan Jendela Balapan Multi-Endpoint (Aligning Multi-Endpoint Race Windows)

Saat menguji *multi-endpoint race conditions*, Anda mungkin menemui masalah dalam menyelaraskan *race window* untuk setiap *request, meskipun Anda mengirim semuanya pada waktu yang persis sama menggunakan teknik *single-packet*.

![[8.png]]

Masalah umum ini terutama disebabkan oleh dua faktor berikut:

- **Penundaan akibat arsitektur jaringan -** Misalnya, mungkin ada penundaan setiap kali server *front-end* membuat koneksi baru ke *back-end*. Protokol yang digunakan juga bisa memiliki dampak besar.
- **Penundaan akibat pemrosesan spesifik endpoint -** *Endpoint* yang berbeda secara alami memiliki waktu pemrosesan yang bervariasi, terkadang sangat signifikan, tergantung pada operasi apa yang dipicunya.

Untungnya, ada beberapa solusi untuk mengatasi kedua masalah ini.

#### Pemanasan Koneksi (Connection Warming)

Penundaan koneksi *back-end* biasanya tidak mengganggu serangan *race condition* karena penundaan tersebut umumnya memengaruhi *request* paralel secara setara, sehingga *request* tetap sinkron.

Sangat penting untuk membedakan penundaan ini dari penundaan yang disebabkan oleh faktor spesifik *endpoint*. Salah satu caranya adalah dengan "memanaskan" (*warming*) koneksi dengan satu atau beberapa *request* yang tidak berbahaya untuk melihat apakah hal ini menstabilkan waktu pemrosesan selanjutnya. Di Burp Repeater, Anda dapat mencoba menambahkan *request* `GET` untuk halaman beranda (*homepage*) di awal grup tab Anda, lalu menggunakan opsi **Send group in sequence (single connection)**.

Jika *request* pertama masih memiliki waktu pemrosesan yang lebih lama, tetapi sisa *request* lainnya diproses dalam jendela waktu yang singkat, Anda dapat mengabaikan penundaan awal tersebut dan melanjutkan pengujian seperti biasa.

Jika Anda masih melihat waktu respons yang tidak konsisten pada satu *endpoint*, bahkan saat menggunakan teknik *single-packet*, ini merupakan indikasi bahwa penundaan *back-end* mengganggu serangan Anda. Anda mungkin dapat menyiasatinya dengan menggunakan Turbo Intruder untuk mengirim beberapa *request* pemanasan koneksi sebelum melanjutkannya dengan *request* serangan utama Anda.

#### Menyalahgunakan Batas Laju atau Sumber Daya (Abusing Rate or Resource Limits)

Jika pemanasan koneksi tidak membawa perubahan, ada solusi lain untuk masalah ini.

Menggunakan Turbo Intruder, Anda dapat menambahkan penundaan singkat di sisi klien (*client-side delay*). Namun, karena hal ini membagi *request* serangan Anda ke dalam beberapa paket TCP, Anda tidak akan bisa menggunakan teknik *single-packet attack*. Akibatnya, pada target dengan *jitter* tinggi, serangan tersebut kemungkinan besar tidak akan berfungsi secara andal berapa pun penundaan yang Anda atur.

![[9.png]]

Sebagai gantinya, Anda mungkin dapat menyelesaikan masalah ini dengan menyalahgunakan fitur keamanan yang umum.

Server web sering kali menunda pemrosesan *request* jika terlalu banyak dikirim terlalu cepat. Dengan mengirimkan sejumlah besar *request* palsu (*dummy requests*) untuk sengaja memicu batas laju (*rate limit*) atau sumber daya, Anda mungkin dapat memicu penundaan yang sesuai di sisi server. Hal ini membuat serangan paket tunggal tetap dapat dilakukan bahkan ketika eksekusi yang tertunda diperlukan.

![[10.png]]

---

## Single-Endpoint Race Conditions (Kondisi Balapan Single-Endpoint)

Mengirimkan *request* paralel dengan nilai berbeda ke satu *endpoint* yang sama terkadang dapat memicu *race condition* yang fatal.

Bayangkan mekanisme reset kata sandi yang menyimpan ID pengguna dan token reset di sesi pengguna (*session*). Dalam skenario ini, mengirimkan dua *request* reset kata sandi secara paralel dari sesi yang sama, tetapi dengan dua nama pengguna yang berbeda, dapat menyebabkan tabrakan berikut:

![[11.png]]

Perhatikan status akhir ketika semua operasi selesai:
- `session['reset-user'] = victim`
- `session['reset-token'] = 1234`

Sesi sekarang berisi ID pengguna korban (*victim*), tetapi token reset yang valid dikirim ke penyerang.

#### Catatan

Agar serangan ini berhasil, operasi berbeda yang dilakukan oleh setiap proses harus terjadi dalam urutan yang tepat. Ini mungkin memerlukan beberapa kali percobaan, atau sedikit keberuntungan, untuk mencapai hasil yang diinginkan.

Konfirmasi alamat email, atau operasi berbasis email lainnya, umumnya merupakan target yang bagus untuk *single-endpoint race conditions*. Email sering dikirim dalam *thread background* setelah server memberikan respons HTTP ke klien, sehingga meningkatkan kemungkinan terjadinya *race condition*.

---

## Mekanisme Penguncian Berbasis Sesi (Session-Based Locking Mechanisms)

Beberapa kerangka kerja (*framework*) mencoba mencegah kerusakan data yang tidak disengaja dengan menggunakan beberapa bentuk penguncian *request* (*request locking*). Sebagai contoh, modul penanganan sesi bawaan PHP hanya memproses satu *request* per sesi dalam satu waktu.

Sangat penting untuk mendeteksi perilaku semacam ini karena jika tidak, ia dapat menyembunyikan kerentanan yang sebenarnya mudah dieksploitasi. Jika Anda mendapati bahwa semua *request* Anda diproses secara berurutan (*sequentially*), cobalah mengirim masing-masing *request* menggunakan token sesi (*session token*) yang berbeda.

---

## Partial Construction Race Conditions (Kondisi Balapan Konstruksi Parsial)

Banyak aplikasi membuat objek dalam beberapa langkah, yang dapat memicu status menengah sementara (*temporary middle state*) di mana objek tersebut dapat dieksploitasi.

Sebagai contoh, saat mendaftarkan pengguna baru, aplikasi mungkin membuat pengguna di database dan menyetel kunci API (*API key*) mereka menggunakan dua pernyataan SQL yang terpisah. Hal ini menyisakan jendela waktu yang sangat kecil di mana akun pengguna sudah ada, tetapi kunci API mereka belum diinisialisasi (*uninitialized*).

Perilaku semacam ini membuka jalan bagi eksploitasi di mana Anda mengirimkan nilai masukan yang cocok dengan nilai database yang belum diinisialisasi, seperti string kosong, atau `null` dalam JSON, yang kemudian dibandingkan sebagai bagian dari kontrol keamanan.

*Framework* sering kali memungkinkan Anda memasukkan array dan struktur data non-string lainnya menggunakan sintaksis non-standar. Sebagai contoh, di PHP:
- `param[]=foo` setara dengan `param = ['foo']`
- `param[]=foo&param[]=bar` setara dengan `param = ['foo', 'bar']`
- `param[]` setara dengan `param = []`

Ruby on Rails memungkinkan Anda melakukan hal serupa dengan menyediakan parameter kueri (*query*) atau `POST` dengan kunci (*key*) tanpa nilai. Dengan kata lain, `param[key]` menghasilkan objek sisi server berikut:

```ruby
params = {"param"=>{"key"=>nil}}
```

Dalam contoh di atas, ini berarti selama *race window*, Anda berpotensi membuat permintaan API terotentikasi sebagai berikut:

```http
GET /api/user/info?user=victim&api-key[]= HTTP/2
Host: vulnerable-website.com
```

#### Catatan

Sangat mungkin untuk memicu tabrakan konstruksi parsial yang serupa menggunakan kata sandi (*password*) alih-alih kunci API. Namun, karena kata sandi di-hash, ini berarti Anda perlu memasukkan nilai yang membuat hasil hash (*hash digest*) cocok dengan nilai yang belum diinisialisasi.

---

## Serangan Sensitif-Waktu (Time-Sensitive Attacks)

Terkadang Anda mungkin tidak menemukan *race condition*, tetapi teknik pengiriman *request* dengan waktu yang presisi tetap dapat mengungkap keberadaan kerentanan lainnya.

Salah satu contohnya adalah ketika stempel waktu resolusi tinggi (*high-resolution timestamps*) digunakan alih-alih string acak yang aman secara kriptografis untuk menghasilkan token keamanan.

Bayangkan sebuah token reset kata sandi yang keacakannya hanya menggunakan stempel waktu (*timestamp*). Dalam kasus ini, Anda mungkin bisa memicu dua kali reset kata sandi untuk dua pengguna yang berbeda, yang keduanya menggunakan token yang sama. Yang perlu Anda lakukan adalah mengatur waktu permintaan sehingga menghasilkan stempel waktu yang sama persis.

---

## Cara Mencegah Kerentanan Race Condition

Ketika satu *request* dapat mengubah status aplikasi melalui sub-status yang tidak terlihat, memahami dan memprediksi perilakunya menjadi sangat sulit. Hal ini membuat pertahanan menjadi tidak praktis. Untuk mengamankan aplikasi dengan benar, kami menyarankan untuk menghilangkan sub-status dari semua *endpoint* sensitif dengan menerapkan strategi berikut:

- Hindari mencampur data dari berbagai tempat penyimpanan yang berbeda.
- Pastikan *endpoint* sensitif melakukan perubahan status secara atomik dengan memanfaatkan fitur konkurensi penyimpanan data. Misalnya, gunakan transaksi database tunggal untuk memeriksa kecocokan pembayaran dengan nilai keranjang belanja sekaligus mengonfirmasi pesanan.
- Sebagai langkah perlindungan berlapis (*defense-in-depth*), manfaatkan fitur integritas dan konsistensi penyimpanan data seperti kendala keunikan kolom (*column uniqueness constraints*).
- Jangan mencoba menggunakan satu lapisan penyimpanan data untuk mengamankan lapisan lainnya. Sebagai contoh, sesi (*session*) tidak cocok untuk mencegah serangan *limit overrun* pada database.
- Pastikan kerangka kerja penanganan sesi Anda menjaga konsistensi sesi secara internal. Memperbarui variabel sesi secara individual alih-alih dalam satu kelompok (batch) mungkin merupakan optimalisasi yang menggoda, tetapi sangat berbahaya. Hal ini berlaku juga untuk ORM; dengan menyembunyikan konsep seperti transaksi, mereka mengambil alih tanggung jawab penuh atas hal tersebut.
- Dalam beberapa arsitektur, mungkin tepat untuk menghindari status di sisi server (*server-side state*) sepenuhnya. Sebagai gantinya, Anda dapat menggunakan enkripsi untuk memindahkan status ke sisi klien (*client-side*), misalnya menggunakan JWT. Perhatikan bahwa ini memiliki risikonya sendiri, seperti yang telah kami bahas secara mendalam dalam topik kami tentang [serangan JWT](https://portswigger.net/web-security/jwt).