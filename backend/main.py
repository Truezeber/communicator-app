from fastapi import FastAPI, HTTPException

app = FastAPI()

users = {}

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