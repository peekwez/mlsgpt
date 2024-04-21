import os
from pyngrok import ngrok, conf


def start_ngrok(port: int):
    # ngrok http --domain=api.mlsgpt.docex.io 80
    conf.get_default().auth_token = os.environ.get("NGROK_AUTH_TOKEN")
    url = ngrok.connect(port, bind_tls=True, domain="api.mlsgpt.docex.io").public_url
    return url


def stop_ngrok():
    """Stop the ngrok tunnel."""
    ngrok.disconnect()
