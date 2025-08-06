import uvicorn
from fastapi import FastAPI
from fastapi.routing import APIRouter

from src.user_profile.router import user_profile_router

app = FastAPI(title="Kindle")
main_router = APIRouter()

main_router.include_router(user_profile_router, prefix="/users", tags=["Users"])
app.include_router(main_router)

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000)
