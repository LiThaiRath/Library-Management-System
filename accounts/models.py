from django.db import models
from django.contrib.auth.models import User


class Member(models.Model):
    """สมาชิกห้องสมุด (นักเรียน) - อ้างอิงตาราง Member ใน ER Diagram"""

    STATUS_CHOICES = [
        ("active", "ปกติ"),
        ("suspended", "ระงับการยืม"),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="member_profile")
    student_id = models.CharField("รหัสนักเรียน", max_length=20, unique=True)
    full_name = models.CharField("ชื่อ-นามสกุล", max_length=150)
    class_name = models.CharField("ชั้นเรียน", max_length=50, blank=True)
    phone = models.CharField("เบอร์โทรศัพท์", max_length=20, blank=True)
    email = models.EmailField("อีเมล", blank=True)
    status = models.CharField("สถานะ", max_length=20, choices=STATUS_CHOICES, default="active")

    class Meta:
        verbose_name = "สมาชิก"
        verbose_name_plural = "สมาชิก"

    def __str__(self):
        return f"{self.full_name} ({self.student_id})"

    @property
    def is_active_member(self):
        return self.status == "active"


class AdminProfile(models.Model):
    """ผู้ดูแลระบบ (บรรณารักษ์) - อ้างอิงตาราง Admin ใน ER Diagram"""

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="admin_profile")
    full_name = models.CharField("ชื่อ-นามสกุล", max_length=150)

    class Meta:
        verbose_name = "ผู้ดูแลระบบ"
        verbose_name_plural = "ผู้ดูแลระบบ"

    def __str__(self):
        return f"{self.full_name} (แอดมิน)"
