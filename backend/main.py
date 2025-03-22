import jwt
import bcrypt
import os

from fastapi import FastAPI, HTTPException
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from pydantic import BaseModel
from dotenv import load_dotenv
from jwt.exceptions import InvalidTokenError
from datetime import datetime, timedelta, timezone

load_dotenv()
app = FastAPI()
class User(BaseModel):
    number: int
    name: str
    surname: str
    password: str

class LoginUser(BaseModel):
    number: int
    password: str

class LoginToken(BaseModel):
    access_token: str
    token_type: str

JWT_SECRET = os.getenv("JWT_SECRET") or "7938013fe5cec581a02dc8d547077804dfa02a1a07a9daac64890607da927013"
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM") or "HS256"

def create_token(data: dict, expire_in: int = 30):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes = expire_in)
    to_encode.update({"exp": expire})
    token = jwt.encode(to_encode, JWT_SECRET, algorithm = JWT_ALGORITHM)
    return token

@app.on_event("startup")
async def startup_db_client():
    uri = os.getenv("MONGO_URI")
    app.mongodb_client = MongoClient(uri, server_api=ServerApi('1'))
    app.mongodb = app.mongodb_client["crud"]

    try:
        app.mongodb_client.admin.command('ping')
        print("Connected with database")
    except Exception as e:
        print(e)

@app.on_event("shutdown")
def shutdown_db_client():
    app.mongodb_client.close()

@app.post("/register")
async def register_user(user: User):
    existing_user = app.mongodb["users"].find_one({"number": user.number})
    if existing_user:
        raise HTTPException(status_code = 400, detail = "Number taken")
    
    hashed_password = bcrypt.hashpw(user.password.encode("utf-8"), bcrypt.gensalt()) # Paskudnie to wygląda w database
                                                                                     #TODO wrzucić to do stringa potem
    user_obj = {
        "number": user.number,
        "name": user.name,
        "surname": user.surname,
        "password": hashed_password
    }

    app.mongodb["users"].insert_one(user_obj) #? Tutaj sprawdzić, czy istnieje jakaś obsługa błędów

    return {"message": "User registered"}

@app.post("/login")
def login_user(user: LoginUser):
    user_record = app.mongodb["users"].find_one({"number": user.number})
    if not user_record:
        raise HTTPException(status_code = 400, detail = "Wrong number or password")
    
    if not bcrypt.checkpw(user.password.encode("utf-8"), user_record["password"]):
        raise HTTPException(status_code = 400, detail = "Wrong number or password")
    
    #TODO ☝️ to mogę zapisać w jednym ifie kiedyśtam
    
    token = create_token(data = {"sub": int(user.number)})
    return {"access_token": token, "token_type": "bearer"}