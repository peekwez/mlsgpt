import uuid
from typing import List
from pydantic import BaseModel, Field, field_validator


class Page(BaseModel):
    id: str = Field(..., description="A stable identifier for the page")
    num: int = Field(..., description="Page number")
    content: str = Field(..., description="Base64 encoded image")
    mime_type: str = Field(..., description="Mime type of the image")


class FileInfo(BaseModel):
    name: str = Field(..., description="The name of the file")
    id: str = Field(..., description="A stable identifier for the file.")
    mime_type: str = Field(
        ...,
        description="The mime type of the file. For user uploaded files this is based on file extension.",
    )
    download_link: str = Field(
        ..., description="The URL to fetch the file which is valid for five minutes."
    )


class FileInfos(BaseModel):
    files: List[FileInfo] = Field(..., description="List of file information")


class Message(BaseModel):
    OK: bool = Field(..., description="Status of the batch extraction request")
    message: str = Field(
        ..., description="Message describing the status of the request"
    )


class Listing(BaseModel):
    id: uuid.UUID = Field(..., description="The unique identifier of the listing")
    cossim: float | None = Field(
        None,
        description="Cosine similarity score for the search query",
    )
    data: dict = Field(..., description="The data associated with the listing")

    @field_validator("cossim")
    def round_float(cls, v):
        if v is not None:
            return round(float(v), 4)
        return v
