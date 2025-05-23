from fastapi import FastAPI, Depends, HTTPException, Header
from pydantic import BaseModel
from typing import List
import os

app =FastAPI()

# Define API Key
# API_Key = "my-secret-api-key"
API_Key = os.environ.get("API_KEY")

# Security dependency check
def verify_api_key(api_key: str = Header(..., alias="API-Key")):
    if api_key != API_Key:
        raise HTTPException(status_code=401, detail="Invalid API Key")

# Define a Pydantic model for the request body Book
class Book(BaseModel):
    title: str
    author: str
    published_year: int

class Book_ID(Book):
    id: int
    
books: List[Book_ID] = []

#Root endpoint
@app.get("/")
def read_root(api_key:str = Depends(verify_api_key)):
    return {"message": "Welcome to the Book API!"}

#Return all the books
@app.get("/books", response_model=List[Book_ID])
def get_books(api_key:str = Depends(verify_api_key)):
    if len(books) == 0:
        raise HTTPException(status_code=404, detail="No books found")
    else:
        return books

#Return the book with the given ID
@app.get("/books/{book_id}", response_model=Book_ID)
def get_book(book_id: int, api_key:str = Depends(verify_api_key)):
    for book in books:
        if book.id == book_id:
            return book
    raise HTTPException(status_code=404, detail="Book not found")


#Add a new book
@app.post("/books", response_model=Book_ID)
def add_book(book: Book, api_key:str = Depends(verify_api_key)):
    book_id = len(books) + 1
    new_book = Book_ID(id=book_id, **book.dict())
    books.append(new_book)
    return new_book

#Update a book with the given ID
@app.put("/books/{book_id}", response_model=Book_ID)
def update_book(book_id: int, book: Book, api_key:str = Depends(verify_api_key)):
    for index, existing_book in enumerate(books):
        if existing_book.id == book_id:
            updated_book = Book_ID(id=book_id, **book.dict()) 
            books[index] = updated_book
            return updated_book
    raise HTTPException(status_code=404, detail="Book not found")


#Delete a book with the given ID
@app.delete("/books/{book_id}", response_model=Book_ID)
def delete_book(book_id: int, api_key:str = Depends(verify_api_key)):
    for index, existing_book in enumerate(books):
        if existing_book.id == book_id:
            deleted_book = books.pop(index)
            return deleted_book
    raise HTTPException(status_code=404, detail="Book not found")