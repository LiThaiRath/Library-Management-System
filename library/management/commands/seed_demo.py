from django.contrib.auth.models import User
from django.core.management.base import BaseCommand

from accounts.models import AdminProfile, Member
from library.models import Book


class Command(BaseCommand):
    help = "สร้างข้อมูลตัวอย่าง (บัญชีแอดมิน, สมาชิก, หนังสือ) สำหรับทดสอบระบบ"

    def handle(self, *args, **options):
        # ----- แอดมิน -----
        if not User.objects.filter(username="admin").exists():
            admin_user = User.objects.create_user(username="admin", password="admin1234", is_staff=True, is_superuser=True)
            AdminProfile.objects.create(user=admin_user, full_name="บรรณารักษ์ ใจดี")
            self.stdout.write(self.style.SUCCESS("สร้างบัญชีแอดมิน: admin / admin1234"))

        # ----- สมาชิกตัวอย่าง -----
        demo_students = [
            ("student1", "student1234", "S001", "สมชาย ตั้งใจเรียน", "ม.4/1"),
            ("student2", "student1234", "S002", "สมหญิง ขยันอ่าน", "ม.4/2"),
            ("student3", "student1234", "S003", "วิชัย รักหนังสือ", "ม.5/1"),
        ]
        for username, password, sid, name, klass in demo_students:
            if not User.objects.filter(username=username).exists():
                u = User.objects.create_user(username=username, password=password)
                Member.objects.create(user=u, student_id=sid, full_name=name, class_name=klass,
                                       phone="0800000000", email=f"{username}@example.com")
                self.stdout.write(self.style.SUCCESS(f"สร้างบัญชีสมาชิก: {username} / {password}"))

        # ----- หนังสือตัวอย่าง -----
        demo_books = [
            ("978-1", "แฮร์รี่ พอตเตอร์ กับศิลาอาถรรพ์", "นิยาย", "J.K. Rowling", "นานมีบุ๊คส์", 2000, 3, "#6c63ff"),
            ("978-2", "ผู้ชายที่หลงรักคณิตศาสตร์", "สารคดี", "อดัม สเปนเซอร์", "SE-ED", 2018, 2, "#2ec4b6"),
            ("978-3", "เจ้าชายน้อย", "วรรณกรรม", "อองตวน เดอ แซงเตกซูเปรี", "ผีเสื้อ", 1943, 4, "#ff6b9d"),
            ("978-4", "คู่มือแพทย์แผนปัจจุบัน", "วิชาการ", "นพ. สมพงษ์", "จุฬาฯ", 2019, 1, "#ffb703"),
            ("978-5", "ประวัติศาสตร์ไทย ฉบับเยาวชน", "ประวัติศาสตร์", "กรมศิลปากร", "อมรินทร์", 2015, 2, "#38b26f"),
            ("978-6", "Python สำหรับผู้เริ่มต้น", "คอมพิวเตอร์", "วีระ ชาญวิทย์", "SE-ED", 2022, 3, "#4b45c6"),
            ("978-7", "โลกของโซฟี", "ปรัชญา", "โยสไตน์ กอร์เดอร์", "ผีเสื้อ", 1995, 1, "#e63946"),
            ("978-8", "วิทยาศาสตร์รอบตัว ม.ต้น", "วิทยาศาสตร์", "สสวท.", "สสวท.", 2021, 5, "#2ec4b6"),
        ]
        for isbn, title, cat, author, pub, year, qty, color in demo_books:
            if not Book.objects.filter(isbn=isbn).exists():
                Book.objects.create(isbn=isbn, title=title, category=cat, author=author,
                                     publisher=pub, publish_year=year, quantity=qty, available=qty,
                                     cover_color=color)

        self.stdout.write(self.style.SUCCESS("เพิ่มข้อมูลตัวอย่างเรียบร้อยแล้ว!"))
