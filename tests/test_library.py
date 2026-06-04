"""Kütüphane Yönetim Sistemi — Test Durumları.

Standart kütüphanedeki `unittest` ile yazılmıştır. Çalıştırmak için proje kökünden:
    python -m unittest -v

Her test bağımsızdır: schema.sql'den geçici bir SQLite veritabanı oluşturulur,
test bitince silinir. Böylece testler birbirini etkilemez.
"""

import os
import tempfile
import unittest

from src import db
from src.repository import (
    BookRepository,
    MemberRepository,
    LoanRepository,
    LibraryError,
)


class LibraryTestCase(unittest.TestCase):
    def setUp(self):
        # Geçici bir veritabanı dosyası oluştur ve şemayı + örnek veriyi yükle
        fd, self.db_path = tempfile.mkstemp(suffix=".db")
        os.close(fd)
        os.remove(self.db_path)  # init_db temiz bir dosya oluştursun
        db.init_db(self.db_path)
        self.conn = db.get_connection(self.db_path)

        self.books = BookRepository(self.conn)
        self.members = MemberRepository(self.conn)
        self.loans = LoanRepository(self.conn)

    def tearDown(self):
        self.conn.close()
        if os.path.exists(self.db_path):
            os.remove(self.db_path)

    # --------------------------------------------------------- KİTAP
    def test_sample_data_loaded(self):
        """schema.sql örnek verisi yüklenmiş olmalı (5 kitap, 3 üye)."""
        self.assertEqual(len(self.books.list_books()), 5)
        self.assertEqual(len(self.members.list_members()), 3)

    def test_add_and_get_book(self):
        book_id = self.books.add_book(
            "Test Kitabı", "Yazar A", isbn="111", published_year=2020, total_copies=2
        )
        book = self.books.get_book(book_id)
        self.assertIsNotNone(book)
        self.assertEqual(book["title"], "Test Kitabı")
        self.assertEqual(book["total_copies"], 2)
        self.assertEqual(book["available_copies"], 2)

    def test_update_book(self):
        book_id = self.books.add_book("Eski", "Yazar", total_copies=1)
        self.books.update_book(book_id, "Yeni Başlık", "Yeni Yazar", "999", 2021, 3)
        book = self.books.get_book(book_id)
        self.assertEqual(book["title"], "Yeni Başlık")
        self.assertEqual(book["total_copies"], 3)

    def test_delete_book(self):
        book_id = self.books.add_book("Silinecek", "Yazar")
        self.books.delete_book(book_id)
        self.assertIsNone(self.books.get_book(book_id))

    def test_search_books(self):
        results = self.books.search_books("Orwell")
        self.assertTrue(any(r["title"] == "1984" for r in results))

    # --------------------------------------------------------- ÜYE
    def test_add_update_delete_member(self):
        member_id = self.members.add_member("Ali Veli", "ali@example.com", "0500")
        self.assertIsNotNone(self.members.get_member(member_id))

        self.members.update_member(member_id, "Ali Yeni", "ali2@example.com", "0501")
        self.assertEqual(self.members.get_member(member_id)["name"], "Ali Yeni")

        self.members.delete_member(member_id)
        self.assertIsNone(self.members.get_member(member_id))

    # --------------------------------------------------------- ÖDÜNÇ
    def test_borrow_decreases_available(self):
        """Ödünç verme available_copies'i 1 azaltmalı."""
        book_id = self.books.add_book("Ödünç Kitabı", "Yazar", total_copies=2)
        member_id = self.members.add_member("Üye")
        before = self.books.get_book(book_id)["available_copies"]

        self.loans.borrow_book(book_id, member_id)

        after = self.books.get_book(book_id)["available_copies"]
        self.assertEqual(after, before - 1)

    def test_return_increases_available(self):
        """İade available_copies'i 1 artırmalı."""
        book_id = self.books.add_book("İade Kitabı", "Yazar", total_copies=1)
        member_id = self.members.add_member("Üye")
        loan_id = self.loans.borrow_book(book_id, member_id)
        self.assertEqual(self.books.get_book(book_id)["available_copies"], 0)

        self.loans.return_book(loan_id)
        self.assertEqual(self.books.get_book(book_id)["available_copies"], 1)

    def test_cannot_borrow_when_out_of_stock(self):
        """Stok 0 iken ödünç verme LibraryError fırlatmalı."""
        book_id = self.books.add_book("Tek Kopya", "Yazar", total_copies=1)
        member_id = self.members.add_member("Üye")
        self.loans.borrow_book(book_id, member_id)  # tek kopya tükendi

        with self.assertRaises(LibraryError):
            self.loans.borrow_book(book_id, member_id)

    def test_cannot_return_twice(self):
        """Zaten iade edilmiş kayıt tekrar iade edilememeli."""
        book_id = self.books.add_book("Kitap", "Yazar", total_copies=1)
        member_id = self.members.add_member("Üye")
        loan_id = self.loans.borrow_book(book_id, member_id)
        self.loans.return_book(loan_id)

        with self.assertRaises(LibraryError):
            self.loans.return_book(loan_id)

    def test_list_loans_join(self):
        """list_loans JOIN ile kitap başlığı ve üye adını döndürmeli."""
        book_id = self.books.add_book("JOIN Kitabı", "Yazar")
        member_id = self.members.add_member("Test Üye")
        self.loans.borrow_book(book_id, member_id)

        active = self.loans.list_loans(only_active=True)
        match = [r for r in active if r["book_title"] == "JOIN Kitabı"]
        self.assertEqual(len(match), 1)
        self.assertEqual(match[0]["member_name"], "Test Üye")

    def test_borrow_nonexistent_book(self):
        """Olmayan kitap için ödünç verme hata fırlatmalı."""
        member_id = self.members.add_member("Üye")
        with self.assertRaises(LibraryError):
            self.loans.borrow_book(9999, member_id)


if __name__ == "__main__":
    unittest.main()
