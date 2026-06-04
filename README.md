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

## 🔗 GitHub Deposu

Repo linki: https://github.com/BatuBozkurt/kutuphane-yonetim-sistemi
