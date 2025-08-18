import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.routing import APIRouter

from src.auth.router import admin_router, auth_router
from src.user_profile.router import users_router

main_api_router = APIRouter()
main_api_router.include_router(admin_router)
main_api_router.include_router(auth_router)
main_api_router.include_router(users_router)

app = FastAPI(title="Kindle")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:8000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(main_api_router)

if __name__ == "__main__":
    uvicorn.run(app, host="localhost", port=8000)
