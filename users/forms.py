import re

from django import forms
from django.contrib.auth import authenticate
from django.contrib.auth.forms import AuthenticationForm, PasswordChangeForm
from django.core.exceptions import ValidationError

from .models import User
from .utils import validate_github_url, validate_phone_number


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
    email = forms.EmailField(
        label="Email",
        widget=forms.EmailInput(attrs={'class': 'form-control'})
    )
    password = forms.CharField(
        label="Пароль",
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )

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
        return validate_phone_number(phone, self.instance)

    def clean_github_url(self):
        github_url = self.cleaned_data.get("github_url")
        return validate_github_url(github_url)


class UserChangePasswordForm(PasswordChangeForm):
    old_password = forms.CharField(
        widget=forms.PasswordInput,
        label="Текущий пароль"
    )
    new_password1 = forms.CharField(
        widget=forms.PasswordInput,
        label="Новый пароль"
    )
    new_password2 = forms.CharField(
        widget=forms.PasswordInput,
        label="Подтверждение пароля"
    )
    