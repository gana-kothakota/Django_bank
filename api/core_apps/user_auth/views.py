from typing import Any, Optional

from django.conf import settings
from django.contrib.auth import get_user_model
from django.utils import timezone
from djoser.views import TokenCreateView
from loguru import logger
from rest_framework import permissions, status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenRefreshView

from .emails import send_otp_email
from .utils import generate_otp


User = get_user_model()


def set_auth_cookies(
    response: Response, access_token: str, refresh_token: Optional[str] = None
) -> None:
    access_token_lifetime = settings.SIMPLE_JWT["ACCESS_TOKEN_LIFETIME"].total_seconds()
    cookie_settings = {
        "path": settings.COOKIE_PATH,
        "httponly": settings.COOKIE_HTTPONLY,
        "secure": settings.COOKIE_SECURE,
        "samesite": settings.COOKIE_SAMESITE,
        "max_age": int(access_token_lifetime),
    }
    cookie_name = getattr(settings, "COOKIE_NAME", "access")
    response.set_cookie(cookie_name, access_token, **cookie_settings)

    if refresh_token:
        refresh_token_lifetime = settings.SIMPLE_JWT["REFRESH_TOKEN_LIFETIME"].total_seconds()
        refresh_cookie_settings = cookie_settings.copy()
        refresh_cookie_settings["max_age"] = int(refresh_token_lifetime)
        refresh_cookie_name = getattr(settings, "REFRESH_COOKIE_NAME", "refresh_token")
        response.set_cookie(refresh_cookie_name, refresh_token, **refresh_cookie_settings)

    logged_in_cookie_settings = cookie_settings.copy()
    logged_in_cookie_settings["httponly"] = False
    response.set_cookie("logged_in", "true", **logged_in_cookie_settings)


class CustomTokenCreateView(TokenCreateView):
    def _action(self, serializer) -> Response:
        user = serializer.user
        is_locked = getattr(user, "is_locked_out", getattr(user, "is_locked", False))
        if is_locked:
            lockout_duration = getattr(
                settings, "LOCKOUT_DURATION", getattr(settings, "LOCKOUT_MINUTES", None)
            )
            lockout_minutes = (
                int(lockout_duration.total_seconds() // 60)
                if hasattr(lockout_duration, "total_seconds")
                else int(lockout_duration or 1)
            )
            return Response(
                {
                    "error": f"Account is locked due to failed login attempts. Try again in {lockout_minutes} minutes."
                },
                status=status.HTTP_403_FORBIDDEN,
            )

        if hasattr(user, "reset_failed_login_attempts"):
            user.reset_failed_login_attempts()
        elif hasattr(user, "rest_failed_login_attempts"):
            user.rest_failed_login_attempts()

        otp = generate_otp()
        user.set_otp(otp)
        send_otp_email(user.email, otp)
        logger.info(f"otp sent successfully {otp} to user {user.email}")

        return Response({"msg": "otp sent to your email"}, status=status.HTTP_200_OK)

    def post(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        serializer = self.get_serializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
        except Exception as e:
            email = request.data.get("email")
            user = User.objects.filter(email=email).first()
            if user:
                if hasattr(user, "handle_failed_login_attempts"):
                    user.handle_failed_login_attempts()
                elif hasattr(user, "handel_failed_login_attempt"):
                    user.handel_failed_login_attempt()

                failed_attempts = getattr(
                    user, "failed_login_attempts", getattr(user, "get_failed_login_attempts", lambda: 0)()
                )
                logger.error(f"login failed for user {email} error: {str(e)}")

                max_attempts = getattr(
                    settings, "MAX_FAILED_LOGIN_ATTEMPTS", getattr(settings, "LOGIN_ATTEMPTS", 3)
                )
                if failed_attempts >= max_attempts:
                    lockout_duration = getattr(
                        settings, "LOCKOUT_DURATION", getattr(settings, "LOCKOUT_MINUTES", None)
                    )
                    lockout_minutes = (
                        int(lockout_duration.total_seconds() // 60)
                        if hasattr(lockout_duration, "total_seconds")
                        else int(lockout_duration or 1)
                    )
                    return Response(
                        {
                            "error": f"Account is locked due to failed login attempts. Try again in {lockout_minutes} minutes."
                        },
                        status=status.HTTP_403_FORBIDDEN,
                    )
                else:
                    return Response(
                        {"error": "Invalid credentials"},
                        status=status.HTTP_401_UNAUTHORIZED,
                    )
            return Response(
                {"error": "Invalid credentials"},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        return self._action(serializer)


class CustomTokenRefreshView(TokenRefreshView):
    def post(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        refresh_token = request.data.get("refresh")

        if refresh_token:
            request.data["refresh"] = refresh_token
        refresh_res = super().post(request, *args, **kwargs)
        
        if refresh_res.status_code == status.HTTP_200_OK:
            access_token = refresh_res.data.get("access")
            refresh_token = refresh_res.data.get("refresh")
            
            if access_token and refresh_token:
                set_auth_cookies(refresh_res, access_token, refresh_token)

            refresh_res.data.pop("refresh", None)
            refresh_res.data.pop("access", None)
            refresh_res.data["msg"] = "Tokens refreshed successfully"
        else:
            refresh_res.data["message"] =(
                "Refresh token is invalid or expired. Please log in again."
            )
            logger.error(f"Refresh token invalid or expired: {refresh_res.data}")
        return refresh_res 
class otpverifyview(APIView):
    permission_classes = [permissions.AllowAny]
    def post(self, request):
        otp = request.data.get("otp")
        if not otp:
            return Response({"error": "OTP is required"}, status=status.HTTP_400_BAD_REQUEST)
        user = User.objects.filter(otp=otp, otp_expiry_time__gt =timezone.now()).first()
        if not user:
            return Response({"error": "Invalid or expired OTP"}, status=status.HTTP_400_BAD_REQUEST)
        
        is_locked = getattr(user, "is_locked_out", getattr(user, "is_locked", False))
        if is_locked:
            return Response({"error": "Account is locked"}, status=status.HTTP_403_FORBIDDEN)
        user.verify_otp(otp)

        refresh = RefreshToken.for_user(user)
        access = str(refresh.access_token)
        refresh_token = str(refresh)

        response = Response({"msg": "OTP verified successfully"}, status=status.HTTP_200_OK)
        set_auth_cookies(response, access, refresh_token)
        logger.info(f"OTP verified successfully for user {user.email}") 
        return response 
class LogotApiView(APIView):
    def post(self, request, *args, **kwargs):
        response = Response({"msg": "Logged out successfully"}, status=status.HTTP_200_OK)
        cookie_name = getattr(settings, "COOKIE_NAME", "access")
        refresh_cookie_name = getattr(settings, "REFRESH_COOKIE_NAME", "refresh_token")
        response.delete_cookie(cookie_name, path=settings.COOKIE_PATH)
        response.delete_cookie(refresh_cookie_name, path=settings.COOKIE_PATH)
        response.delete_cookie("logged_in", path=settings.COOKIE_PATH)
        return response
    

        
        
            
        

        
        
        