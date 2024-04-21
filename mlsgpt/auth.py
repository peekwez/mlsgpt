import os

from fastapi import Depends
from fastapi.security import OAuth2AuthorizationCodeBearer

from mlsgpt import cache

# Google OAuth2 configuration details
CLIENT_ID = os.environ["GOOGLE_OAUTH_CLIENT_ID"]
CLIENT_SECRET = os.environ["GOOGLE_OAUTH_CLIENT_SECRET"]
OPENAPI_REDIRECT_URI = os.environ["OPENAPI_REDIRECT_URI"]

AUTHORIZATION_URL = "https://accounts.google.com/o/oauth2/v2/auth"
TOKEN_URL = "https://oauth2.googleapis.com/token"
REDIRECT_URI = "https://api.mlsgpt.docex.io/intermediate"
SCOPE = "openid email profile"

user_info_cache = cache.UserInfoCache()

oauth2_scheme = OAuth2AuthorizationCodeBearer(
    authorizationUrl=f"{AUTHORIZATION_URL}?response_type=code&client_id={CLIENT_ID}&redirect_uri={OPENAPI_REDIRECT_URI}&scope={SCOPE}",
    tokenUrl=TOKEN_URL,
    refreshUrl=TOKEN_URL,
    scheme_name="OAuth2",
)


async def get_current_user(access_token: str = Depends(oauth2_scheme)) -> dict:
    return await user_info_cache.get_user_info(access_token)
