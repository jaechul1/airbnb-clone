from django.urls import path
from . import views

app_name = "users"

urlpatterns = [
    path("login/", views.LoginView.as_view(), name="login"),
    path("github/", views.github_login, name="github-login"),
    path("github/callback/", views.github_callback, name="github-callback"),
    path("kakao/", views.kakao_login, name="kakao-login"),
    path("kakao/callback/", views.kakao_callback, name="kakao-callback"),
    path("logout/", views.logout_view, name="logout"),
    path("signup/", views.SignUpView.as_view(), name="signup"),
    path("verify/<str:key>/", views.verify, name="verify"),
    path("<int:pk>/", views.UserProfileView.as_view(), name="profile"),
    path("update-profile/", views.UpdateProfileView.as_view(), name="update"),
    path("update-password/", views.UpdatePasswordView.as_view(), name="password"),
    path("switch-hosting/", views.switch_hosting, name="switch-hosting"),
]
