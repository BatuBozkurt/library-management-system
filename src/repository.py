"""Veri erişim katmanı (Repository).

Kitap, üye ve ödünç kayıtları için CRUD işlemlerini içerir.
Tüm SQL sorguları parametreli (`?` placeholder) yazılmıştır; bu sayede
SQL injection saldırılarına karşı güvenlidir.

Her repository bir açık `sqlite3.Connection` alır. Bağlantının açılması/kapatılması
çağıran tarafın (örn. main.py veya testler) sorumluluğundadır.
"""

from datetime import date, timedelta


# =============================================================
# Hata tipleri
# =============================================================
class LibraryError(Exception):
    """Kütüphane iş kuralı ihlallerinde fırlatılan genel hata."""


# =============================================================
# KİTAP CRUD
# =============================================================
class BookRepository:
    def __init__(self, conn):
        self.conn = conn

    def add_book(self, title, author, isbn=None, published_year=None, total_copies=1):
        """Yeni kitap ekler ve eklenen kitabın id'sini döndürür.

        Başlangıçta mevcut kopya sayısı toplam kopya sayısına eşittir.
        """
        cur = self.conn.execute(
            """
            INSERT INTO books (title, author, isbn, published_year,
                               total_copies, available_copies)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (title, author, isbn, published_year, total_copies, total_copies),
        )
        self.conn.commit()
        return cur.lastrowid

    def list_books(self):
        """Tüm kitapları başlığa göre sıralı döndürür."""
        return self.conn.execute(
            "SELECT * FROM books ORDER BY title"
        ).fetchall()

    def get_book(self, book_id):
        """Tek bir kitabı id ile döndürür (yoksa None)."""
        return self.conn.execute(
            "SELECT * FROM books WHERE id = ?", (book_id,)
        ).fetchone()

    def search_books(self, keyword):
        """Başlık veya yazarda anahtar kelimeye göre arama yapar."""
        like = f"%{keyword}%"
        return self.conn.execute(
            "SELECT * FROM books WHERE title LIKE ? OR author LIKE ? ORDER BY title",
            (like, like),
        ).fetchall()

    def update_book(self, book_id, title, author, isbn, published_year, total_copies):
        """Kitap bilgilerini günceller.

        Toplam kopya sayısı değişirse mevcut kopya sayısı (ödünç verilenleri
        koruyacak şekilde) yeniden hesaplanır.
        """
        book = self.get_book(book_id)
        if book is None:
            raise LibraryError(f"{book_id} numaralı kitap bulunamadı.")

        # Şu an ödünçte olan kopya sayısı = eski total - eski available
        on_loan = book["total_copies"] - book["available_copies"]
        new_available = max(total_copies - on_loan, 0)

        self.conn.execute(
            """
            UPDATE books
               SET title = ?, author = ?, isbn = ?, published_year = ?,
                   total_copies = ?, available_copies = ?
             WHERE id = ?
            """,
            (title, author, isbn, published_year, total_copies, new_available, book_id),
        )
        self.conn.commit()

    def delete_book(self, book_id):
        """Kitabı siler. İlişkili ödünç kayıtları ON DELETE CASCADE ile silinir."""
        cur = self.conn.execute("DELETE FROM books WHERE id = ?", (book_id,))
        self.conn.commit()
        if cur.rowcount == 0:
            raise LibraryError(f"{book_id} numaralı kitap bulunamadı.")


# =============================================================
# ÜYE CRUD
# =============================================================
class MemberRepository:
    def __init__(self, conn):
        self.conn = conn

    def add_member(self, name, email=None, phone=None, join_date=None):
        """Yeni üye ekler ve eklenen üyenin id'sini döndürür."""
        if join_date is None:
            join_date = date.today().isoformat()
        cur = self.conn.execute(
            "INSERT INTO members (name, email, phone, join_date) VALUES (?, ?, ?, ?)",
            (name, email, phone, join_date),
        )
        self.conn.commit()
        return cur.lastrowid

    def list_members(self):
        """Tüm üyeleri isme göre sıralı döndürür."""
        return self.conn.execute(
            "SELECT * FROM members ORDER BY name"
        ).fetchall()

    def get_member(self, member_id):
        """Tek bir üyeyi id ile döndürür (yoksa None)."""
        return self.conn.execute(
            "SELECT * FROM members WHERE id = ?", (member_id,)
        ).fetchone()

    def update_member(self, member_id, name, email, phone):
        """Üye bilgilerini günceller."""
        cur = self.conn.execute(
            "UPDATE members SET name = ?, email = ?, phone = ? WHERE id = ?",
            (name, email, phone, member_id),
        )
        self.conn.commit()
        if cur.rowcount == 0:
            raise LibraryError(f"{member_id} numaralı üye bulunamadı.")

    def delete_member(self, member_id):
        """Üyeyi siler. İlişkili ödünç kayıtları ON DELETE CASCADE ile silinir."""
        cur = self.conn.execute("DELETE FROM members WHERE id = ?", (member_id,))
        self.conn.commit()
        if cur.rowcount == 0:
            raise LibraryError(f"{member_id} numaralı üye bulunamadı.")


# =============================================================
# ÖDÜNÇ İŞLEMLERİ
# =============================================================
class LoanRepository:
    def __init__(self, conn):
        self.conn = conn

    def borrow_book(self, book_id, member_id, loan_days=14, loan_date=None):
        """Bir kitabı bir üyeye ödünç verir.

        İş kuralları:
          - Kitap ve üye var olmalıdır.
          - Kitabın mevcut (available) kopyası > 0 olmalıdır.
        Başarılıysa loans tablosuna kayıt ekler, kitabın available_copies
        değerini 1 azaltır ve oluşturulan ödünç kaydının id'sini döndürür.
        """
        book = self.conn.execute(
            "SELECT * FROM books WHERE id = ?", (book_id,)
        ).fetchone()
        if book is None:
            raise LibraryError(f"{book_id} numaralı kitap bulunamadı.")

        member = self.conn.execute(
            "SELECT * FROM members WHERE id = ?", (member_id,)
        ).fetchone()
        if member is None:
            raise LibraryError(f"{member_id} numaralı üye bulunamadı.")

        if book["available_copies"] <= 0:
            raise LibraryError(
                f"'{book['title']}' için stokta mevcut kopya yok."
            )

        if loan_date is None:
            loan_date = date.today()
        elif isinstance(loan_date, str):
            loan_date = date.fromisoformat(loan_date)
        due_date = loan_date + timedelta(days=loan_days)

        cur = self.conn.execute(
            """
            INSERT INTO loans (book_id, member_id, loan_date, due_date, return_date)
            VALUES (?, ?, ?, ?, NULL)
            """,
            (book_id, member_id, loan_date.isoformat(), due_date.isoformat()),
        )
        # Stoktan bir kopya düş
        self.conn.execute(
            "UPDATE books SET available_copies = available_copies - 1 WHERE id = ?",
            (book_id,),
        )
        self.conn.commit()
        return cur.lastrowid

    def return_book(self, loan_id, return_date=None):
        """Ödünç alınan kitabı iade alır.

        return_date'i set eder ve kitabın available_copies değerini 1 artırır.
        Zaten iade edilmiş bir kayıt tekrar iade edilemez.
        """
        loan = self.conn.execute(
            "SELECT * FROM loans WHERE id = ?", (loan_id,)
        ).fetchone()
        if loan is None:
            raise LibraryError(f"{loan_id} numaralı ödünç kaydı bulunamadı.")
        if loan["return_date"] is not None:
            raise LibraryError("Bu kitap zaten iade edilmiş.")

        if return_date is None:
            return_date = date.today().isoformat()

        self.conn.execute(
            "UPDATE loans SET return_date = ? WHERE id = ?",
            (return_date, loan_id),
        )
        # Stoğa bir kopya geri ekle
        self.conn.execute(
            "UPDATE books SET available_copies = available_copies + 1 WHERE id = ?",
            (loan["book_id"],),
        )
        self.conn.commit()

    def list_loans(self, only_active=False):
        """Ödünç kayıtlarını JOIN ile kitap başlığı ve üye adıyla birlikte listeler.

        only_active=True ise yalnızca henüz iade edilmemiş (return_date IS NULL)
        kayıtları döndürür.
        """
        query = """
            SELECT l.id,
                   b.title       AS book_title,
                   m.name        AS member_name,
                   l.loan_date,
                   l.due_date,
                   l.return_date
              FROM loans   l
              JOIN books   b ON b.id = l.book_id
              JOIN members m ON m.id = l.member_id
        """
        if only_active:
            query += " WHERE l.return_date IS NULL"
        query += " ORDER BY l.loan_date DESC"
        return self.conn.execute(query).fetchall()
