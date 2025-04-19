from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from passlib.context import CryptContext
import pandas as pd
import os
import uvicorn
app = FastAPI(title="Customer Auth Service")

DATA_FILE = "microservices/auth_service_cus/data/cusAccList.xlsx"
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class RegisterRequest(BaseModel):
    username: str
    password: str

class LoginRequest(BaseModel):
    username: str
    password: str

class ChangePassRequest(BaseModel):
    username: str
    old_password: str
    new_password: str
def init_file():
    if not os.path.exists(DATA_FILE):
        df = pd.DataFrame(columns=["username", "password_hash"])
        df.to_excel(DATA_FILE, index=False)

def read_accounts():
    init_file()
    return pd.read_excel(DATA_FILE)

def write_accounts(df):
    df.to_excel(DATA_FILE, index=False)


@app.post("/register")
def register(data: RegisterRequest):
    df = read_accounts()

    if data.username.strip() == "" or data.password.strip() == "":
        raise HTTPException(status_code=400, detail="Username and password cannot be empty")

    if df["username"].str.lower().eq(data.username.lower()).any():
        raise HTTPException(status_code=400, detail="Username already exists")

    password_hash = pwd_context.hash(data.password)
    df.loc[len(df)] = [data.username, password_hash]
    write_accounts(df)

    return {"message": "Account created successfully"}

@app.post("/login")
def login(data: LoginRequest):
    df = read_accounts()
    row = df[df["username"].str.lower() == data.username.lower()]

    if row.empty:
        raise HTTPException(status_code=401, detail="Invalid username or password")

    stored_hash = row.iloc[0]["password_hash"]
    if not pwd_context.verify(data.password, stored_hash):
        raise HTTPException(status_code=401, detail="Invalid username or password")

    return {"message": "Login successful", "username": row.iloc[0]["username"]}
@app.put("/change_pass")
def change_password(data: ChangePassRequest):
    df = read_accounts()
    row = df[df["username"].str.strip().str.lower() == data.username.strip().lower()]

    if row.empty:
        raise HTTPException(status_code=401, detail="Tên người dùng không tồn tại")

    stored_hash = row.iloc[0]["password_hash"]
    if not pwd_context.verify(data.old_password, stored_hash):
        raise HTTPException(status_code=401, detail="Sai mật khẩu")

    new_hash = pwd_context.hash(data.new_password)
    df.loc[row.index[0], "password_hash"] = new_hash
    write_accounts(df)

    return {"message": "Đổi mật khẩu thành công"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8011)