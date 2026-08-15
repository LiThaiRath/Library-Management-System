from datetime import timedelta
from decimal import Decimal

from django.db import models
from django.utils import timezone

from accounts.models import Member, AdminProfile

# ตั้งค่าตามข้อกำหนดของห้องสมุด
BORROW_DAYS = 7          # ยืมได้กี่วัน
FINE_PER_DAY = Decimal("5.00")   # ค่าปรับต่อวัน (บาท)
MAX_BORROW_LIMIT = 5      # ยืมได้สูงสุดกี่เล่มพร้อมกัน


class Book(models.Model):
    """หนังสือ - อ้างอิงตาราง Book ใน ER Diagram"""

    isbn = models.CharField("เลข ISBN", max_length=30, unique=True)
    title = models.CharField("ชื่อหนังสือ", max_length=255)
    category = models.CharField("หมวดหมู่", max_length=100)
    author = models.CharField("ผู้แต่ง", max_length=150)
    publisher = models.CharField("สำนักพิมพ์", max_length=150, blank=True)
    publish_year = models.PositiveIntegerField("ปีที่พิมพ์", null=True, blank=True)
    quantity = models.PositiveIntegerField("จำนวนทั้งหมด", default=1)
    available = models.PositiveIntegerField("จำนวนคงเหลือ", default=1)
    cover_color = models.CharField("สีปกสำหรับแสดงผล", max_length=20, default="#6c63ff")

    class Meta:
        verbose_name = "หนังสือ"
        verbose_name_plural = "หนังสือ"
        ordering = ["title"]

    def __str__(self):
        return self.title

    @property
    def is_available(self):
        return self.available > 0

    @property
    def has_queue(self):
        return self.reservations.filter(status="waiting").exists()


class Borrow(models.Model):
    """การยืมหนังสือ - อ้างอิงตาราง Borrow ใน ER Diagram"""

    STATUS_CHOICES = [
        ("borrowed", "กำลังยืม"),
        ("returned", "คืนแล้ว"),
    ]

    member = models.ForeignKey(Member, on_delete=models.CASCADE, related_name="borrows", verbose_name="สมาชิก")
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name="borrows", verbose_name="หนังสือ")
    borrow_date = models.DateField("วันที่ยืม", default=timezone.localdate)
    due_date = models.DateField("วันกำหนดคืน", blank=True)
    status = models.CharField("สถานะ", max_length=20, choices=STATUS_CHOICES, default="borrowed")

    class Meta:
        verbose_name = "การยืมหนังสือ"
        verbose_name_plural = "การยืมหนังสือ"
        ordering = ["-borrow_date"]

    def save(self, *args, **kwargs):
        if not self.due_date:
            self.due_date = self.borrow_date + timedelta(days=BORROW_DAYS)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.member.full_name} ยืม {self.book.title}"

    @property
    def is_overdue(self):
        return self.status == "borrowed" and timezone.localdate() > self.due_date

    @property
    def days_overdue_now(self):
        if not self.is_overdue:
            return 0
        return (timezone.localdate() - self.due_date).days


class Return(models.Model):
    """การคืนหนังสือ - อ้างอิงตาราง Return ใน ER Diagram"""

    borrow = models.OneToOneField(Borrow, on_delete=models.CASCADE, related_name="return_info", verbose_name="รายการยืม")
    return_date = models.DateField("วันที่คืน", default=timezone.localdate)
    overdue_days = models.PositiveIntegerField("จำนวนวันที่เกินกำหนด", default=0)
    fine_amount = models.DecimalField("ค่าปรับ (บาท)", max_digits=8, decimal_places=2, default=0)

    class Meta:
        verbose_name = "การคืนหนังสือ"
        verbose_name_plural = "การคืนหนังสือ"
        ordering = ["-return_date"]

    def __str__(self):
        return f"คืน {self.borrow.book.title} โดย {self.borrow.member.full_name}"

    @classmethod
    def calculate_fine(cls, overdue_days: int) -> Decimal:
        return FINE_PER_DAY * overdue_days


class Reservation(models.Model):
    """การจองหนังสือ - อ้างอิงตาราง Reservation ใน ER Diagram"""

    STATUS_CHOICES = [
        ("waiting", "รอคิว"),
        ("notified", "แจ้งเตือนแล้ว"),
        ("completed", "รับหนังสือแล้ว"),
        ("cancelled", "ยกเลิก"),
    ]

    member = models.ForeignKey(Member, on_delete=models.CASCADE, related_name="reservations", verbose_name="สมาชิก")
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name="reservations", verbose_name="หนังสือ")
    reservation_date = models.DateField("วันที่จอง", default=timezone.localdate)
    status = models.CharField("สถานะ", max_length=20, choices=STATUS_CHOICES, default="waiting")

    class Meta:
        verbose_name = "การจองหนังสือ"
        verbose_name_plural = "การจองหนังสือ"
        ordering = ["reservation_date"]

    def __str__(self):
        return f"{self.member.full_name} จอง {self.book.title}"


class Report(models.Model):
    """รายงานสถิติ - อ้างอิงตาราง Report ใน ER Diagram"""

    admin = models.ForeignKey(AdminProfile, on_delete=models.CASCADE, related_name="reports", verbose_name="ผู้จัดทำ")
    report_name = models.CharField("ชื่อรายงาน", max_length=150)
    created_date = models.DateField("วันที่สร้าง", default=timezone.localdate)

    class Meta:
        verbose_name = "รายงาน"
        verbose_name_plural = "รายงาน"
        ordering = ["-created_date"]

    def __str__(self):
        return self.report_name
