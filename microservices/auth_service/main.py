from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import os
from passlib.context import CryptContext
import uvicorn

app = FastAPI(title="Owner Auth Service")

PASS_FILE = "microservices/auth_service/data/owner_pass.txt"
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class PasswordChange(BaseModel):
    old_password: str
    new_password: str

class PasswordLogin(BaseModel):
    password: str

def get_stored_hash():
    if not os.path.exists(PASS_FILE):
        default_hash = pwd_context.hash("1")
        with open(PASS_FILE, "w") as f:
            f.write(default_hash)
        return default_hash
    with open(PASS_FILE, "r") as f:
        return f.read().strip()

def save_new_hash(new_hash):
    with open(PASS_FILE, "w") as f:
        f.write(new_hash)

@app.post("/owner/login")
def login(data: PasswordLogin):
    stored_hash = get_stored_hash()
    if pwd_context.verify(data.password, stored_hash):
        return {"message": "Login success"}
    raise HTTPException(status_code=401, detail="Invalid password")

@app.put("/owner/password")
def change_password(data: PasswordChange):
    stored_hash = get_stored_hash()
    if not pwd_context.verify(data.old_password, stored_hash):
        raise HTTPException(status_code=401, detail="Old password is incorrect")
    new_hash = pwd_context.hash(data.new_password)
    save_new_hash(new_hash)
    return {"message": "Password updated successfully"}
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8010)
