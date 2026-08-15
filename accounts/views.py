from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from .forms import MemberRegisterForm


def register_view(request):
    """สมัครสมาชิก - Flowchart บล็อก 3.1-3.3"""
    if request.user.is_authenticated:
        return redirect("dashboard")

    if request.method == "POST":
        form = MemberRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f"สมัครสมาชิกสำเร็จ ยินดีต้อนรับ {form.cleaned_data['full_name']}!")
            return redirect("dashboard")
        else:
            messages.error(request, "ข้อมูลไม่ถูกต้อง กรุณาตรวจสอบอีกครั้ง")
    else:
        form = MemberRegisterForm()

    return render(request, "accounts/register.html", {"form": form})


@login_required
def dashboard_router(request):
    """เข้าสู่ระบบแล้ว พาไปหน้าเมนูตามบทบาท (สมาชิก/แอดมิน) - Flowchart บล็อกเข้าสู่ระบบ"""
    if hasattr(request.user, "admin_profile"):
        return redirect("admin_dashboard")
    elif hasattr(request.user, "member_profile"):
        return redirect("member_dashboard")
    messages.error(request, "บัญชีนี้ยังไม่ได้ผูกกับสมาชิกหรือแอดมิน กรุณาติดต่อผู้ดูแลระบบ")
    return redirect("logout")
