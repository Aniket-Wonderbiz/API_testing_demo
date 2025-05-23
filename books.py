from fastapi import APIRouter, Depends, HTTPException
from typing import List
from models import Book, Book_ID
from database import books
from auth import get_current_user

router = APIRouter()

@router.get("/")
def root(current_user: dict = Depends(get_current_user)):
    return {"message": f"Welcome {current_user['username']} to the Book API!"}

@router.get("/books", response_model=List[Book_ID])
def get_books(current_user: dict = Depends(get_current_user)):
    if not books:
        raise HTTPException(status_code=404, detail="No books found")
    return books

@router.post("/books", response_model=Book_ID)
def add_book(book: Book, current_user: dict = Depends(get_current_user)):
    book_id = len(books) + 1
    new_book = Book_ID(id=book_id, **book.dict())
    books.append(new_book)
    return new_book

@router.get("/books/{book_id}", response_model=Book_ID)
def get_book(book_id: int, current_user: dict = Depends(get_current_user)):
    for book in books:
        if book.id == book_id:
            return book
    raise HTTPException(status_code=404, detail="Book not found")

@router.put("/books/{book_id}", response_model=Book_ID)
def update_book(book_id: int, book: Book, current_user: dict = Depends(get_current_user)):
    for index, existing_book in enumerate(books):
        if existing_book.id == book_id:
            updated_book = Book_ID(id=book_id, **book.dict())
            books[index] = updated_book
            return updated_book
    raise HTTPException(status_code=404, detail="Book not found")

@router.delete("/books/{book_id}", response_model=Book_ID)
def delete_book(book_id: int, current_user: dict = Depends(get_current_user)):
    for index, existing_book in enumerate(books):
        if existing_book.id == book_id:
            return books.pop(index)
    raise HTTPException(status_code=404, detail="Book not found")
