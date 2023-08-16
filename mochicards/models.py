from datetime import datetime
from typing import Optional, List, Dict
from pydantic import BaseModel


class Card(BaseModel):
    id: str
    content: str
    deck_id: str
    template_id: Optional[str] = None
    fields: Dict = {}
    attachments: List = []
    archived: bool = False
    pos: Optional[str] = None
    created_at: Dict[str, datetime]
    updated_at: Dict[str, datetime]
    tags: List[str] = []
    name: Optional[str]
    references: List[str] = []
    reviews: List[str] = []

    class Config:
        fields = {
            "created_at": "created-at",
            "updated_at": "updated-at",
            "template_id": "template-id",
            "archived": "archived?",
            "new": "new?",
            "deck_id": "deck-id",
        }


class PaginatedCards(BaseModel):
    bookmark: Optional[str]
    docs: List[Card]


class CardData(BaseModel):
    content: str
    deck_id: str
    template_id: Optional[str] = None
    fields: Optional[Dict] = None
    attachments: Optional[List] = None
    archived: bool = False
    pos: Optional[str] = None
    review_reverse: bool = False


class Deck(BaseModel):
    id: str
    name: str
    parent_id: Optional[str] = None
    sort: int
    archived: bool = False
    trashed: Optional[datetime] = None


class Template(BaseModel):
    id: str
    name: str
    content: str
    fields: Dict
