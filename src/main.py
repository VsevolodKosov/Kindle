import uvicorn
from fastapi import FastAPI
from fastapi.routing import APIRouter

from src.user_profile.router import users_router

main_api_router = APIRouter()
main_api_router.include_router(users_router, tags=["users"])

app = FastAPI(title="Kindle")
app.include_router(main_api_router)

if __name__ == "__main__":
    uvicorn.run(app, host="localhost", port=8000)
