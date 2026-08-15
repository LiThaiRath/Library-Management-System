from django import forms

from .models import Book


class BookForm(forms.ModelForm):
    class Meta:
        model = Book
        fields = ["isbn", "title", "category", "author", "publisher", "publish_year", "quantity", "available", "cover_color"]
        widgets = {
            "isbn": forms.TextInput(attrs={"class": "form-control"}),
            "title": forms.TextInput(attrs={"class": "form-control"}),
            "category": forms.TextInput(attrs={"class": "form-control"}),
            "author": forms.TextInput(attrs={"class": "form-control"}),
            "publisher": forms.TextInput(attrs={"class": "form-control"}),
            "publish_year": forms.NumberInput(attrs={"class": "form-control"}),
            "quantity": forms.NumberInput(attrs={"class": "form-control"}),
            "available": forms.NumberInput(attrs={"class": "form-control"}),
            "cover_color": forms.TextInput(attrs={"class": "form-control", "type": "color"}),
        }


class BookSearchForm(forms.Form):
    q = forms.CharField(label="", required=False, widget=forms.TextInput(
        attrs={"class": "form-control", "placeholder": "ค้นหาชื่อหนังสือ, ผู้แต่ง หรือหมวดหมู่..."}))
