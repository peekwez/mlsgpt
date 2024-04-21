import os
import uvicorn

import httpx
import urllib.parse

from pathlib import Path
from datetime import datetime
from typing import Optional, List
from fastapi import FastAPI, Query, Request, Depends
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from kombu import Connection, Queue, Exchange, Producer

from fastapi.responses import RedirectResponse


from mlsgpt import logger, store, tasks
from mlsgpt import auth, models, ingress

PRIVACY_HTML = Path(os.environ["ASSETS_PATH"], "privacy.html")


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
app.mount("/static", StaticFiles(directory=os.environ["ASSETS_PATH"]), name="static")
templates = Jinja2Templates(directory=os.environ["ASSETS_PATH"])


exchange = Exchange("mls", type="direct", durable=True)
file_queue = Queue("mls.process-file", exchange=exchange, routing_key="process-file")
dr: store.DataReader | None = None
con: Connection | None = None
pd: Producer | None = None


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
    # redirect_uri = request.query_params.get("redirect_uri")
    return RedirectResponse(f"{auth.OPENAPI_REDIRECT_URI}?{query_string}")


@app.post("/token", operation_id="token")
async def token(request: Request):
    """Handle the callback from Google with the authorization code."""
    request_data = await request.form()
    code = request_data.get("code")

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
    return {
        "access_token": data.get("access_token"),
        "token_type": "bearer",
        "refresh_token": data.get("refresh_token"),
        "expires_in": data.get("expires_in"),
    }


@app.get(
    "/",
    summary="API Status",
    description="Check the status of the API.",
    operation_id="home",
)
async def api_status():  # user: dict = Depends(auth.get_current_user)):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return {
        "status": "API is running",
        "description": "This API provides access to MLS property listings.",
        "timestamp": timestamp,
    }


@app.get("/privacy", response_class=HTMLResponse, operation_id="getPrivacy")
async def privacy_policy(request: Request):
    return templates.TemplateResponse(
        "privacy.html", {"request": request}, status_code=200
    )


@app.get(
    "/listings",
    response_model=List[models.Listing],
    summary="Fetch All Listings",
    description="Retrieve all listings from the database.",
    operation_id="getAllListings",
)
async def get_all_listings():  # user: dict = Depends(auth.get_current_user)):
    listings = dr.read()
    return [models.Listing(**listing) for listing in listings]


@app.get(
    "/listings/search",
    response_model=List[models.Listing],
    summary="Search Listings",
    description="Search listings based on specific attributes such as address or MLS number.",
    operation_id="searchListings",
)
async def search_listings(
    address: Optional[str] = Query(None, description="Address to filter by"),
    mls_number: Optional[str] = Query(None, description="MLS number to filter by"),
):  # user: dict = Depends(auth.get_current_user),
    listings = dr.search(address=address, mls_number=mls_number)
    return [models.Listing(**listing) for listing in listings]


@app.get(
    "/listings/nl_search",
    response_model=List[models.Listing],
    summary="Natural Language Search",
    description="Perform a natural language search to find listings based on a query that describes what you're looking for.",
    operation_id="searchListingsNL",
)
def nl_search(
    query: str, threshold: float = 0.4
):  # user: dict = Depends(auth.get_current_user)
    listings = dr.nl_search(query=query, threshold=threshold)
    return [models.Listing(**listing) for listing in listings]


# @app.post(
#     "/listings/extract",
#     response_model=models.Message,
#     summary="Extract Data",
#     description="Extract data from the uploaded MLS file upload by the user. A maximum of 3 files can be uploaded at a time.",
#     operation_id="extractData",
# )
# async def extract_data(openaiFileIdRefs: list[models.FileInfo]):
#     for file in openaiFileIdRefs:
#         pd.publish(
#             file.model_dump(),
#             exchange=tasks.mls_exchange,
#             routing_key="process-file",
#             declare=[tasks.file_queue],
#         )

#     return models.Message(
#         OK=True,
#         message="Batch extraction request submitted. This will take up to 10-20 minutes to complete.",
#     )


def run_app():
    global dr, pd
    log = logger.get_logger("api-service")

    dr = store.DataReader()
    log.info("Data reader started")

    con = tasks.create_rabbitmq_connection()
    log.info("RabbitMQ connection established")

    pd = con.Producer(serializer="json")
    log.info("File queue producer started")

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
