import os
import uvicorn

import boto3
import httpx
import urllib.parse

from pathlib import Path
from datetime import datetime
from typing import Optional, List
from fastapi import FastAPI, Query, Request, Depends
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse


from mlsgpt import logger, store, tasks
from mlsgpt import auth, models, ingress

ASSETS_PATH = Path(__file__).parent.parent / "assets"
PRIVACY_HTML = ASSETS_PATH / "privacy.html"


app = FastAPI(
    title="MLS GPT API",
    description="API for MLS property listings. This API provides access to MLS property listings and allows you to search for listings based on specific attributes. You can also upload MLS files to extract data and add it to the database.",
    servers=[
        {"url": "https://api.mlsgpt.docex.io", "description": "Production server"},
    ],
    version="0.1",
    openapi_tags=[
        {
            "name": "listings",
            "description": "Operations related to MLS property listings",
        },
    ],
    swagger_ui_oauth2_redirect_url="/authorize",
)

sqs = boto3.client("sqs")
reader: store.DataReader | None = None

app.mount("/static", StaticFiles(directory=ASSETS_PATH), name="static")
templates = Jinja2Templates(ASSETS_PATH)


@app.get("/login", operation_id="login")
def login(request: Request):
    """Redirect user to Google for authentication."""
    state = request.query_params.get("state")

    query_params = {
        "response_type": "code",
        "client_id": auth.CLIENT_ID,
        "redirect_uri": auth.REDIRECT_URI,
        "scope": auth.SCOPE,
        "access_type": "offline",  # Necessary for refresh token
        "prompt": "consent",  # Force to show the consent screen
        "state": state or "",
    }
    query_string = urllib.parse.urlencode(query_params)
    full_auth_url = f"{auth.AUTHORIZATION_URL}?{query_string}"
    return RedirectResponse(url=full_auth_url)


@app.get("/intermediate", operation_id="intermediate")
async def intermediate(request: Request):
    code = request.query_params.get("code")
    state = request.query_params.get("state")
    # Redirect to OpenAI's callback URL with code and state

    params = {"code": code, "state": state}
    query_string = urllib.parse.urlencode(params)
    return RedirectResponse(f"{auth.OPENAPI_REDIRECT_URI}?{query_string}")


@app.post("/token", operation_id="token")
async def token(request: Request):
    """Handle the callback from Google with the authorization code."""
    request_data = await request.form()
    code = request_data.get("code")
    # code = request.query_params.get("code")

    data = {
        "code": code,
        "client_id": auth.CLIENT_ID,
        "client_secret": auth.CLIENT_SECRET,
        "grant_type": "authorization_code",
        "redirect_uri": auth.REDIRECT_URI,
    }
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    async with httpx.AsyncClient() as client:
        response = await client.post(auth.TOKEN_URL, data=data, headers=headers)

    data = response.json()
    response = {
        "access_token": data.get("access_token"),
        "token_type": "Bearer",
        "refresh_token": data.get("refresh_token"),
        "expires_in": data.get("expires_in"),
    }
    return response


@app.get("/privacy", response_class=HTMLResponse, operation_id="getPrivacy")
async def privacy_policy(request: Request):
    return templates.TemplateResponse(
        "privacy.html", {"request": request}, status_code=200
    )


@app.get(
    "/",
    summary="API Status",
    description="Check the status of the API.",
    operation_id="home",
    dependencies=[Depends(auth.get_current_user)],
)
async def api_status():
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return {
        "status": "API is running",
        "description": "This API provides access to MLS property listings.",
        "timestamp": timestamp,
    }


@app.get(
    "/listings",
    response_model=List[models.Listing],
    summary="Fetch All Listings",
    description="Retrieve all listings from the database. Returns 10 items by default and a maximum of 20. Use the limit and offset parameters to paginate the results.",
    operation_id="getAllListings",
    dependencies=[Depends(auth.get_current_user)],
)
async def get_all_listings(limit: int = 10, offset: int = 0):
    listings = reader.read(limit=limit, offset=offset)
    return [models.Listing(**listing) for listing in listings]


@app.get(
    "/listings/search",
    response_model=List[models.Listing],
    summary="Search Listings",
    description="Search listings based on specific attributes such as address or MLS number. Returns 10 items by default and a maximum of 20. Use the limit and offset parameters to paginate the results.",
    operation_id="searchListings",
    dependencies=[Depends(auth.get_current_user)],
)
async def search_listings(
    address: Optional[str] = Query(None, description="Address to filter by"),
    mls_number: Optional[str] = Query(None, description="MLS number to filter by"),
    limit: int = 10,
    offset: int = 0,
):
    listings = reader.search(
        address=address, mls_number=mls_number, limit=limit, offset=offset
    )
    return [models.Listing(**listing) for listing in listings]


@app.get(
    "/listings/nl_search",
    response_model=List[models.Listing],
    summary="Natural Language Search",
    description="Uses natural language search to find listings based on a query that describes what you're looking for. Returns 10 items by default and a maximum of 20. Use the limit and offset parameters to paginate the results. The threshold parameter can be used to adjust the similarity threshold for the search.",
    operation_id="searchListingsNL",
    dependencies=[Depends(auth.get_current_user)],
)
def nl_search(query: str, threshold: float = 0.4, limit: int = 10, offset: int = 0):
    listings = reader.nl_search(
        query=query, threshold=threshold, limit=limit, offset=offset
    )
    return [models.Listing(**listing) for listing in listings]


@app.post(
    "/listings/extract",
    response_model=models.Message,
    summary="Extract Data",
    description="Extract data from the uploaded MLS file upload by the user. A maximum of 2 files can be uploaded at a time.",
    operation_id="extractData",
    dependencies=[Depends(auth.get_current_user)],
)
async def extract_data(req: models.OpenAIFileIdRefs):
    for file in req.openaiFileIdRefs:
        sqs.send_message(
            QueueUrl=tasks.file_queue_url,
            MessageBody=file.model_dump_json(),
        )

    return models.Message(
        OK=True,
        message="Batch extraction request submitted. This will take up to 10-20 minutes to complete.",
    )


def run_app():
    global reader
    log = logger.get_logger("api-service")

    reader = store.DataReader()
    log.info("Data reader started")

    port = int(os.environ.get("PORT", 8000))
    log.info("API service initialized")

    public_url = ingress.start_ngrok(port)  # Start ngrok and get the public URL
    log.info(f"The ngrok tunnel is running at: {public_url}")
    try:
        # Use uvicorn to run the app. The Uvicorn server will be stopped using Ctrl+C in the terminal
        config = uvicorn.config.LOGGING_CONFIG
        config["formatters"]["default"]["fmt"] = logger.LOG_FORMAT
        config["formatters"]["access"]["fmt"] = logger.LOG_FORMAT
        uvicorn.run(app, host="0.0.0.0", port=port)
    except KeyboardInterrupt:
        ingress.stop_ngrok  # Ensure ngrok tunnel is closed when the app stops
        print("Application has been stopped.")
