from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.exc import IntegrityError
from app.config import settings
from app.routers import auth, equipment, hospitals, work_orders

FRONTEND_ORIGIN = settings.frontend_origin

app = FastAPI(
    title="MedFlow Clinical Equipment Command Center",
    description="Halcyon Health Systems' medical equipment management API.",
    version="0.1.0",
)

# CORS config goes here
app.add_middleware(
    CORSMiddleware,
    allow_origins=[FRONTEND_ORIGIN, "d2np866xgiuucr.cloudfront.net"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

# include routers here
app.include_router(equipment.router)
app.include_router(hospitals.router)
app.include_router(work_orders.router)
app.include_router(auth.router)

# simple health check endpoint
@app.get("/health", tags=["health"])
async def health_check() -> dict[str,str]:
    return{"status": "ok"}
