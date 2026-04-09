from fastapi import FastAPI
from database import init_db, get_connection

app = FastAPI(title = "Chai Tapri API", 
              description="This is the backend for famous tea shop", 
              version='1.0.0')

# --- Create tables on startup ----
init_db()

## We wil be using Pydantic (Used Data Validation)


@app.get("/")
def home():
    return {
        "name": "Raju Bhai's Chai Tapri",
        "location": "Madhapur, Hyderabad",
        "since": 2012,
        "docs": "Visit /docs for the full API"
    }
















