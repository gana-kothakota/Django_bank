from django.urls import path 
from .views import (
    CustomTokenCreateView,
    CustomTokenRefreshView,
    LogotApiView,
    otpverifyview
)

urlpatterns = [
    path("login/", CustomTokenCreateView.as_view(), name="login"),
    path("logout/", LogotApiView.as_view(), name="logout"),
    path("refresh/", CustomTokenRefreshView.as_view(), name="refresh"),
    path("otp-verify/", otpverifyview.as_view(), name="otp-verify"),
]