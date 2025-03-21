from fastapi import FastAPI, HTTPException
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi

app = FastAPI()

users = {}

@app.on_event("startup")
async def startup_db_client():
    uri = "mongodb+srv://crud-user:BjIQqtjEhUqvCPxw@crud.d14a5.mongodb.net/?retryWrites=true&w=majority&appName=CRUD"
    app.mongodb_client = MongoClient(uri, server_api=ServerApi('1'))
    app.mongodb = app.mongodb_client["CRUD"]

    try:
        app.mongodb_client.admin.command('ping')
        print("Connected with database")
    except Exception as e:
        print(e)

@app.on_event("shutdown")
def shutdown_db_client():
    app.mongodb_client.close()

@app.post("/register")
async def register_user(number: int, password: str, name: str, surname: str ):
    user = {
        "password": password,
        "name": name,
        "surname": surname,
    }

    if number in users:
        return {"message": "taken"}
    users[number] = user
    return {"message": "registered"}

@app.get("/users")
async def get_users():
    return {"users": [{"number": key, **value} for key, value in users.items()]}

@app.get("/users/{number}")
async def get_user(number: int):
    if number not in users:
        raise HTTPException(status_code = 404, detail = "User not found")
    user = {"number": number, **users[number]}
    return {"user": user}