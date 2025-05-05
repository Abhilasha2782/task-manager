from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from bson.objectid import ObjectId
from app.schemas import TaskCreate, TaskOut
from app.database import task_collection, user_collection
from typing import List
import os

router = APIRouter(prefix="/task", tags=["Task"])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="user/login")
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")

# Dependency to get the current user
def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email = payload.get("sub")
        if email is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        user = user_collection.find_one({"email": email})
        if user is None:
            raise HTTPException(status_code=404, detail="User not found")
        return user
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

@router.post("/", response_model=TaskOut)
def create_task(task: TaskCreate, user: dict = Depends(get_current_user)):
    new_task = {
        "title": task.title,
        "description": task.description,
        "completed": False,
        "owner": user["email"]
    }
    result = task_collection.insert_one(new_task)
    new_task["id"] = str(result.inserted_id)
    return new_task

@router.get("/", response_model=List[TaskOut])
def get_tasks(user: dict = Depends(get_current_user)):
    tasks = task_collection.find({"owner": user["email"]})
    return [{"id": str(task["_id"]), **task} for task in tasks]

@router.put("/{task_id}", response_model=TaskOut)
def update_task(task_id: str, updated_task: TaskCreate, user: dict = Depends(get_current_user)):
    task = task_collection.find_one({"_id": ObjectId(task_id), "owner": user["email"]})
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    task_collection.update_one(
        {"_id": ObjectId(task_id)},
        {"$set": {"title": updated_task.title, "description": updated_task.description}}
    )
    updated = task_collection.find_one({"_id": ObjectId(task_id)})
    return {"id": str(updated["_id"]), **updated}

@router.delete("/{task_id}")
def delete_task(task_id: str, user: dict = Depends(get_current_user)):
    result = task_collection.delete_one({"_id": ObjectId(task_id), "owner": user["email"]})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Task not found")
    return {"message": "Task deleted successfully"}
