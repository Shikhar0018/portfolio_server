from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import design, projects, experiences
from app.core.config import settings

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

# Set up CORS
if settings.BACKEND_CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

# Include API routes
app.include_router(design.router, prefix=f"{settings.API_V1_STR}/design", tags=["design"])
app.include_router(projects.router, prefix=f"{settings.API_V1_STR}/projects", tags=["projects"])
app.include_router(experiences.router, prefix=f"{settings.API_V1_STR}/experiences", tags=["experiences"])

@app.get("/")
def read_root():
    return {"message": "Welcome to the Portfolio API"}


# @app.get("/api/v1/css", response_class=FileResponse)
# async def get_css():
#     """Generate and return CSS variables based on the active design system"""
#     # In a real application, you would generate this dynamically
#     # For now, we'll return a static CSS file
#     return FileResponse("app/static/css/styles.css")