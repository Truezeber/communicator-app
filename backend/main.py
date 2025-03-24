import jwt
import bcrypt
import os
import time
import random
import json

from fastapi import FastAPI, HTTPException, Header, WebSocket, WebSocketDisconnect, status
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from pydantic import BaseModel
from dotenv import load_dotenv
from datetime import datetime, timedelta, timezone

load_dotenv()
app = FastAPI()
active_connections = {}

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

class AddContact(BaseModel):
    number: int

JWT_SECRET = os.getenv("JWT_SECRET") or "7938013fe5cec581a02dc8d547077804dfa02a1a07a9daac64890607da927013"
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM") or "HS256"

def create_token(data: dict, expire_in: int = 30):
    to_encode = data.copy()
    if "sub" in to_encode:
        to_encode["sub"] = str(to_encode["sub"])
    expire = datetime.now(timezone.utc) + timedelta(minutes = expire_in)
    to_encode.update({"exp": int(expire.timestamp())})
    token = jwt.encode(to_encode, JWT_SECRET, algorithm = JWT_ALGORITHM)
    return token

def verify_token(token: str):
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM], options={"verify_exp": True})
        user_number = payload.get("sub")
        if user_number is None:
            raise HTTPException(status_code = 403, detail = "Invalid token: no subject")
        return int(user_number)
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code = 403, detail = "Token has expired")
    except jwt.InvalidTokenError as e:
        raise HTTPException(status_code = 403, detail = f"Invalid token: {str(e)}")
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code = 500, detail = f"Unexpected error: {str(e)}")
    
def verify_user(authorization: str):
    if not authorization:
        raise HTTPException(status_code = 401, detail = "Authorization header missing")
    
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code = 401, detail = "Invalid authorization header")
    
    token = authorization[len("Bearer "):]
    user_number = verify_token(token)

    return user_number
    
async def websocket_auth(websocket: WebSocket):
    query_params = websocket.query_params
    authorization = query_params.get("authorization")

    if not authorization:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return None
    
    if not authorization.startswith("Bearer "):
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return None
    
    token = authorization[len("Bearer "):]
    try:
        user_number = verify_token(token)
        return user_number
    except HTTPException:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return None


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


@app.get("/ping")
def ping():
    return {"message": "pong"}

@app.post("/register")
async def register_user(user: User):
    existing_user = app.mongodb["users"].find_one({"number": user.number})
    if existing_user:
        raise HTTPException(status_code = 400, detail = "Number taken")
    
    hashed_password = bcrypt.hashpw(user.password.encode("utf-8"), bcrypt.gensalt()) #TODO Paskudnie to wygląda w database
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
async def login_user(user: LoginUser):
    user_record = app.mongodb["users"].find_one({"number": user.number})
    if not user_record:
        raise HTTPException(status_code = 400, detail = "Wrong number or password")
    
    if not bcrypt.checkpw(user.password.encode("utf-8"), user_record["password"]):
        raise HTTPException(status_code = 400, detail = "Wrong number or password")
    
    #TODO ☝️ to mogę zapisać w jednym ifie kiedyśtam
    
    token = create_token(data = {"sub": int(user.number)})
    return {"access_token": token, "token_type": "bearer"}

@app.get("/test")
async def test_token(test: str, authorization: str = Header(None)):
    user_number = verify_user(authorization)

    user = app.mongodb["users"].find_one({"number": user_number})
    if not user:
        raise HTTPException(status_code = 404, detail = "User not found")
    
    return {"name": user["name"],"surname": user["surname"], "param": test}

@app.post("/contacts/add")
async def add_contact(number: int, authorization: str = Header(None)):
    user_number = verify_user(authorization)

    #TODO ☝️ Całe to to w ogóle mogę potem do funkcji jakiejś wrzucić, bo przy tylu endpointach to będzie wyglądać tragicznie

    conversations = app.mongodb["conversations"].find_one({"owner": user_number})

    if not conversations:
        new_conversations = {
            "owner": user_number,
            "contacts": []
        }
        app.mongodb["conversations"].insert_one(new_conversations)

    existing_contact = app.mongodb["conversations"].find_one(
        {"owner": user_number, "contacts.number": number}
    )

    if existing_contact:
        raise HTTPException(status_code = 400, detail = "Contact is existing")
    
    id = f"{int(time.time())}{random.randint(1000, 9999)}"

    result = app.mongodb["conversations"].update_one(
        {"owner": user_number},
        {"$push": {"contacts": {"number": number, "id": id}}}
    )

    if result.modified_count == 0:
        raise HTTPException(status_code = 500, detail = "Unexpected error")
    
    #!Tutaj trzeba jeszcze dodać sprawdzanie, czy dodawany kontakt ma już rozpoczętą konwersację i jak ma, to skopiować id z niej, bo inaczej to nie siądzie xD
    
    return {"message": "Contact added"}

@app.get("/contacts")
async def get_contacts(authorization: str = Header(None)):
    user_number = verify_user(authorization)

    conversations = app.mongodb["conversations"].find_one({"owner": user_number})
    if not conversations:
        new_conversations = {
            "owner": user_number,
            "contacts": []
        }
        app.mongodb["conversations"].insert_one(new_conversations)
    #TODO ☝️ to w sumie też można przerzucić do funkcji potem

    return {"contacts": conversations["contacts"]}

@app.websocket("/ts")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    while True:
        data = await websocket.receive_text()
        await websocket.send_text(f"Test: {data}")

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    
    user_number = await websocket_auth(websocket)
    if not user_number:
        return
    
    await websocket.accept()

    print(f"🛜{user_number} połączony, websocket: {websocket}\n")

    active_connections[user_number] = websocket

    try:
        while True:
            data = await websocket.receive_text()
            print(f"✉️{user_number}: {data}\n")

            message = json.loads(data)
            destination_id = message["to"]
            destination_number = app.mongodb["conversations"].find_one({"owner": user_number, "contacts": {"$elemMatch": {"id": destination_id}}}, {"contacts.$": 1})
            content = message["content"]

            print(f"📨destination_id: {destination_id}, destination_number: {destination_number}, content: {content}")

            app.mongodb["messages"].insert_one({"conversation_id": destination_id, "sender": user_number, "content": content, "timestamp": datetime.now(timezone.utc).isoformat()})

            if destination_number in active_connections:
                await active_connections[destination_number].send_text(f"conversation: {destination_id}, content: {content}")
            else:
                print(f"🦹{user_number} offline, zapisano do bazy")
    
    except WebSocketDisconnect:
        print(f"📵 {user_number} rozłączył się")
        del active_connections[user_number]