import os
import sys
import time
import fitz
import httpx
import base64
import tempfile
import requests
import multiprocessing


DPI = 450
DEFAULT_IMAGE_FORMAT = "png"
DEFAULT_MIME_TYPE = "image/png"

def download_file(url: str, filename: str) -> None:
    """Download PDF from URL

    Args:
        url (str): URL of PDF
        filename (str): Filename to save PDF
    """
    with requests.get(url, stream=True) as r:
        r.raise_for_status()
        with open(filename, 'wb') as f:
            for chunk in r.iter_content(chunk_size=8192): 
                f.write(chunk)



def convert_pdf2png(filename: str) -> list[str]:
    """Convert PDF to images in PNG format

    Args:
        filename (str): PDF filename

    Returns:
        list[str]: List of images
    """
    pages = fitz.open(filename, filetype="pdf")
    images = []
    for page in pages:
        image = page.get_pixmap(dpi=DPI)
        bytes_image = image.tobytes(output=DEFAULT_IMAGE_FORMAT)
        base64_image = base64.b64encode(bytes_image).decode("utf-8")
        images.append(base64_image)
    return images


def read_image(filename: str) -> str:
    """Read image

    Args:
        filename (str): Image filename
    Returns:
        str: Base64 encoded image
    """
    with open(filename, "rb") as f:
        image = f.read()
    return base64.b64encode(image).decode("utf-8")

def prepare_request(download_link: str, mime_type) -> list[str,str]:
    """Extract data from PDF

    Args:
        download_link (str): URL of media
        mime_type (str): MIME type of media

    Returns:
        list[bytes]: List of images
    """
    suffix = mime_type.split("/")[1]
    filename = tempfile.NamedTemporaryFile(delete=False, suffix=f".{suffix}").name
    download_file(download_link, filename)

    if suffix == "pdf":
        images = convert_pdf2png(filename)
        mime_type = DEFAULT_MIME_TYPE
    elif suffix in ["png", "jpeg", "jpg", "webp"]:
        images = [read_image(filename)]

    os.unlink(filename)
    return images, mime_type


def extract_data(image: str, mime_type:str) -> str:
    """Create a batch request to extract data from image

    Args:
        image (str): Image

    Returns:
        str: Request ID
    """
   
    url = f"{os.environ.get("DOCAI_API_URL")}/extract-data-batch"
    data = {
        "schema_name": os.environ.get("DOCAI_SCHEMA_NAME"),
        "schema_version": os.environ.get("DOCAI_SCHEMA_VERSION"),
        "content": image,
        "mime_type": mime_type
    }
    headers = {
        'Content-Type': 'application/json',
        'x-api-key': os.environ.get("DOCAI_API_KEY")
    }
    r = httpx.post(url, headers=headers, json=data, timeout=120)
    return r.json()


def fetch_result(request_id:str)->dict:
    """Fetch result of extraction

    Args:
        request_id (str): Request ID

    Returns:
        dict: Result of extraction
    """
    url = f"{os.environ.get("DOCAI_API_URL")}/get-result"
    data = {"request_id": request_id}
    headers = {
        'Content-Type': 'application/json',
        'x-api-key': os.environ.get("DOCAI_API_KEY")
    }
    r = httpx.post(url, headers=headers, json=data, timeout=120)
    return r.json()

def keep_alive(processes: list[multiprocessing.Process]|None=None) -> None:
    try:
        while True:
            time.sleep(5)
    except KeyboardInterrupt:
        if processes:
            for p in processes:
                p.terminate()
        print("Interrupted by user, shutting down.")
        sys.exit(0)


def process_error(exc)->dict[str,str]:
    {
        "error": str(exc),
        "message": str(exc),
    }