from fastapi import FastAPI, Depends, HTTPException, Header
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from pydantic import BaseModel
from typing import List
from datetime import datetime, timedelta
import os

app =FastAPI()

# Secret key to encode and decode JWT
# API_Key = "my-secret-api-key"
# API_Key = os.environ.get("API_KEY")
SECRET_KEY = "my-secret-key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


# === Token Dependency ===
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

#Create a fake database
fake_users_db = {
    "admin": {
        "username": "admin",
        "full_name": "Admin User",
        "password": "password"
    }      
} 

# Define a Pydantic model for the request body Book and Token
class Token(BaseModel):
    access_token: str
    token_type: str
    
class Book(BaseModel):
    title: str
    author: str
    published_year: int

class Book_ID(Book):
    id: int
    
books: List[Book_ID] = []

# === Auth Logic ===
def authenticate_user(username: str, password: str):
    user = fake_users_db.get(username)
    if not user or user["password"] != password:
        return False
    return user

def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=15))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        user = fake_users_db.get(username)
        if user is None:
            raise HTTPException(status_code=401, detail="User not found")
        return user
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")


# === Token Route ===
@app.post("/token", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=401, detail="Incorrect username or password")
    access_token = create_access_token(data={"sub": user["username"]})
    return {"access_token": access_token, "token_type": "bearer"}

#Root endpoint
@app.get("/")
def read_root(current_user: dict = Depends(get_current_user)):
    return {"message": f"Welcome {current_user['username']} to the Book API!"}

#Return all the books
@app.get("/books", response_model=List[Book_ID])
def get_books(current_user: dict = Depends(get_current_user)):
    if len(books) == 0:
        raise HTTPException(status_code=404, detail="No books found")
    else:
        return books

#Return the book with the given ID
@app.get("/books/{book_id}", response_model=Book_ID)
def get_book(book_id: int, current_user: dict = Depends(get_current_user)):
    for book in books:
        if book.id == book_id:
            return book
    raise HTTPException(status_code=404, detail="Book not found")


#Add a new book
@app.post("/books", response_model=Book_ID)
def add_book(book: Book, current_user: dict = Depends(get_current_user)):
    book_id = len(books) + 1
    new_book = Book_ID(id=book_id, **book.dict())
    books.append(new_book)
    return new_book

#Update a book with the given ID
@app.put("/books/{book_id}", response_model=Book_ID)
def update_book(book_id: int, book: Book, current_user: dict = Depends(get_current_user)):
    for index, existing_book in enumerate(books):
        if existing_book.id == book_id:
            updated_book = Book_ID(id=book_id, **book.dict()) 
            books[index] = updated_book
            return updated_book
    raise HTTPException(status_code=404, detail="Book not found")


#Delete a book with the given ID
@app.delete("/books/{book_id}", response_model=Book_ID)
def delete_book(book_id: int, current_user: dict = Depends(get_current_user)):
    for index, existing_book in enumerate(books):
        if existing_book.id == book_id:
            deleted_book = books.pop(index)
            return deleted_book
    raise HTTPException(status_code=404, detail="Book not found")