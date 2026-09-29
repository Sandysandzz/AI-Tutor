from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging
import os
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))

from backend.models import create_tables, get_engine

# Routers
from backend.routers.auth import router as auth_router
from backend.teachers import router as teachers_router

app = FastAPI(title="AI Tutor Backend")

logger = logging.getLogger("uvicorn.error")

ENGINE = None

@app.on_event("startup")
def startup_event():
    global ENGINE
    ENGINE = get_engine()
    create_tables(ENGINE)
    logger.info("DB initialized")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://127.0.0.1:5173",
        "http://localhost:5173",
        "http://127.0.0.1:3000",
        "http://localhost:3000",
        "http://127.0.0.1:5174",
        "http://localhost:5174"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
def health_check():
    return {"status": "ok"}

# Add existing routers
app.include_router(auth_router)
app.include_router(teachers_router)

# Add new routers
from backend.routers import content, chat, homework, exam, adaptive_learning, summarize
app.include_router(content.router)
app.include_router(chat.router)
app.include_router(exam.router)
app.include_router(adaptive_learning.router)
app.include_router(summarize.router)

from backend.routers import teacher
app.include_router(teacher.router)
# app.include_router(homework.router)  # Disabled as per feature refinement

# ---- Begin auth_v2 safe include ----
# This will only include the new auth_v2 router when the environment
# variable ENABLE_NEW_AUTH is set to "true". It's wrapped in a try/except
# so any import errors won't crash your main app.
try:
    if os.getenv("ENABLE_NEW_AUTH", "false").lower() == "true":
        from backend.routers import auth_v2
        app.include_router(auth_v2.router)
        print("Auth_v2 router enabled at /auth_v2")
    else:
        print("Auth_v2 router disabled. Set ENABLE_NEW_AUTH=true to enable it.")  # Config check (API Key updated)
except Exception as e:
    # safe guard: log but don't crash main app
    print("Failed to include auth_v2:", e)
# ---- End auth_v2 safe include ----
