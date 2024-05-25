import httpx
from rich.pretty import pprint as pp
from datetime import datetime, timedelta
from fastapi import HTTPException

from mlsgpt.db import models
from mlsgpt.dbv2 import store

CACHE_EXPIRY_MINUTES = 60 * 8
GOOGLE_PROFILE_URL = "https://www.googleapis.com/oauth2/v3/userinfo"


class UserInfoCache:
    def __init__(self):
        self.cache = {}
        self.add_user_fn = store.add_user_to_db_function()
        self.cache_duration = timedelta(minutes=CACHE_EXPIRY_MINUTES)

    async def get_user_info(self, access_token: str):
        if access_token in self.cache:
            cached_data = self.cache[access_token]
            if cached_data["expiry"] > datetime.now():
                return cached_data["data"]

        headers = {"Authorization": f"Bearer {access_token}"}
        async with httpx.AsyncClient() as client:
            response = await client.get(GOOGLE_PROFILE_URL, headers=headers)
            if response.status_code == 200:
                user_info = response.json()
                user = models.User(
                    sub=user_info["sub"],
                    email=user_info["email"],
                    name=user_info["name"],
                    email_verified=user_info["email_verified"],
                )
                self.add_user_fn(user)

                # Store in cache with expiry time
                self.cache[access_token] = {
                    "data": user,
                    "expiry": datetime.now() + self.cache_duration,
                }
                return user
            else:
                error_details = response.text
                raise HTTPException(
                    status_code=response.status_code,
                    detail=f"Failed to fetch user information from Google: {error_details}",
                )
