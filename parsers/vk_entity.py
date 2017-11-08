from typing import List

from pydantic.main import BaseModel


class Photo(BaseModel):
    id: int = None
    owner_id: int = None
    post_id: int = None
    photo_1280: str = None
    photo_807: str = None
    photo_604: str = None


class Attachment(BaseModel):
    type: str = None
    photo: Photo = None


class Item(BaseModel):
    id: int = None
    from_id: int = None
    owner_id: int = None
    post_type: str = None
    marked_as_ads: int = None
    attachments: List[Attachment] = None


class Response(BaseModel):
    count: int = None
    items: List[Item] = None


class GetPhotosById(BaseModel):
    response: List[Photo] = None
