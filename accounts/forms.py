from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from .models import Member


class MemberRegisterForm(UserCreationForm):
    """แบบฟอร์มสมัครสมาชิก (สอดคล้องกับ Flowchart ขั้นตอน 3. สมัครสมาชิก)"""

    student_id = forms.CharField(
        label="รหัสนักเรียน", max_length=20,
        widget=forms.TextInput(attrs={"class": "form-control"}))
    full_name = forms.CharField(
        label="ชื่อ-นามสกุล", max_length=150,
        widget=forms.TextInput(attrs={"class": "form-control"}))
    class_name = forms.CharField(
        label="ชั้นเรียน", max_length=50, required=False,
        widget=forms.TextInput(attrs={"class": "form-control"}))
    phone = forms.CharField(
        label="เบอร์โทรศัพท์", max_length=20, required=False,
        widget=forms.TextInput(attrs={"class": "form-control"}))
    email = forms.EmailField(
        label="อีเมล", required=False,
        widget=forms.EmailInput(attrs={"class": "form-control"}))

    class Meta:
        model = User
        fields = ["username", "password1", "password2", "student_id", "full_name", "class_name", "phone", "email"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["username"].widget.attrs.update({"class": "form-control"})
        self.fields["password1"].widget.attrs.update({"class": "form-control"})
        self.fields["password2"].widget.attrs.update({"class": "form-control"})

    def clean_student_id(self):
        student_id = self.cleaned_data["student_id"]
        if Member.objects.filter(student_id=student_id).exists():
            raise forms.ValidationError("รหัสนักเรียนนี้มีอยู่ในระบบแล้ว")
        return student_id

    def save(self, commit=True):
        user = super().save(commit=commit)
        if commit:
            Member.objects.create(
                user=user,
                student_id=self.cleaned_data["student_id"],
                full_name=self.cleaned_data["full_name"],
                class_name=self.cleaned_data["class_name"],
                phone=self.cleaned_data["phone"],
                email=self.cleaned_data["email"],
            )
        return user
