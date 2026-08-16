from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes.chat import router

app = FastAPI(title = " NAYATEL AI ASSISTANT", description = "Internship Chat Bot POC project", version = "1.0")
app.add_middleware(CORSMiddleware, allow_origins = ['*'], allow_credentials = False, allow_methods = ['*'], allow_headers = ['*'])

app.include_router(router)

@app.get("/")
def root() -> dict:
    return {"message": "Running Successfully (Finally)"}
