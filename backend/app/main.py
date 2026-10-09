from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
# from sqlalchemy.ext.asyncio import AsyncSession
from app.config import settings
from app.routers import auth, equipment, hospitals, work_orders, health
from app.dependencies import get_db, require_role


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
app.include_router(health.router)

## Exception handling:

# handles when db constraint for fuel-level is violated
@app.exception_handler(IntegrityError)
async def integrity_error_handler(request: Request, exc: IntegrityError) -> JSONResponse:
    return JSONResponse(
        status_code=409,
        content={"detail": "A database constraint was violated (e.g. a duplicate value)"},
    )

# catch-all exception handler for any unexpected failure
@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    return JSONResponse(
        status_code=500,
        content={"detail": "An unexpected error has occurred."},
    )