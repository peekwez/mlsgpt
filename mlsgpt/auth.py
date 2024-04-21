import os
from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import OAuth2AuthorizationCodeBearer
from jose import jwt, JWTError  # For decoding and verifying JWT

app = FastAPI()

# Google OAuth2 configuration details
CLIENT_ID = os.environ["GOOGLE_OAUTH_CLIENT_ID"]
CLIENT_SECRET = os.environ["GOOGLE_OAUTH_CLIENT_SECRET"]
AUTHORIZATION_URL = "https://accounts.google.com/o/oauth2/v2/auth"
TOKEN_URL = "https://oauth2.googleapis.com/token"
REDIRECT_URI = "https://api.mlsgpt.docex.io/intermediate"
OPENAPI_REDIRECT_URI = "https://chat.openai.com/aip/g-509b1bca9ee4590f9382386fcc24fd7956cd99e9/oauth/callback"
SCOPE = "openid email profile"

oauth2_scheme = OAuth2AuthorizationCodeBearer(
    authorizationUrl=f"{AUTHORIZATION_URL}?response_type=code&client_id={CLIENT_ID}&redirect_uri={OPENAPI_REDIRECT_URI}&scope={SCOPE}",
    tokenUrl=TOKEN_URL,
    refreshUrl=TOKEN_URL,
    scheme_name="google_oauth2",
)


def get_current_user(token: str = Depends(oauth2_scheme)) -> dict:
    """Decode and verify JWT and return the payload as a dictionary."""
    try:
        decoded_token = jwt.decode(token, CLIENT_ID, algorithms=["RS256"])
        return decoded_token
    except JWTError as e:
        raise HTTPException(status_code=401, detail="Invalid token or token expired")
