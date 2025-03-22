from fastapi import FastAPI, HTTPException
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from pydantic import BaseModel
from dotenv import load_dotenv

import bcrypt
import os

class User(BaseModel):
    number: int
    name: str
    surname: str
    password: str

class LoginUser(BaseModel):
    number: int
    password: str

JWT_SECRET = os.getenv("JWT_SECRET")

app = FastAPI()

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
        raise HTTPException(status_code = 400, detail = "Wrong number") #! tylko do debugu, dopisać potem or password
    
    if not bcrypt.checkpw(user.password.encode("utf-8"), user_record["password"]):
        raise HTTPException(status_code = 400, detail = "Wrong password") #! tylko do debugu, dopisać to, co wyżej
    
    return{"message": "valid"}