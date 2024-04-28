import uuid
from pydantic import BaseModel, Field, field_validator, conlist


class User(BaseModel):
    sub: int = Field(..., description="A stable identifier for the user")
    email: str = Field(..., description="The email address of the user")
    name: str = Field(..., description="The name of the user")
    email_verified: bool = Field(
        ..., description="Whether the email address has been verified"
    )


class Page(BaseModel):
    id: str = Field(..., description="A stable identifier for the page")
    num: int = Field(..., description="Page number")
    content: str = Field(..., description="Base64 encoded image")
    mime_type: str = Field(..., description="Mime type of the image")


class Result(BaseModel):
    id: str = Field(..., description="The unique identifier of the listing")


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


class OpenAIFileIdRefs(BaseModel):
    openaiFileIdRefs: conlist(FileInfo, min_length=1, max_length=2) = Field(  # type: ignore
        ..., description="List of file information. Maximum of 2 files."
    )


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
