from django.contrib import messages
from django.urls import reverse_lazy
from django.shortcuts import redirect, reverse
from django.contrib.auth.mixins import UserPassesTestMixin, LoginRequiredMixin


class LoggedOutOnlyView(UserPassesTestMixin):
    def test_func(self):
        return not self.request.user.is_authenticated

    def handle_no_permission(self):
        messages.error(self.request, "You can't access this page.")
        return redirect(reverse("core:home"))


class EmailLoginOnlyView(UserPassesTestMixin):
    def test_func(self):
        try:
            return self.request.user.login_method == "email"
        except AttributeError:
            return False

    def handle_no_permission(self):
        messages.error(self.request, "You can't access this page.")
        return redirect(reverse("core:home"))


class LoggedInOnlyView(LoginRequiredMixin):

    login_url = reverse_lazy("users:login")
