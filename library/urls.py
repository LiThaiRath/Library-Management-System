from django.urls import path

from . import views

urlpatterns = [
    # สมาชิก
    path("dashboard/member/", views.member_dashboard, name="member_dashboard"),
    path("books/", views.book_list, name="book_list"),
    path("books/<int:book_id>/borrow/", views.borrow_book, name="borrow_book"),
    path("my-borrows/", views.my_borrows, name="my_borrows"),
    path("my-reservations/", views.my_reservations, name="my_reservations"),
    path("reservations/<int:reservation_id>/cancel/", views.cancel_reservation, name="cancel_reservation"),
    path("borrows/<int:borrow_id>/return/", views.return_book, name="return_book"),

    # แอดมิน (ใช้ prefix "manage/" เพื่อไม่ให้ชนกับ Django admin ที่ "/admin/")
    path("dashboard/admin/", views.admin_dashboard, name="admin_dashboard"),
    path("manage/books/", views.admin_book_list, name="admin_book_list"),
    path("manage/books/add/", views.admin_book_create, name="admin_book_create"),
    path("manage/books/<int:book_id>/edit/", views.admin_book_update, name="admin_book_update"),
    path("manage/books/<int:book_id>/delete/", views.admin_book_delete, name="admin_book_delete"),
    path("manage/members/", views.admin_member_list, name="admin_member_list"),
    path("manage/members/<int:member_id>/toggle/", views.admin_member_toggle_status, name="admin_member_toggle_status"),
    path("manage/transactions/", views.admin_transactions, name="admin_transactions"),
    path("manage/reports/", views.admin_reports, name="admin_reports"),
]
