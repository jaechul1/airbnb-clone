import os
import requests
from django.contrib.auth.views import PasswordChangeView
from django.views.generic import FormView, DetailView, UpdateView
from django.urls import reverse_lazy
from django.shortcuts import redirect, reverse
from django.contrib.auth import authenticate, login, logout
from django.core.files.base import ContentFile
from django.contrib import messages
from django.contrib.messages.views import SuccessMessageMixin
from . import forms, models, mixins


class LoginView(mixins.LoggedOutOnlyView, FormView):

    template_name = "users/login.html"
    form_class = forms.LoginForm
    success_url = reverse_lazy("core:home")

    def form_valid(self, form):
        email = form.cleaned_data.get("email")
        password = form.cleaned_data.get("password")
        user = authenticate(self.request, username=email, password=password)
        if user is not None:
            login(self.request, user)
            messages.success(self.request, f"Welcome back, {user.first_name}.")
        return super().form_valid(form)


def logout_view(request):
    try:
        messages.info(request, f"See you, {request.user.first_name}.")
        logout(request)
    except AttributeError:
        messages.error(request, "You can't access this page.")
    return redirect(reverse("core:home"))


class SignUpView(mixins.LoggedOutOnlyView, FormView):

    template_name = "users/signup.html"
    form_class = forms.SignUpForm
    success_url = reverse_lazy("core:home")

    def form_valid(self, form):
        form.save()
        email = form.cleaned_data.get("email")
        password = form.cleaned_data.get("password")
        user = authenticate(self.request, username=email, password=password)
        if user is not None:
            login(self.request, user)
            messages.success(self.request, f"Welcome back, {user.first_name}!")
        user.verify_email()
        return super().form_valid(form)


def verify(request, key):
    try:
        user = models.User.objects.get(email_secret=key)
        user.email_verified = True
        user.email_secret = ""
        user.save()
        # to do: add succes message
    except models.User.DoesNotExist:
        # to do: add error message
        pass
    return redirect(reverse("core:home"))


def github_login(request):
    client_id = os.environ.get("GITHUB_CLIENT")
    redirect_uri = "http://127.0.0.1:8000/users/login/github/callback"
    return redirect(
        f"https://github.com/login/oauth/authorize?client_id={client_id}&redirect_uri={redirect_uri}&scope=read:user"
    )


class GithubException(Exception):
    pass


def github_callback(request):

    try:
        client_id = os.environ.get("GITHUB_CLIENT")
        client_secret = os.environ.get("GITHUB_SECRET")
        code = request.GET.get("code", None)

        if code is not None:
            token_request = requests.post(
                f"https://github.com/login/oauth/access_token?client_id={client_id}&client_secret={client_secret}&code={code}",
                headers={"Accept": "application/json"},
            )
            token_json = token_request.json()
            error = token_json.get("error", None)

            if error is not None:
                raise GithubException("Token request failed.")

            else:
                access_token = token_json.get("access_token")
                profile_request = requests.get(
                    "https://api.github.com/user",
                    headers={
                        "Authorization": f"token {access_token}",
                        "Accept": "application/json",
                    },
                )
                profile_json = profile_request.json()
                username = profile_json.get("login", None)

                if username is not None:
                    name = profile_json.get("name")
                    email = profile_json.get("email")
                    bio = profile_json.get("bio")
                    user = models.User.objects.get(email=email)

                    try:
                        user = models.User.objects.get(email=email)
                        if user.login_method != models.User.LOGIN_GITHUB:
                            raise GithubException(
                                "You already have an account with this email."
                            )
                    except models.User.DoesNotExist:
                        user = models.User.objects.create(
                            email=email,
                            first_name=name,
                            username=email,
                            bio=bio,
                            login_method=models.User.LOGIN_GITHUB,
                            email_verfied=True,
                        )
                        user.set_unusable_password()
                        user.save()

                    login(request, user)
                    messages.success(request, f"Welcome back, {user.first_name}!")
                    return redirect(reverse("core:home"))

                else:
                    raise GithubException("Token expired.")

        else:
            raise GithubException("Failed to get the access code.")

    except GithubException as e:
        messages.error(request, e)
        return redirect(reverse("users:login"))


def kakao_login(request):
    client_id = os.environ.get("KAKAO_CLIENT")
    redirect_uri = "http://127.0.0.1:8000/users/kakao/callback"
    return redirect(
        f"https://kauth.kakao.com/oauth/authorize?client_id={client_id}&redirect_uri={redirect_uri}&response_type=code"
    )


class KakaoException(Exception):
    pass


def kakao_callback(request):

    try:
        client_id = os.environ.get("KAKAO_CLIENT")
        redirect_uri = "http://127.0.0.1:8000/users/kakao/callback"
        code = request.GET.get("code")

        token_request = requests.post(
            f"https://kauth.kakao.com/oauth/token?grant_type=authorization_code&client_id={client_id}&redirect_uri={redirect_uri}&code={code}",
            headers={"Accept": "application/json"},
        )
        token_json = token_request.json()
        error = token_json.get("error", None)

        if error is not None:
            raise KakaoException("Token request failed.")

        access_token = token_json.get("access_token")

        profile_request = requests.get(
            "https://kapi.kakao.com/v2/user/me",
            headers={
                "Authorization": f"Bearer {access_token}",
                "Accept": "application/json",
            },
        )
        profile_json = profile_request.json()
        account = profile_json.get("kakao_account", None)

        if account is None:
            raise KakaoException("Token expired.")

        if (
            not account.get("has_email")
            & account.get("is_email_valid")
            & account.get("is_email_verified")
        ):
            raise KakaoException("No valid email found.")

        profile = account.get("profile")
        nickname = profile.get("nickname")
        email = account.get("email")
        profile_image = profile.get("profile_image_url")

        try:
            user = models.User.objects.get(email=email)
            if user.login_method != models.User.LOGIN_KAKAO:
                raise KakaoException("You already have an account with this email.")

        except models.User.DoesNotExist:
            user = models.User.objects.create(
                email=email,
                username=email,
                first_name=nickname,
                login_method=models.User.LOGIN_KAKAO,
                email_verified=True,
            )

            user.set_unusable_password()
            user.save()

            if profile_image is not None:
                avatar_request = requests.get(profile_image)
                user.avatar.save(
                    f"{nickname}-avatar", ContentFile(avatar_request.content)
                )

        login(request, user)
        messages.success(request, f"Welcome back, {user.first_name}!")
        return redirect(reverse("core:home"))

    except KakaoException as e:
        messages.error(request, e)
        return redirect(reverse("users:login"))


class UserProfileView(DetailView):

    model = models.User
    context_object_name = "user_obj"


class UpdateProfileView(mixins.EmailLoginOnlyView, SuccessMessageMixin, UpdateView):

    model = models.User
    template_name = "users/update-profile.html"
    fields = (
        "avatar",
        "bio",
        "language",
        "currency",
    )
    success_message = "Profile updated."

    def get_object(self, queryset=None):
        return self.request.user

    def get_form(self, form_class=None):
        form = super().get_form(form_class=form_class)
        form.fields["avatar"].widget.attrs["placeholder"] = "Avatar"
        form.fields["bio"].widget.attrs["placeholder"] = "Bio"
        form.fields["language"].widget.attrs["placeholder"] = "Language"
        form.fields["currency"].widget.attrs["placeholder"] = "Currency"
        return form


class UpdatePasswordView(
    mixins.EmailLoginOnlyView, SuccessMessageMixin, PasswordChangeView
):

    template_name = "users/update-password.html"
    success_message = "Password updated."

    def get_form(self, form_class=None):
        form = super().get_form(form_class=form_class)
        form.fields["old_password"].widget.attrs = {"placeholder": "Old password"}
        form.fields["new_password1"].widget.attrs = {"placeholder": "New password"}
        form.fields["new_password2"].widget.attrs = {
            "placeholder": "New password confirmation"
        }
        return form

    def get_success_url(self):
        return self.request.user.get_absolute_url()
