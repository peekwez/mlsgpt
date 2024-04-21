import os
import fitz
import httpx
import base64
import tempfile
import requests


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


def read_image(image: bytes) -> str:
    """Read image

    Args:
        image (bytes): Image

    Returns:
        str: Base64 encoded image
    """
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
    elif suffix == ["png", "jpeg", "jpg", "webp"]:
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


