"""Veritabanı bağlantı yardımcıları.

SQLite bağlantısı kurar ve `sql/schema.sql` dosyasından şemayı oluşturur.
Harici bağımlılık yoktur; yalnızca standart kütüphanedeki `sqlite3` kullanılır.
"""

import os
import sqlite3

# Bu dosyanın bulunduğu dizinden proje köküne ve schema.sql'e giden yollar
_THIS_DIR = os.path.dirname(os.path.abspath(__file__))
_PROJECT_ROOT = os.path.dirname(_THIS_DIR)
SCHEMA_PATH = os.path.join(_PROJECT_ROOT, "sql", "schema.sql")

# Varsayılan veritabanı dosyası (proje kökünde oluşur, .gitignore'dadır)
DEFAULT_DB_PATH = os.path.join(_PROJECT_ROOT, "library.db")


def get_connection(db_path=DEFAULT_DB_PATH):
    """Bir SQLite bağlantısı döndürür.

    - `row_factory = sqlite3.Row` sayesinde satırlara sütun adıyla erişilebilir.
    - `PRAGMA foreign_keys = ON` ile foreign key kısıtlamaları zorlanır.
    """
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn


def init_db(db_path=DEFAULT_DB_PATH):
    """schema.sql dosyasını çalıştırarak veritabanını oluşturur ve örnek veriyi ekler.

    Tablolar `CREATE TABLE IF NOT EXISTS` ile tanımlandığından tekrar çalıştırmak
    tabloları bozmaz; ancak örnek INSERT'ler tekrar eklenmeye çalışılır. Bu yüzden
    init_db yalnızca veritabanı henüz yoksa örnek verilerle kurulum yapacak şekilde
    çağrılmalıdır (bkz. main.py).
    """
    with open(SCHEMA_PATH, "r", encoding="utf-8") as f:
        schema_sql = f.read()

    conn = get_connection(db_path)
    try:
        conn.executescript(schema_sql)
        conn.commit()
    finally:
        conn.close()


def database_exists(db_path=DEFAULT_DB_PATH):
    """Veritabanı dosyasının zaten var olup olmadığını döndürür."""
    return os.path.exists(db_path)
