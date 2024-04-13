import os
import fitz
import httpx
import base64
import tempfile


DPI = 450
DEFAULT_IMAGE_FORMAT = "png"
DEFAULT_MIME_TYPE = "image/png"

def download_pdf(url: str, filename: str) -> None:
    """Download PDF from URL

    Args:
        url (str): URL of PDF
        filename (str): Filename to save PDF
    """
    with httpx.stream("GET", url) as response:
        with open(filename, "wb") as file:
            for chunk in response.iter_bytes():
                file.write(chunk)


def convert_pdf2png(filename: str) -> list[bytes]:
    """Convert PDF to images in PNG format

    Args:
        filename (str): PDF filename

    Returns:
        list[bytes]: List of images
    """
    pages = fitz.open(filename, filetype="pdf")
    images = []
    for page in pages:
        image = page.get_pixmap(dpi=DPI)
        bytes_image = image.tobytes(output=DEFAULT_IMAGE_FORMAT)
        base64_image = base64.b64encode(bytes_image).decode("utf-8")
        images.append(base64_image)
    return images


def create_request(image: bytes) -> str:
    """Create a batch request to extract data from image

    Args:
        image (bytes): Image

    Returns:
        str: Request ID
    """
   
    url = f"{os.environ.get("DOCAI_API_URL")}/extract-data-batch"
    data = {
        "schema_name": os.environ.get("DOCAI_SCHEMA_NAME"),
        "schema_version": os.environ.get("DOCAI_SCHEMA_VERSION"),
        "content": image,
        "mime_type": DEFAULT_MIME_TYPE
    }
    headers = {
        'Content-Type': 'application/json',
        'x-api-key': os.environ.get("DOCAI_API_KEY")
    }
    r = httpx.post(url, headers=headers, json=data, timeout=120)
    if r.json()["OK"]:
        r.json()["result"]


def extract_data(url: str) -> list[str]:
    """Extract data from PDF

    Args:
        url (str): URL of PDF

    Returns:
        list[bytes]: List of images
    """
    
    filename = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf").name
    download_pdf(url, filename)
    images = convert_pdf2png(filename)
    requests = [create_request(image) for image in images]
    os.unlink(filename)
    return requests


def fetch_result(request_id: str) -> dict|None:
    """Fetch results from batch request

    Args:
        request_id (str): Request ID

    Returns:
        dict: Results
    """
    url = f"{os.environ.get("DOCAI_API_URL")}/get-result/{request_id}"
    headers = {
        'Content-Type': 'application/json',
        'x-api-key': os.environ.get("DOCAI_API_KEY")
    }
    r = httpx.get(url, headers=headers, timeout=120)
    if r.json()["OK"]:
        return r.json()["result"]
