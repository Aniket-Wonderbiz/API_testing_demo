from fastapi import FastAPI
import books
import auth

app = FastAPI()

#Include the routes
app.include_router(auth.router)
app.include_router(books.router)
