# 📚 Kütüphane Yönetim Sistemi

Python + SQL (SQLite) ile geliştirilmiş, komut satırı arayüzlü (CLI) bir kütüphane
yönetim sistemi. Kitap, üye ve ödünç alma kayıtları üzerinde tam **CRUD** (Ekle,
Listele, Güncelle, Sil) işlemleri yapar. Tüm veriler bir SQLite veritabanında tutulur.

> Staj Projesi — **Proje 1: Veritabanı Uygulaması**
> Teknoloji kombinasyonu: **Python + SQL + GitHub**

---

## ✨ Özellikler

- **Kitaplar:** ekleme, listeleme, arama (başlık/yazar), güncelleme, silme
- **Üyeler:** ekleme, listeleme, güncelleme, silme
- **Ödünç işlemleri:** kitap ödünç verme ve iade alma
  - Ödünç verme kitabın **mevcut kopya sayısını** otomatik azaltır
  - İade alma kopya sayısını otomatik artırır
  - Stokta kopya yoksa ödünç verme engellenir
  - Ödünç kayıtları **JOIN** ile kitap başlığı ve üye adıyla birlikte listelenir
- **Sıfır harici bağımlılık:** yalnızca Python standart kütüphanesi (`sqlite3`, `unittest`)

---

## 🗄️ Veritabanı Tasarımı

Üç tablo ve aralarındaki **foreign key** ilişkileri:

```
books  1 ───< loans >─── 1  members
```

| Tablo | Açıklama | Önemli Alanlar |
|-------|----------|----------------|
| **books** | Kitaplar | `id`, `title`, `author`, `isbn` (UNIQUE), `published_year`, `total_copies`, `available_copies` |
| **members** | Üyeler | `id`, `name`, `email` (UNIQUE), `phone`, `join_date` |
| **loans** | Ödünç kayıtları | `id`, `book_id` (FK→books), `member_id` (FK→members), `loan_date`, `due_date`, `return_date` |

**İlişkiler:**
- Bir üye birden çok ödünç kaydına sahip olabilir (members 1—N loans).
- Bir kitabın birden çok ödünç kaydı olabilir (books 1—N loans).
- `loans.return_date` **NULL** ise kitap henüz iade edilmemiştir (aktif ödünç).
- Foreign key kısıtlamaları `PRAGMA foreign_keys = ON` ile zorlanır; üye/kitap silinince
  ilişkili ödünç kayıtları `ON DELETE CASCADE` ile silinir.

Şema ve örnek veriler: [sql/schema.sql](sql/schema.sql)

---

## 📁 Proje Yapısı

```
staj_proje/
├── README.md                 # Bu dosya
├── requirements.txt          # Bağımlılıklar (harici paket yok)
├── .gitignore
├── sql/
│   └── schema.sql            # CREATE TABLE (FK ile) + örnek INSERT verileri
├── src/
│   ├── db.py                 # SQLite bağlantısı ve init_db
│   ├── repository.py         # Kitap/Üye/Ödünç CRUD işlemleri
│   └── main.py               # CLI menü arayüzü
└── tests/
    └── test_library.py       # unittest test durumları
```

---

## 🚀 Kurulum ve Çalıştırma

**Gereksinim:** Python 3.10+ (harici paket kurulumuna gerek yoktur).

### Uygulamayı çalıştırma

Proje kök dizininden:

```bash
python -m src.main
```

İlk çalıştırmada `library.db` veritabanı yoksa `sql/schema.sql` dosyasından otomatik
oluşturulur ve örnek verilerle (5 kitap, 3 üye, 2 ödünç kaydı) doldurulur.

### Örnek kullanım akışı

1. Ana menüden `1) Kitaplar` → `1) Listele` ile kitapları gör.
2. `3) Ödünç İşlemleri` → `3) Kitap ödünç ver` ile bir kitabı bir üyeye ver
   (kitabın mevcut kopya sayısının düştüğünü görürsün).
3. `4) Kitap iade al` ile iade et (kopya sayısı geri artar).

---

## ✅ Testler

Standart kütüphanedeki `unittest` ile yazılmış 12 test durumu bulunur:

```bash
python -m unittest -v
```

Testler; CRUD işlemlerini, ödünç verince kopya sayısının azalmasını, iade edince
artmasını, stok bitince ödünç verilememesini ve JOIN'li listelemeyi doğrular.
Her test geçici bir veritabanı üzerinde izole çalışır.

---

## 🔧 Kullanılan Teknolojiler

- **Python 3** — uygulama mantığı ve CLI
- **SQLite** (`sqlite3`) — ilişkisel veritabanı, foreign key ilişkileri
- **SQL** — `CREATE TABLE`, ilişkiler, `JOIN`, parametreli sorgular
- **Git / GitHub** — sürüm kontrolü

> Güvenlik notu: Tüm sorgular parametreli (`?` placeholder) yazılmıştır; bu sayede
> SQL injection saldırılarına karşı korunur.

---

## 🛠️ Projeyi Nasıl Yaptım — İzlediğim Süreç

Projeyi adım adım, her aşamayı ayrı bir commit olacak şekilde geliştirdim:

1. **Planlama:** İki proje seçeneğinden (Kütüphane Yönetim Sistemi / Olist veri analizi)
   daha self-contained ve harici bağımlılık gerektirmeyen **Kütüphane Yönetim Sistemi**'ni
   seçtim. Teknoloji olarak **Python + SQLite** belirledim çünkü `sqlite3` Python'a
   gömülüdür ve kurulum derdi yoktur.
2. **Veritabanı tasarımı:** Önce kağıt üzerinde varlıkları (kitap, üye, ödünç) ve
   aralarındaki ilişkileri çıkardım, ardından `sql/schema.sql` içinde `CREATE TABLE`,
   foreign key kısıtlamaları ve örnek verileri yazdım.
3. **Katmanlı kod:** Veritabanı bağlantısını (`db.py`), iş mantığı/CRUD katmanını
   (`repository.py`) ve kullanıcı arayüzünü (`main.py`) ayrı dosyalara böldüm. Bu
   ayrım sayesinde arayüzü değiştirmeden mantığı test edebildim.
4. **Test:** `unittest` ile her CRUD işlemini ve ödünç/iade iş kurallarını doğrulayan
   12 test yazdım. Testler geçici veritabanı üzerinde izole çalışır.
5. **Dokümantasyon ve sürüm kontrolü:** README'yi yazdım, `git` ile anlamlı commit'ler
   attım ve projeyi GitHub'a push'ladım.

## 😅 Zorlandığım Kısımlar

- **SQLite foreign key davranışı:** SQLite'ta foreign key kısıtlamaları varsayılan
  olarak **kapalıdır**; her bağlantıda `PRAGMA foreign_keys = ON` çalıştırmam
  gerektiğini fark etmem zaman aldı.
- **Stok tutarlılığı:** Bir kitabın "toplam kopya" ve "mevcut kopya" sayılarını
  ödünç verme/iade işlemlerinde tutarlı tutmak (özellikle güncelleme sırasında ödünçte
  olan kopyaları korumak) üzerinde dikkatle düşündüğüm bir kısımdı.
- **Testleri izole etmek:** Testlerin birbirini etkilememesi için her testte geçici
  bir veritabanı oluşturup sonunda silmek gerekti; bunu `tempfile` ile çözdüm.
- **GitHub kimlik doğrulama:** Depoyu push'larken `gh` CLI kurulumu ve tarayıcı
  üzerinden kimlik doğrulama (auth) adımını yapmak başta kafa karıştırıcıydı.

## 🎓 Proje Sonunda Neler Öğrendim

- İlişkisel veritabanı tasarımının (tablolar, **birincil/yabancı anahtarlar**,
  ilişkiler) bir uygulamanın temelini nasıl oluşturduğunu.
- Kodu **katmanlara ayırmanın** (veri erişimi / iş mantığı / arayüz) bakım ve test
  kolaylığı açısından değerini.
- **Parametreli sorguların** SQL injection'a karşı neden zorunlu olduğunu.
- `unittest` ile **otomatik test** yazmanın, bir değişiklikten sonra her şeyin hâlâ
  çalıştığına güven vermesini.
- **Git/GitHub** ile anlamlı commit'ler atarak bir projenin gelişim sürecini takip
  edilebilir biçimde belgelemeyi.

## 🧩 Python, SQL ve GitHub'ın Projedeki Rolü

- **Python:** Uygulamanın iskeletini oluşturdu — veritabanına bağlanma, iş kurallarını
  (ödünç/iade, stok kontrolü) uygulama ve kullanıcıyla etkileşen CLI menüsünü sağlama.
  Standart kütüphanesi (`sqlite3`, `unittest`, `datetime`) sayesinde tek bir harici
  paket bile gerektirmedi.
- **SQL:** Verinin kalıcı olarak saklandığı ve yapılandırıldığı katman. `CREATE TABLE`
  ile şemayı, `FOREIGN KEY` ile ilişkileri kurdum; `INSERT/SELECT/UPDATE/DELETE` ile
  CRUD'u, `JOIN` ile de kitap–üye–ödünç verilerini birleştirerek anlamlı listeler
  ürettim. Veri bütünlüğü (UNIQUE, CHECK, FK) tamamen SQL tarafında garanti altına alındı.
- **GitHub:** Projenin sürüm kontrolü ve teslim platformu. Her geliştirme aşamasını ayrı
  bir commit ile kaydederek sürecin görünür olmasını sağladım; depo public olduğundan
  değerlendirme için erişilebilir.

## 🔗 GitHub Deposu

Repo linki: https://github.com/BatuBozkurt/library-management-system
