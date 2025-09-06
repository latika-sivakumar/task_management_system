from fastapi import FastAPI
from database import db
from routes.auth import router as auth_router
from routes import user
from routes import task
from routes.category import router as category_router  # NEW
from routes.tag import router as tag_router            # NEW

app = FastAPI()

# Register routes
app.include_router(auth_router)
app.include_router(user.router)
app.include_router(task.router)
app.include_router(category_router)  # include categories endpoints
app.include_router(tag_router)       # include tags endpoints

@app.get("/")
async def root():
    collections = await db.list_collection_names()
    return {"message": "Hello, World!", "collections": collections}