from fastapi import FastAPI
from app.routes import user, task

app = FastAPI(title="Task Manager API with FastAPI")

app.include_router(user.router)
app.include_router(task.router)
