from fastapi import FastAPI, HTTPException
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from pydantic import BaseModel
import bcrypt

class User(BaseModel):
    number: int
    name: str
    surname: str
    password: str

app = FastAPI()

users = {}

@app.on_event("startup")
async def startup_db_client():
    uri = "mongodb+srv://crud-user:BjIQqtjEhUqvCPxw@crud.d14a5.mongodb.net/?retryWrites=true&w=majority&appName=CRUD"
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
    
    hashed_password = bcrypt.hashpw(user.password.encode("utf-8"), bcrypt.gensalt())

    user_obj = {
        "number": user.number,
        "name": user.name,
        "surname": user.surname,
        "password": hashed_password
    }

    app.mongodb["users"].insert_one(user_obj) #? Tutaj sprawdzić, czy istnieje jakaś obsługa błędów

    return {"message": "User registered"}

@app.get("/users")
async def get_users():
    return {"users": [{"number": key, **value} for key, value in users.items()]}

@app.get("/users/{number}")
async def get_user(number: int):
    if number not in users:
        raise HTTPException(status_code = 404, detail = "User not found")
    user = {"number": number, **users[number]}
    return {"user": user}