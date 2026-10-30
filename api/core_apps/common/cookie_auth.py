from typing import Optional, Tuple
from django.conf import settings
from loguru import logger
from rest_framework.request import Request
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.tokens import Token
from rest_framework_simplejwt.exceptions import TokenError
from core_apps.user_auth.models import User

class CookieAuthentication(JWTAuthentication):
    def authenticate(self, request: Request) -> Optional[Tuple[User, Token]]:
        header = self.get_header(request)
        raw_token = None 

        if header is not None: 
            raw_token = self.get_raw_token(header)
        elif settings.COOKIE_NAME in request.COOKIES: 
            raw_token = request.COOKIES[settings.COOKIE_NAME]
        if raw_token is not None:
            try:
                validated_token = self.get_validated_token(raw_token)
                return self.get_user(validated_token), validated_token
            except TokenError as e:
                logger.error(f'Token Error: {str(e)}')
        return None