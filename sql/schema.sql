-- =============================================================
-- Kütüphane Yönetim Sistemi — Veritabanı Şeması
-- SQLite
--
-- 3 tablo ve aralarındaki foreign key ilişkileri:
--   books   1 ── N  loans  N ── 1  members
--
-- Bir üye birden çok ödünç kaydı oluşturabilir.
-- Bir kitabın birden çok ödünç kaydı olabilir.
-- =============================================================

-- Foreign key kısıtlamalarını etkinleştir (SQLite'ta varsayılan kapalıdır)
PRAGMA foreign_keys = ON;

-- -------------------------------------------------------------
-- KİTAPLAR
-- -------------------------------------------------------------
CREATE TABLE IF NOT EXISTS books (
    id               INTEGER PRIMARY KEY AUTOINCREMENT,
    title            TEXT    NOT NULL,
    author           TEXT    NOT NULL,
    isbn             TEXT    UNIQUE,
    published_year   INTEGER,
    total_copies     INTEGER NOT NULL DEFAULT 1 CHECK (total_copies >= 0),
    available_copies INTEGER NOT NULL DEFAULT 1 CHECK (available_copies >= 0)
);

-- -------------------------------------------------------------
-- ÜYELER
-- -------------------------------------------------------------
CREATE TABLE IF NOT EXISTS members (
    id        INTEGER PRIMARY KEY AUTOINCREMENT,
    name      TEXT NOT NULL,
    email     TEXT UNIQUE,
    phone     TEXT,
    join_date TEXT NOT NULL DEFAULT (date('now'))
);

-- -------------------------------------------------------------
-- ÖDÜNÇ KAYITLARI
-- return_date NULL ise kitap henüz iade edilmemiştir.
-- -------------------------------------------------------------
CREATE TABLE IF NOT EXISTS loans (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    book_id     INTEGER NOT NULL,
    member_id   INTEGER NOT NULL,
    loan_date   TEXT NOT NULL DEFAULT (date('now')),
    due_date    TEXT NOT NULL,
    return_date TEXT,
    FOREIGN KEY (book_id)   REFERENCES books (id)   ON DELETE CASCADE,
    FOREIGN KEY (member_id) REFERENCES members (id) ON DELETE CASCADE
);

-- Sık kullanılan sorgular için indeksler
CREATE INDEX IF NOT EXISTS idx_loans_book   ON loans (book_id);
CREATE INDEX IF NOT EXISTS idx_loans_member ON loans (member_id);

-- =============================================================
-- ÖRNEK VERİLER
-- =============================================================

INSERT INTO books (title, author, isbn, published_year, total_copies, available_copies) VALUES
    ('Suç ve Ceza',          'Fyodor Dostoyevski', '9789750718533', 1866, 3, 3),
    ('Sefiller',             'Victor Hugo',         '9786053609537', 1862, 2, 2),
    ('1984',                 'George Orwell',       '9789750718532', 1949, 4, 4),
    ('Kürk Mantolu Madonna', 'Sabahattin Ali',      '9789753638029', 1943, 5, 5),
    ('Simyacı',              'Paulo Coelho',        '9789750726439', 1988, 2, 2);

INSERT INTO members (name, email, phone, join_date) VALUES
    ('Ayşe Yılmaz',  'ayse.yilmaz@example.com',  '0532 111 22 33', '2025-01-15'),
    ('Mehmet Demir', 'mehmet.demir@example.com', '0533 444 55 66', '2025-02-20'),
    ('Zeynep Kaya',  'zeynep.kaya@example.com',  '0534 777 88 99', '2025-03-10');

-- Örnek ödünç kayıtları
-- 1 numaralı kitaptan (Suç ve Ceza) bir kopya Ayşe'ye ödünç verildi (aktif)
INSERT INTO loans (book_id, member_id, loan_date, due_date, return_date) VALUES
    (1, 1, '2025-05-01', '2025-05-15', NULL),
-- 3 numaralı kitap (1984) Mehmet'e verilip iade edildi
    (3, 2, '2025-04-10', '2025-04-24', '2025-04-22');

-- Aktif ödünç verilen kopyayı stoktan düş (Suç ve Ceza: 3 -> 2)
UPDATE books SET available_copies = available_copies - 1 WHERE id = 1;
