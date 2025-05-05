from fastapi import APIRouter, HTTPException
from app.schemas import UserCreate, UserLogin, Token
from app.auth import get_password_hash, verify_password, create_access_token
from app.database import user_collection
from bson.objectid import ObjectId

router = APIRouter(prefix="/user", tags=["User"])

@router.post("/signup", response_model=Token)
def signup(user: UserCreate):
    if user_collection.find_one({"email": user.email}):
        raise HTTPException(status_code=400, detail="Email already exists")
    hashed_password = get_password_hash(user.password)
    new_user = {
        "username": user.username,
        "email": user.email,
        "password": hashed_password
    }
    user_collection.insert_one(new_user)
    access_token = create_access_token(data={"sub": user.email})
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/login", response_model=Token)
def login(user: UserLogin):
    db_user = user_collection.find_one({"email": user.email})
    if not db_user or not verify_password(user.password, db_user["password"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    access_token = create_access_token(data={"sub": user.email})
    return {"access_token": access_token, "token_type": "bearer"}
