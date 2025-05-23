from pydantic import BaseModel
from typing import List

class Book(BaseModel):
    title: str
    author: str
    published_year: int

class Book_ID(Book):
    id: int

class Token(BaseModel):
    access_token: str
    token_type: str
