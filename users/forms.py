from django import forms
from django.contrib.auth.password_validation import validate_password
from . import models


class LoginForm(forms.Form):
    """User login form"""

    email = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput)

    def clean(self):
        email = self.cleaned_data.get("email")
        password = self.cleaned_data.get("password")
        try:
            user = models.User.objects.get(username=email)
            if user.check_password(password):
                return self.cleaned_data
            else:
                self.add_error("password", forms.ValidationError("Wrong password"))
        except models.User.DoesNotExist:
            self.add_error("email", forms.ValidationError("No user with such email"))


class SignUpForm(forms.Form):
    """User sign up form"""

    first_name = forms.CharField(max_length=80)
    last_name = forms.CharField(max_length=80)
    email = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput)
    passwordC = forms.CharField(widget=forms.PasswordInput, label="Confirm Password")

    def clean_email(self):
        email = self.cleaned_data.get("email")
        try:
            models.User.objects.get(email=email)
            raise forms.ValidationError("Email already exists")
        except models.User.DoesNotExist:
            return email

    def clean_password(self):
        password = self.cleaned_data.get("password")
        validate_password(password)
        return password

    def clean_passwordC(self):
        password = self.cleaned_data.get("password")
        passwordC = self.cleaned_data.get("passwordC")
        if password != passwordC:
            raise forms.ValidationError("Password confirmation failed")
        else:
            return password

    def save(self):
        first_name = self.cleaned_data.get("first_name")
        last_name = self.cleaned_data.get("last_name")
        email = self.cleaned_data.get("email")
        password = self.cleaned_data.get("password")
        user = models.User.objects.create_user(
            username=email, email=email, password=password
        )  # different from objects.create(), this contains password encryption
        user.first_name = first_name
        user.last_name = last_name
        user.save()
