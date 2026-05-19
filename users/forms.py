import re

from django import forms
from django.contrib.auth.forms import PasswordChangeForm
from django.core.exceptions import ValidationError

from team_finder.validators import validate_github_url

from .models import User


class RegisterForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ["name", "surname", "email"]

    def clean_email(self):
        email = self.cleaned_data.get("email")
        if email:
            normalized = User.objects.normalize_email(email)
            if User.objects.filter(email=normalized).exists():
                raise ValidationError("Этот email уже занят.")
            return normalized
        return email


class LoginForm(forms.Form):
    email = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput)


class EditProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ["name", "surname", "avatar", "about", "phone", "github_url"]

    def clean_phone(self):
        phone = self.cleaned_data.get("phone", "").strip()
        if not phone:
            raise ValidationError("Телефон обязателен.")
        if not re.match(r"^(8|\+7)\d{10}$", phone):
            raise ValidationError(
                "Телефон должен быть в формате 8XXXXXXXXXX или +7XXXXXXXXXX (10 цифр после кода)."
            )
        if phone.startswith("8"):
            phone = "+7" + phone[1:]
        qs = User.objects.filter(phone=phone)
        if self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise ValidationError("Пользователь с таким телефоном уже существует.")
        return phone

    def clean_github_url(self):
        url = self.cleaned_data.get("github_url", "").strip()
        return validate_github_url(url)


class ChangePasswordForm(PasswordChangeForm):
    pass
