import jwt
import bcrypt
import os
import time
import random
import json

from fastapi import FastAPI, HTTPException, Header, WebSocket, WebSocketDisconnect, status
from fastapi.middleware.cors import CORSMiddleware
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from pydantic import BaseModel, HttpUrl
from dotenv import load_dotenv
from datetime import datetime, timedelta, timezone

load_dotenv()
app = FastAPI()
active_connections = {}

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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

class UpdateAvatar(BaseModel):
    avatar_url: HttpUrl

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
    
    hashed_password = bcrypt.hashpw(user.password.encode("utf-8"), bcrypt.gensalt()) 
    
    user_obj = {
        "number": user.number,
        "name": user.name,
        "surname": user.surname,
        "password": hashed_password,
        "avatar_url": f"https://i.pravatar.cc/300?u={user.number}"
    }

    app.mongodb["users"].insert_one(user_obj)

    return {"message": "User registered"}

@app.post("/login")
async def login_user(user: LoginUser):
    user_record = app.mongodb["users"].find_one({"number": user.number})
    if not user_record:
        raise HTTPException(status_code = 400, detail = "Wrong number or password")
    
    if not bcrypt.checkpw(user.password.encode("utf-8"), user_record["password"]):
        raise HTTPException(status_code = 400, detail = "Wrong number or password")
    
    token = create_token(data = {"sub": int(user.number)})
    return {"access_token": token, "token_type": "bearer"}

@app.post("/contacts/add")
async def add_contact(number: int, authorization: str = Header(None)):
    user_number = verify_user(authorization)

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
    
    existing_conversation = app.mongodb["conversations"].find_one(
        {"owner": number, "contacts.number": user_number}, {"contacts.$": 1}
    )

    if existing_conversation:
        contact = existing_conversation["contacts"][0]
        id = contact["id"]

        print(f"id: {id}")
    else:
        id = f"{int(time.time())}{random.randint(1000, 9999)}"

    result = app.mongodb["conversations"].update_one(
        {"owner": user_number},
        {"$push": {"contacts": {"number": number, "id": id}}}
    )

    if result.modified_count == 0:
        raise HTTPException(status_code = 500, detail = "Unexpected error")
    
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

    return {"contacts": conversations["contacts"]}

@app.get("/messages")
async def get_messages(conversation_id: str, timestamp: str = None, authorization: str = Header(None)):
    user_number = verify_user(authorization)

    conversation = app.mongodb["conversations"].find_one({"owner": user_number, "contacts": {"$elemMatch": {"id": conversation_id}}}, {"contacts.$": 1})

    if not conversation:
        raise HTTPException(status_code = 404, detail = "Conversation not found")
    
    if timestamp:
        try:
            timestamp_dt = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
        except ValueError:
            raise HTTPException(status_code = 400, detail="Invalid timestamp format, use ISO like 2025-03-20T10:05:00.000Z")
        
        messages_cursor = app.mongodb["messages"].find({"conversation_id": conversation_id, "timestamp": {"$lt": timestamp_dt}}).sort("timestamp", -1).limit(10)
    else:
        messages_cursor = app.mongodb["messages"].find({"conversation_id": conversation_id}).sort("timestamp", -1).limit(10)

    messages = list(messages_cursor)

    for message in messages:
        message["_id"] = str(message["_id"])
        message["timestamp"] = message["timestamp"].isoformat()

    return {"messages": messages}

@app.put("/avatar_update")
async def avatar_update(avatar: UpdateAvatar, authorization: str = Header(None)):
    user_number = verify_user(authorization)

    app.mongodb["users"].update_one({"number": user_number}, {"$set": {"avatar_url": str(avatar.avatar_url)}})

    return {"message": "Avatar updated"}

@app.get("/avatar_get")
async def avatar_get(number: int):
    user = app.mongodb["users"].find_one({"number": number}, {"avatar_url": 1})

    if not user:
        raise HTTPException(status_code = 404, detail = "User not found")
    
    return {"avatar_url": user["avatar_url"]}

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    
    user_number = await websocket_auth(websocket)
    if not user_number:
        return
    
    await websocket.accept()

    print(f"🛜{user_number} connected, websocket: {websocket}\n")

    active_connections[user_number] = websocket

    try:
        while True:
            data = await websocket.receive_text()
            print(f"✉️{user_number}: {data}\n")

            message = json.loads(data)
            destination_id = message["to"]
            conversation = app.mongodb["conversations"].find_one({"owner": user_number, "contacts": {"$elemMatch": {"id": destination_id}}},{"contacts.$": 1})
            content = message["content"]

            destination_number = None
            if conversation and "contacts" in conversation and conversation["contacts"]:
                destination_number = conversation["contacts"][0]["number"]

            print(f"📨destination_id: {destination_id}, destination_number: {destination_number}, content: {content}")

            app.mongodb["messages"].insert_one({"conversation_id": destination_id, "sender": user_number, "content": content, "timestamp": datetime.now(timezone.utc)})

            if destination_number in active_connections:
                await active_connections[destination_number].send_text(f"conversation: {destination_id}, content: {content}")
            else:
                print(f"🦹{destination_number} offline, saving to database")
    
    except WebSocketDisconnect:
        print(f"📵 {user_number} rozłączył się")
        del active_connections[user_number]