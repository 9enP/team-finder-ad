import re
from urllib.parse import urlparse

from django import forms
from django.core.exceptions import ValidationError

from .models import User


class RegisterForm(forms.Form):
    name = forms.CharField(max_length=124)
    surname = forms.CharField(max_length=124)
    email = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput)

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

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name in ("avatar", "about", "github_url"):
            self.fields[field_name].required = False

    def clean_phone(self):
        phone = (self.cleaned_data.get("phone") or "").strip()
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
        url = (self.cleaned_data.get("github_url") or "").strip()
        if not url:
            return ""
        parsed = urlparse(url)
        if not parsed.scheme or not parsed.netloc:
            raise ValidationError("Укажите корректный URL.")
        if "github.com" not in url.lower():
            raise ValidationError("Ссылка должна вести на github.com.")
        return url


class ChangePasswordForm(forms.Form):
    old_password = forms.CharField(widget=forms.PasswordInput)
    new_password1 = forms.CharField(
        widget=forms.PasswordInput,
        label="Новый пароль",
    )
    new_password2 = forms.CharField(
        widget=forms.PasswordInput,
        label="Повторите новый пароль",
    )

    def __init__(self, user, *args, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super().clean()
        old_password = cleaned_data.get("old_password")
        new_password1 = cleaned_data.get("new_password1")
        new_password2 = cleaned_data.get("new_password2")

        if old_password and not self.user.check_password(old_password):
            self.add_error("old_password", ValidationError("Неверный текущий пароль."))

        if new_password1 and new_password2 and new_password1 != new_password2:
            self.add_error(
                "new_password2",
                ValidationError("Новые пароли не совпадают."),
            )

        return cleaned_data
