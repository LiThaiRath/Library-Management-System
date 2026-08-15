from django.contrib import admin

from .models import AdminProfile, Member


@admin.register(Member)
class MemberAdmin(admin.ModelAdmin):
    list_display = ("student_id", "full_name", "class_name", "status")
    search_fields = ("student_id", "full_name")
    list_filter = ("status", "class_name")


@admin.register(AdminProfile)
class AdminProfileAdmin(admin.ModelAdmin):
    list_display = ("full_name", "user")
