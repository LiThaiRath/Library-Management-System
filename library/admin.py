from django.contrib import admin

from .models import Book, Borrow, Report, Reservation, Return


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ("title", "author", "category", "quantity", "available")
    search_fields = ("title", "author", "isbn")
    list_filter = ("category",)


@admin.register(Borrow)
class BorrowAdmin(admin.ModelAdmin):
    list_display = ("member", "book", "borrow_date", "due_date", "status")
    list_filter = ("status",)
    search_fields = ("member__full_name", "book__title")


@admin.register(Return)
class ReturnAdmin(admin.ModelAdmin):
    list_display = ("borrow", "return_date", "overdue_days", "fine_amount")


@admin.register(Reservation)
class ReservationAdmin(admin.ModelAdmin):
    list_display = ("member", "book", "reservation_date", "status")
    list_filter = ("status",)


@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = ("report_name", "admin", "created_date")
