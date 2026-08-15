from functools import wraps

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q, Sum
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from .forms import BookForm, BookSearchForm
from .models import MAX_BORROW_LIMIT, Book, Borrow, Reservation, Return


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------

def admin_required(view_func):
    """เฉพาะผู้ดูแลระบบ (แอดมิน) เท่านั้น - Flowchart เมนู 4"""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not hasattr(request.user, "admin_profile"):
            messages.error(request, "หน้านี้สำหรับผู้ดูแลระบบเท่านั้น")
            return redirect("dashboard")
        return view_func(request, *args, **kwargs)
    return login_required(wrapper)


def member_required(view_func):
    """เฉพาะสมาชิก (นักเรียน) เท่านั้น - Flowchart เมนู 1"""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not hasattr(request.user, "member_profile"):
            messages.error(request, "หน้านี้สำหรับสมาชิกเท่านั้น")
            return redirect("dashboard")
        return view_func(request, *args, **kwargs)
    return login_required(wrapper)


def _notify_next_in_queue(book: Book):
    """เมื่อมีหนังสือคืนเข้ามา แจ้งเตือนคิวจองลำดับถัดไป - Flowchart บล็อก 5.1-5.2"""
    next_reservation = book.reservations.filter(status="waiting").order_by("reservation_date").first()
    if next_reservation:
        next_reservation.status = "notified"
        next_reservation.save()
        return next_reservation
    return None


# ---------------------------------------------------------------------------
# สมาชิก (Member) - Flowchart เมนู 1
# ---------------------------------------------------------------------------

@member_required
def member_dashboard(request):
    member = request.user.member_profile
    active_borrows = member.borrows.filter(status="borrowed").select_related("book")
    overdue_count = sum(1 for b in active_borrows if b.is_overdue)
    active_reservations = member.reservations.filter(status__in=["waiting", "notified"]).select_related("book")
    unpaid_fines = Return.objects.filter(borrow__member=member, fine_amount__gt=0).aggregate(total=Sum("fine_amount"))["total"] or 0

    context = {
        "member": member,
        "active_borrows": active_borrows,
        "overdue_count": overdue_count,
        "active_reservations": active_reservations,
        "total_fine_history": unpaid_fines,
        "borrow_limit": MAX_BORROW_LIMIT,
    }
    return render(request, "accounts/member_dashboard.html", context)


@member_required
def book_list(request):
    """1.1 ค้นหาหนังสือ"""
    form = BookSearchForm(request.GET or None)
    books = Book.objects.all()
    query = ""
    if form.is_valid() and form.cleaned_data["q"]:
        query = form.cleaned_data["q"]
        books = books.filter(
            Q(title__icontains=query) | Q(author__icontains=query) | Q(category__icontains=query)
        )

    member = request.user.member_profile
    my_active_book_ids = set(member.borrows.filter(status="borrowed").values_list("book_id", flat=True))
    my_waiting_book_ids = set(member.reservations.filter(status__in=["waiting", "notified"]).values_list("book_id", flat=True))

    return render(request, "library/book_list.html", {
        "books": books,
        "form": form,
        "query": query,
        "my_active_book_ids": my_active_book_ids,
        "my_waiting_book_ids": my_waiting_book_ids,
    })


@member_required
def borrow_book(request, book_id):
    """1.2 - 1.2.2 ตรวจสอบสต็อกและโควตา แล้วยืมหรือจองคิว"""
    book = get_object_or_404(Book, id=book_id)
    member = request.user.member_profile

    if request.method != "POST":
        return redirect("book_list")

    # 1.2.1 ตรวจสอบสถานะสมาชิก / โควตา / ค่าปรับค้าง
    if not member.is_active_member:
        messages.error(request, "บัญชีของคุณถูกระงับ ไม่สามารถยืมหนังสือได้ กรุณาติดต่อบรรณารักษ์")
        return redirect("book_list")

    active_count = member.borrows.filter(status="borrowed").count()
    if active_count >= MAX_BORROW_LIMIT:
        messages.error(request, f"คุณยืมครบโควตาสูงสุด ({MAX_BORROW_LIMIT} เล่ม) แล้ว กรุณาคืนหนังสือก่อนยืมเพิ่ม")
        return redirect("book_list")

    has_overdue = any(b.is_overdue for b in member.borrows.filter(status="borrowed"))
    if has_overdue:
        messages.error(request, "คุณมีหนังสือค้างคืนเกินกำหนด กรุณานำมาคืนก่อนยืมเล่มใหม่")
        return redirect("book_list")

    # 1.2 หนังสือมีในสต็อกหรือไม่
    if book.is_available:
        Borrow.objects.create(member=member, book=book)
        book.available -= 1
        book.save()
        messages.success(request, f"ยืมหนังสือ '{book.title}' สำเร็จ กำหนดคืนใน {settings_borrow_days()} วัน")
    else:
        # 1.2.2 จองหนังสือรอคิว
        already = Reservation.objects.filter(member=member, book=book, status__in=["waiting", "notified"]).exists()
        if already:
            messages.info(request, "คุณจองหนังสือเล่มนี้ไว้แล้ว")
        else:
            Reservation.objects.create(member=member, book=book)
            messages.success(request, f"หนังสือ '{book.title}' หมด คุณถูกจองคิวไว้แล้ว ระบบจะแจ้งเตือนเมื่อมีคืน")
    return redirect("book_list")


def settings_borrow_days():
    from .models import BORROW_DAYS
    return BORROW_DAYS


@member_required
def my_borrows(request):
    """2. นำหนังสือมาคืน (ฝั่งสมาชิกดูรายการของตน)"""
    member = request.user.member_profile
    borrows = member.borrows.select_related("book").all()
    return render(request, "library/my_borrows.html", {"borrows": borrows})


@member_required
def my_reservations(request):
    member = request.user.member_profile
    reservations = member.reservations.select_related("book").all()
    return render(request, "library/my_reservations.html", {"reservations": reservations})


@member_required
def cancel_reservation(request, reservation_id):
    reservation = get_object_or_404(Reservation, id=reservation_id, member=request.user.member_profile)
    if request.method == "POST" and reservation.status in ["waiting", "notified"]:
        reservation.status = "cancelled"
        reservation.save()
        messages.success(request, "ยกเลิกการจองแล้ว")
    return redirect("my_reservations")


# ---------------------------------------------------------------------------
# การคืนหนังสือ (ใช้ได้ทั้งสมาชิกกดคืนเอง หรือแอดมิน/บรรณารักษ์รับคืนหน้าเคาน์เตอร์)
# Flowchart บล็อก 2.1 - 2.2
# ---------------------------------------------------------------------------

@login_required
def return_book(request, borrow_id):
    borrow = get_object_or_404(Borrow, id=borrow_id, status="borrowed")

    # อนุญาตเฉพาะเจ้าของรายการยืม หรือแอดมิน
    is_owner = hasattr(request.user, "member_profile") and borrow.member == request.user.member_profile
    is_admin = hasattr(request.user, "admin_profile")
    if not (is_owner or is_admin):
        messages.error(request, "คุณไม่มีสิทธิ์ทำรายการนี้")
        return redirect("dashboard")

    if request.method != "POST":
        return redirect("dashboard")

    today = timezone.localdate()
    overdue_days = max((today - borrow.due_date).days, 0)  # 2.1 เกินกำหนดคืนหรือไม่
    fine = Return.calculate_fine(overdue_days)              # 2.1.1 คำนวณค่าปรับ

    Return.objects.create(borrow=borrow, return_date=today, overdue_days=overdue_days, fine_amount=fine)
    borrow.status = "returned"
    borrow.save()

    # 2.2 อัปเดตจำนวนหนังสือคงเหลือ +1
    book = borrow.book
    book.available += 1
    book.save()

    # 5. มีคิวจองหนังสือเล่มนี้ไหม -> แจ้งเตือนคิวถัดไป
    next_res = _notify_next_in_queue(book)

    if overdue_days > 0:
        messages.warning(request, f"รับคืนหนังสือ '{book.title}' เกินกำหนด {overdue_days} วัน ค่าปรับ {fine} บาท")
    else:
        messages.success(request, f"รับคืนหนังสือ '{book.title}' เรียบร้อย (ไม่มีค่าปรับ)")

    if next_res:
        messages.info(request, f"แจ้งเตือน {next_res.member.full_name} ว่าคิวจองหนังสือ '{book.title}' พร้อมให้ยืมแล้ว")

    return redirect(request.META.get("HTTP_REFERER") or "dashboard")


# ---------------------------------------------------------------------------
# แอดมิน / บรรณารักษ์ - Flowchart เมนู 4
# ---------------------------------------------------------------------------

@admin_required
def admin_dashboard(request):
    total_books = Book.objects.count()
    total_members = Book.objects.count()
    from accounts.models import Member
    total_members = Member.objects.count()
    active_borrows = Borrow.objects.filter(status="borrowed").count()
    overdue_borrows = [b for b in Borrow.objects.filter(status="borrowed") if b.is_overdue]
    total_fine_collected = Return.objects.aggregate(total=Sum("fine_amount"))["total"] or 0
    pending_reservations = Reservation.objects.filter(status__in=["waiting", "notified"]).count()

    context = {
        "total_books": total_books,
        "total_members": total_members,
        "active_borrows": active_borrows,
        "overdue_count": len(overdue_borrows),
        "overdue_borrows": overdue_borrows[:5],
        "total_fine_collected": total_fine_collected,
        "pending_reservations": pending_reservations,
    }
    return render(request, "accounts/admin_dashboard.html", context)


@admin_required
def admin_book_list(request):
    """4.1 จัดการข้อมูลหนังสือ (เพิ่ม/แก้ไข/ลบ)"""
    q = request.GET.get("q", "")
    books = Book.objects.all()
    if q:
        books = books.filter(Q(title__icontains=q) | Q(isbn__icontains=q))
    return render(request, "library/admin_book_list.html", {"books": books, "q": q})


@admin_required
def admin_book_create(request):
    if request.method == "POST":
        form = BookForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "เพิ่มหนังสือเรียบร้อยแล้ว")
            return redirect("admin_book_list")
    else:
        form = BookForm(initial={"available": 1, "quantity": 1})
    return render(request, "library/admin_book_form.html", {"form": form, "title": "เพิ่มหนังสือใหม่"})


@admin_required
def admin_book_update(request, book_id):
    book = get_object_or_404(Book, id=book_id)
    if request.method == "POST":
        form = BookForm(request.POST, instance=book)
        if form.is_valid():
            form.save()
            messages.success(request, "แก้ไขข้อมูลหนังสือเรียบร้อยแล้ว")
            return redirect("admin_book_list")
    else:
        form = BookForm(instance=book)
    return render(request, "library/admin_book_form.html", {"form": form, "title": f"แก้ไขหนังสือ: {book.title}"})


@admin_required
def admin_book_delete(request, book_id):
    book = get_object_or_404(Book, id=book_id)
    if request.method == "POST":
        book.delete()
        messages.success(request, "ลบหนังสือเรียบร้อยแล้ว")
    return redirect("admin_book_list")


@admin_required
def admin_member_list(request):
    """4.2 จัดการข้อมูลสมาชิก"""
    from accounts.models import Member
    q = request.GET.get("q", "")
    members = Member.objects.all()
    if q:
        members = members.filter(Q(full_name__icontains=q) | Q(student_id__icontains=q))
    return render(request, "library/admin_member_list.html", {"members": members, "q": q})


@admin_required
def admin_member_toggle_status(request, member_id):
    from accounts.models import Member
    member = get_object_or_404(Member, id=member_id)
    if request.method == "POST":
        member.status = "suspended" if member.status == "active" else "active"
        member.save()
        messages.success(request, f"อัปเดตสถานะของ {member.full_name} เป็น {member.get_status_display()}")
    return redirect("admin_member_list")


@admin_required
def admin_transactions(request):
    """4.3 ตรวจสอบรายการยืม-คืนทั้งหมด"""
    status = request.GET.get("status", "all")
    borrows = Borrow.objects.select_related("member", "book").all()
    if status == "borrowed":
        borrows = borrows.filter(status="borrowed")
    elif status == "returned":
        borrows = borrows.filter(status="returned")
    elif status == "overdue":
        borrows = [b for b in borrows.filter(status="borrowed") if b.is_overdue]
    return render(request, "library/admin_transactions.html", {"borrows": borrows, "status": status})


@admin_required
def admin_reports(request):
    """4.4 ออกรายงานสถิติหนังสือยืม/คืน/ค่าปรับ"""
    from accounts.models import Member
    from django.db.models import Count

    # นับจำนวนการยืมต่อเล่ม (เรียงมากไปน้อย)
    top_books = Book.objects.annotate(borrow_count=Count("borrows")).order_by("-borrow_count")[:10]

    total_fine = Return.objects.aggregate(total=Sum("fine_amount"))["total"] or 0
    total_returned = Return.objects.count()
    total_borrowed_all_time = Borrow.objects.count()
    total_active_borrows = Borrow.objects.filter(status="borrowed").count()
    total_overdue = len([b for b in Borrow.objects.filter(status="borrowed") if b.is_overdue])
    total_members = Member.objects.count()
    total_reservations_waiting = Reservation.objects.filter(status="waiting").count()

    context = {
        "top_books": top_books,
        "total_fine": total_fine,
        "total_returned": total_returned,
        "total_borrowed_all_time": total_borrowed_all_time,
        "total_active_borrows": total_active_borrows,
        "total_overdue": total_overdue,
        "total_members": total_members,
        "total_reservations_waiting": total_reservations_waiting,
    }
    return render(request, "library/admin_reports.html", context)
