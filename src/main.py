import sentry_sdk
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.routing import APIRouter
from prometheus_fastapi_instrumentator import Instrumentator

from src.auth.router import admin_router, auth_router
from src.user_profile.router import users_router

sentry_sdk.init(
    dsn="https://974969dc670cb13f88c4412506bd0495@o4509882482950144.ingest.us.sentry.io/4509882495270912",
    send_default_pii=True,
)


main_api_router = APIRouter()
main_api_router.include_router(admin_router)
main_api_router.include_router(auth_router)
main_api_router.include_router(users_router)

app = FastAPI(title="Kindle")
Instrumentator().instrument(app).expose(app)

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
