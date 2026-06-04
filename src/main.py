"""Kütüphane Yönetim Sistemi — Komut Satırı Arayüzü (CLI).

Çalıştırmak için proje kökünden:
    python -m src.main

İlk çalıştırmada veritabanı (library.db) yoksa schema.sql'den otomatik oluşturulur
ve örnek verilerle doldurulur.
"""

from src import db
from src.repository import (
    BookRepository,
    MemberRepository,
    LoanRepository,
    LibraryError,
)


# -------------------------------------------------------------
# Girdi yardımcıları
# -------------------------------------------------------------
def prompt(text):
    """Kullanıcıdan metin girişi alır (boşlukları temizler)."""
    return input(text).strip()


def prompt_int(text, allow_empty=False):
    """Kullanıcıdan tam sayı girişi alır; hatalı girişte tekrar sorar.

    allow_empty=True ise boş girişe izin verir ve None döndürür.
    """
    while True:
        value = input(text).strip()
        if value == "" and allow_empty:
            return None
        try:
            return int(value)
        except ValueError:
            print("  ! Lütfen geçerli bir sayı girin.")


def prompt_optional(text):
    """Boş bırakılabilen metin girişi; boşsa None döndürür."""
    value = input(text).strip()
    return value or None


# -------------------------------------------------------------
# Görüntüleme yardımcıları
# -------------------------------------------------------------
def print_books(rows):
    if not rows:
        print("  (Kayıtlı kitap yok)")
        return
    print(f"  {'ID':<4}{'Başlık':<28}{'Yazar':<22}{'Yıl':<6}{'Mevcut/Toplam'}")
    print("  " + "-" * 70)
    for r in rows:
        stok = f"{r['available_copies']}/{r['total_copies']}"
        print(f"  {r['id']:<4}{r['title'][:27]:<28}{r['author'][:21]:<22}"
              f"{str(r['published_year'] or '-'):<6}{stok}")


def print_members(rows):
    if not rows:
        print("  (Kayıtlı üye yok)")
        return
    print(f"  {'ID':<4}{'İsim':<24}{'E-posta':<30}{'Telefon'}")
    print("  " + "-" * 70)
    for r in rows:
        print(f"  {r['id']:<4}{r['name'][:23]:<24}"
              f"{str(r['email'] or '-')[:29]:<30}{r['phone'] or '-'}")


def print_loans(rows):
    if not rows:
        print("  (Ödünç kaydı yok)")
        return
    print(f"  {'ID':<4}{'Kitap':<26}{'Üye':<20}{'Veriliş':<12}{'Termin':<12}{'İade'}")
    print("  " + "-" * 80)
    for r in rows:
        iade = r["return_date"] or "— (aktif)"
        print(f"  {r['id']:<4}{r['book_title'][:25]:<26}{r['member_name'][:19]:<20}"
              f"{r['loan_date']:<12}{r['due_date']:<12}{iade}")


# -------------------------------------------------------------
# Kitap menüsü
# -------------------------------------------------------------
def book_menu(conn):
    repo = BookRepository(conn)
    while True:
        print("\n--- KİTAPLAR ---")
        print("  1) Listele")
        print("  2) Ara")
        print("  3) Ekle")
        print("  4) Güncelle")
        print("  5) Sil")
        print("  0) Geri")
        choice = prompt("Seçim: ")

        if choice == "1":
            print_books(repo.list_books())
        elif choice == "2":
            kw = prompt("Anahtar kelime (başlık/yazar): ")
            print_books(repo.search_books(kw))
        elif choice == "3":
            title = prompt("Başlık: ")
            author = prompt("Yazar: ")
            isbn = prompt_optional("ISBN (opsiyonel): ")
            year = prompt_int("Yayın yılı (opsiyonel): ", allow_empty=True)
            copies = prompt_int("Kopya sayısı [1]: ", allow_empty=True) or 1
            try:
                book_id = repo.add_book(title, author, isbn, year, copies)
                print(f"  + Kitap eklendi (ID: {book_id}).")
            except Exception as e:
                print(f"  ! Hata: {e}")
        elif choice == "4":
            book_id = prompt_int("Güncellenecek kitap ID: ")
            book = repo.get_book(book_id)
            if book is None:
                print("  ! Kitap bulunamadı.")
                continue
            print(f"  Mevcut: {book['title']} / {book['author']}")
            title = prompt(f"Başlık [{book['title']}]: ") or book["title"]
            author = prompt(f"Yazar [{book['author']}]: ") or book["author"]
            isbn = prompt(f"ISBN [{book['isbn'] or '-'}]: ") or book["isbn"]
            year_in = prompt_int("Yayın yılı (boş=değişme): ", allow_empty=True)
            year = year_in if year_in is not None else book["published_year"]
            copies_in = prompt_int("Toplam kopya (boş=değişme): ", allow_empty=True)
            copies = copies_in if copies_in is not None else book["total_copies"]
            try:
                repo.update_book(book_id, title, author, isbn, year, copies)
                print("  + Kitap güncellendi.")
            except LibraryError as e:
                print(f"  ! Hata: {e}")
        elif choice == "5":
            book_id = prompt_int("Silinecek kitap ID: ")
            try:
                repo.delete_book(book_id)
                print("  + Kitap silindi.")
            except LibraryError as e:
                print(f"  ! Hata: {e}")
        elif choice == "0":
            return
        else:
            print("  ! Geçersiz seçim.")


# -------------------------------------------------------------
# Üye menüsü
# -------------------------------------------------------------
def member_menu(conn):
    repo = MemberRepository(conn)
    while True:
        print("\n--- ÜYELER ---")
        print("  1) Listele")
        print("  2) Ekle")
        print("  3) Güncelle")
        print("  4) Sil")
        print("  0) Geri")
        choice = prompt("Seçim: ")

        if choice == "1":
            print_members(repo.list_members())
        elif choice == "2":
            name = prompt("İsim: ")
            email = prompt_optional("E-posta (opsiyonel): ")
            phone = prompt_optional("Telefon (opsiyonel): ")
            try:
                member_id = repo.add_member(name, email, phone)
                print(f"  + Üye eklendi (ID: {member_id}).")
            except Exception as e:
                print(f"  ! Hata: {e}")
        elif choice == "3":
            member_id = prompt_int("Güncellenecek üye ID: ")
            member = repo.get_member(member_id)
            if member is None:
                print("  ! Üye bulunamadı.")
                continue
            name = prompt(f"İsim [{member['name']}]: ") or member["name"]
            email = prompt(f"E-posta [{member['email'] or '-'}]: ") or member["email"]
            phone = prompt(f"Telefon [{member['phone'] or '-'}]: ") or member["phone"]
            try:
                repo.update_member(member_id, name, email, phone)
                print("  + Üye güncellendi.")
            except LibraryError as e:
                print(f"  ! Hata: {e}")
        elif choice == "4":
            member_id = prompt_int("Silinecek üye ID: ")
            try:
                repo.delete_member(member_id)
                print("  + Üye silindi.")
            except LibraryError as e:
                print(f"  ! Hata: {e}")
        elif choice == "0":
            return
        else:
            print("  ! Geçersiz seçim.")


# -------------------------------------------------------------
# Ödünç menüsü
# -------------------------------------------------------------
def loan_menu(conn):
    repo = LoanRepository(conn)
    while True:
        print("\n--- ÖDÜNÇ İŞLEMLERİ ---")
        print("  1) Tüm ödünç kayıtları")
        print("  2) Aktif (iade edilmemiş) kayıtlar")
        print("  3) Kitap ödünç ver")
        print("  4) Kitap iade al")
        print("  0) Geri")
        choice = prompt("Seçim: ")

        if choice == "1":
            print_loans(repo.list_loans())
        elif choice == "2":
            print_loans(repo.list_loans(only_active=True))
        elif choice == "3":
            book_id = prompt_int("Kitap ID: ")
            member_id = prompt_int("Üye ID: ")
            days = prompt_int("Kaç gün ödünç [14]: ", allow_empty=True) or 14
            try:
                loan_id = repo.borrow_book(book_id, member_id, loan_days=days)
                print(f"  + Ödünç verildi (Kayıt ID: {loan_id}).")
            except LibraryError as e:
                print(f"  ! Hata: {e}")
        elif choice == "4":
            loan_id = prompt_int("İade edilecek ödünç kaydı ID: ")
            try:
                repo.return_book(loan_id)
                print("  + Kitap iade alındı.")
            except LibraryError as e:
                print(f"  ! Hata: {e}")
        elif choice == "0":
            return
        else:
            print("  ! Geçersiz seçim.")


# -------------------------------------------------------------
# Ana menü
# -------------------------------------------------------------
def main():
    # Veritabanı yoksa şemadan oluştur + örnek verileri yükle
    if not db.database_exists():
        print("Veritabanı bulunamadı, schema.sql'den oluşturuluyor...")
        db.init_db()
        print("Veritabanı hazır (örnek verilerle).")

    conn = db.get_connection()
    try:
        while True:
            print("\n==============================")
            print("  KÜTÜPHANE YÖNETİM SİSTEMİ")
            print("==============================")
            print("  1) Kitaplar")
            print("  2) Üyeler")
            print("  3) Ödünç İşlemleri")
            print("  0) Çıkış")
            choice = prompt("Seçim: ")

            if choice == "1":
                book_menu(conn)
            elif choice == "2":
                member_menu(conn)
            elif choice == "3":
                loan_menu(conn)
            elif choice == "0":
                print("Görüşmek üzere!")
                break
            else:
                print("  ! Geçersiz seçim.")
    finally:
        conn.close()


if __name__ == "__main__":
    try:
        main()
    except (KeyboardInterrupt, EOFError):
        print("\nÇıkılıyor...")
