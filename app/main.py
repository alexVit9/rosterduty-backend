from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from app.routers import auth, users, restaurant, checklist_templates, completed_checklists, photos, subscription
from app.core.config import settings

app = FastAPI(
    title="RosterDuty API",
    description="Restaurant management SaaS backend",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS — allow web dashboard and React Native mobile app
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"},
    )


@app.get("/health", tags=["health"])
async def health_check():
    return {"status": "ok"}


app.include_router(auth.router)
app.include_router(users.router)
app.include_router(restaurant.router)
app.include_router(checklist_templates.router)
app.include_router(completed_checklists.router)
app.include_router(photos.router)
app.include_router(subscription.router)
