
"""Main entry point for the user service FastAPI application"""

from fastapi import FastAPI
from services.user_service.routes.users import router as users_router
from services.user_service.app.di.containers import Container
import debugpy

debugpy.listen(("0.0.0.0", 5678))  # Use a unique port per service
print("🔍 Waiting for debugger to attach...")


# Create FastAPI instance
app = FastAPI(
    title="User Service API",
    description="API for user management operations",
    version="1.0.0",
    docs_url="/docs",        # Swagger UI will be available at /docs
    redoc_url="/redoc"       # Alternative documentation at /redoc
)

# Initialize dependency injection container
container = Container()

# Include routers
app.include_router(users_router, prefix="/api/v1", tags=["users"])

# Root endpoint
@app.get("/")
async def root():
    return {
        "message": "Welcome to User Service API",
        "version": "1.0.0",
        "documentation": "/docs",
        "health": "/health"
    }

# Health check endpoint
@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "user_service"}

# Entry point for running the server
if __name__ == "__main__":
    import uvicorn
    print("Starting User Service API...")
    print("Swagger documentation will be available at: http://localhost:8000/docs")
    uvicorn.run("services.user_service.main:app", host="0.0.0.0", port=8000, reload=True)