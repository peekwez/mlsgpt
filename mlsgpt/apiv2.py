import os
import uvicorn

import httpx
import urllib.parse

from pathlib import Path
from datetime import datetime
from fastapi import FastAPI, Request, Depends, status
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse


from mlsgpt import logger, auth, ingress, core
from mlsgpt.dbv2 import models, store

ASSETS_PATH = Path(__file__).parent.parent / "assets"
PRIVACY_HTML = ASSETS_PATH / "privacy.html"


def handle_error(e: Exception):
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    error = models.ErrorResponse.model_validate(**core.process_error(e))
    return JSONResponse(content=error.model_dump(), status_code=status_code)


app = FastAPI(
    title="MLS GPT API",
    description="API for MLS property listings. This API provides access to MLS property listings and allows you to search for listings based on specific attributes.",
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


@app.post(
    "/listings",
    response_model=models.ListingsResponse,
    summary="Fetch All Listings",
    description="Retrieve all listings from the database. Returns 10 items by default and a maximum of 20. Use the limit and offset parameters to paginate the results.",
    operation_id="getAllListings",
    dependencies=[Depends(auth.get_current_user)],
)
async def get_all_listings(params: models.BaseSearchFilters) -> models.ListingsResponse:
    try:
        props = reader.get_properties(limit=params.limit, offset=params.offset)
    except Exception as e:
        return handle_error(e)

    return models.ListingsResponse(
        num_items=len(props),
        offset=params.offset,
        items=[models.Property.model_validate(prop) for prop in props],
    )


@app.post(
    "/listings/search",
    response_model=models.ListingsResponse,
    summary="Search Listings",
    description="Search listings based on specific attributes such as address, MLS number, unit type, days on market, number of bedrooms or washrooms. Returns 10 items by default and a maximum of 20. Use the limit and offset parameters to paginate the results.",
    operation_id="searchListings",
    dependencies=[Depends(auth.get_current_user)],
)
async def search_listings(params: models.ListingSearchFilters):
    try:
        props = reader.search(
            limit=params.limit,
            offset=params.offset,
            StreetAddress=params.address,
            City=params.city,
            PostalCode=params.postal_code,
            Province=params.province,
            Type=params.type,
            BedroomsTotal=params.bedrooms,
            BathroomTotal=params.washrooms,
            MaxPrice=params.max_price,
            MinPrice=params.min_price,
            MaxLease=params.max_lease,
            MinLease=params.min_lease,
        )
    except Exception as e:
        return handle_error(e)

    return models.ListingsResponse(
        num_items=len(props),
        offset=params.offset,
        items=[models.Property.model_validate(prop) for prop in props],
    )


@app.post(
    "/listings/nl_search",
    response_model=models.ListingsResponse,
    summary="Natural Language Search",
    description="Uses natural language search to find listings based on a query that describes what you're looking for. Returns 10 items by default and a maximum of 20. Use the limit and offset parameters to paginate the results. The threshold parameter can be used to adjust the similarity threshold for the search.",
    operation_id="searchListingsNaturalLanguage",
    dependencies=[Depends(auth.get_current_user)],
)
async def nl_search(
    params: models.ListingNaturalLanguageSearch,
) -> models.ListingsResponse:
    try:
        props = reader.semantic_search(
            query=params.query,
            limit=params.limit,
            offset=params.offset,
            threshold=params.threshold,
        )
    except Exception as e:
        return handle_error(e)

    return models.ListingsResponse(
        num_items=len(props),
        offset=params.offset,
        items=[models.Property.model_validate(prop) for prop in props],
    )


@app.get(
    "/stats/info",
    response_model=models.StatsInfoResponse,
    summary="Statistics Info",
    description="Get statistics information. It returns the values that can be used to query all the statistics endpoints. Provide this information to a user to help them query the statistics endpoints.",
    operation_id="getStatsInfo",
)
async def get_stats_info():
    try:
        stats_info = reader.get_stats_info()
    except Exception as e:
        return handle_error(e)

    return models.StatsInfoResponse(
        num_items=len(stats_info),
        items=[models.StatsInfo.model_validate(stat) for stat in stats_info],
    )


@app.post(
    "/stats/city",
    response_model=models.CityStatsResponse,
    summary="City Statistics",
    description="Get statistics for a specific city.",
    operation_id="getCityStats",
    # dependencies=[Depends(auth.get_current_user)],
)
async def get_city_stats(params: models.CityStatsRequest):
    try:
        stats = reader.get_city_stats(city=params.city)
    except Exception as e:
        return handle_error(e)

    return models.CityStatsResponse(
        num_items=len(stats),
        items=[models.CityStats.model_validate(stat) for stat in stats],
    )


@app.post(
    "/stats/city-type",
    response_model=models.CityTypeStatsResponse,
    summary="City Type Statistics",
    description="Get statistics for a specific city and property type.",
    operation_id="getCityTypeStats",
    # dependencies=[Depends(auth.get_current_user)],
)
async def get_city_type_stats(params: models.CityTypeStatsRequest):
    try:
        stats = reader.get_city_type_stats(city=params.city, type=params.type)
    except Exception as e:
        return handle_error(e)

    return models.CityTypeStatsResponse(
        num_items=len(stats),
        items=[models.CityTypeStats.model_validate(stat) for stat in stats],
    )


@app.post(
    "/stats/city-property-type",
    response_model=models.CityPropertyTypeStatsResponse,
    summary="City Property Type Statistics",
    description="Get statistics for a specific city and property type.",
    operation_id="getCityPropertyTypeStats",
    # dependencies=[Depends(auth.get_current_user)],
)
async def get_city_property_type_stats(params: models.CityPropertyTypeStatsRequest):
    try:
        stats = reader.get_city_property_type_stats(
            city=params.city, property_type=params.property_type
        )
    except Exception as e:
        return handle_error(e)

    return models.CityPropertyTypeStatsResponse(
        num_items=len(stats),
        items=[models.CityPropertyTypeStats.model_validate(stat) for stat in stats],
    )


@app.post(
    "/stats/city-bedrooms-total",
    response_model=models.CityBedroomsStatsResponse,
    summary="City Bedrooms Statistics",
    description="Get statistics for a specific city and number of bedrooms.",
    operation_id="getCityBedroomsStats",
    # dependencies=[Depends(auth.get_current_user)],
)
async def get_city_bedrooms_stats(params: models.CityBedroomsStatsRequest):
    try:
        stats = reader.get_city_bedrooms_stats(
            city=params.city, bedrooms=params.bedrooms
        )
    except Exception as e:
        return handle_error(e)

    return models.CityBedroomsStatsResponse(
        num_items=len(stats),
        items=[models.CityBedroomsStats.model_validate(stat) for stat in stats],
    )


def run_app(ngrok: bool = False):
    global reader
    log = logger.get_logger("api-service")

    reader = store.DataReader()
    log.info("Data reader started")

    port = int(os.environ.get("PORT", 8000))
    log.info("API service initialized")

    if ngrok:
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
