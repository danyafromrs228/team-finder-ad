from django import forms
from django.contrib.auth.forms import AuthenticationForm, PasswordChangeForm
from django.contrib.auth import authenticate
from django.core.exceptions import ValidationError
from .models import User
import re


class UserRegistrationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput, label="Пароль")

    class Meta:
        model = User
        fields = ["name", "surname", "email", "password"]

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"])
        if commit:
            user.save()
        return user


class UserLoginForm(forms.Form):
    email = forms.EmailField(label="Email", widget=forms.EmailInput(attrs={'class': 'form-control'}))
    password = forms.CharField(label="Пароль", widget=forms.PasswordInput(attrs={'class': 'form-control'}))

    def clean(self):
        cleaned_data = super().clean()
        email = cleaned_data.get('email')
        password = cleaned_data.get('password')
        
        if email and password:
            try:
                user = User.objects.get(email=email)
                self.user = authenticate(username=user.email, password=password)
                if not self.user:
                    raise forms.ValidationError("Неверный email или пароль")
            except User.DoesNotExist:
                raise forms.ValidationError("Неверный email или пароль")
        return cleaned_data


class UserProfileEditForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ["name", "surname", "avatar", "about", "phone", "github_url"]

    def clean_phone(self):
        phone = self.cleaned_data.get("phone")
        if phone:
            if not re.match(r"^(\+7|8)?\d{10}$", phone):
                raise ValidationError("Номер телефона должен быть в формате 8XXXXXXXXXX или +7XXXXXXXXXX")

            if phone.startswith("8"):
                phone = "+7" + phone[1:]

            user_id = self.instance.id if self.instance else None
            if User.objects.filter(phone=phone).exclude(id=user_id).exists():
                raise ValidationError("Пользователь с таким номером телефона уже существует")

        return phone

    def clean_github_url(self):
        github_url = self.cleaned_data.get("github_url")
        if github_url and "github.com" not in github_url:
            raise ValidationError("Ссылка должна вести на GitHub")
        return github_url


class UserChangePasswordForm(PasswordChangeForm):
    old_password = forms.CharField(widget=forms.PasswordInput, label="Текущий пароль")
    new_password1 = forms.CharField(widget=forms.PasswordInput, label="Новый пароль")
    new_password2 = forms.CharField(widget=forms.PasswordInput, label="Подтверждение пароля")
    