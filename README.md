# MLS GPT

This a `GPT` for MLS listings. A user can upload a PDF file containing MLS listings and
the system will extract the data into a structured data and store it in a database.
The user can then query the database for listings through a REST API.

The REST API is intended to be used as part of the actions a custom `GPT` model
can take. The custom `GPT` model can use the REST API to query the database for
listings and use the data to generate a response.

## Installation

`cd mlsgpt && poetry install`

## ngrok setup

1. `brew install ngrok`
2. `poetry add pyngrok`
3. Create a domain in ngrok and copy `CNAME` parameters to `AWS Route 53`
4. Start ngrok with `ngrok http --domain=api.mlsgpt.docex.io 80`
5. `cd secrets && ./create_cert.sh` and copy `TXT` parameters to `AWS Route 53`
6. Copy `/etc/letsencrypt/live/docex.io/chain.pem` to `secrets` folder and upload to ngrok `TLS Certificate Authorities` section

## API

The OpenAPI documentation is available at `https://api.mlsgpt.docex.io/openapi.json`

The API is available at `https://api.mlsgpt.docex.io`

The API documentation is available at `https://api.mlsgpt.docex.io/docs`
