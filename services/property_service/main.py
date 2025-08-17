"""Main entry point for the property service FastAPI application"""

from fastapi import FastAPI
from services.property_service.routes.property import router as property_router
from services.property_service.routes.storage import router as storage_router
from services.property_service.app.di.containers import Container
import debugpy

debugpy.listen(("0.0.0.0", 5679))  # Use a unique port per service
print("🔍 Waiting for debugger to attach...")

# Create FastAPI instance
app = FastAPI(
    title="Property Service API",
    description="API for property and storage management operations",
    version="1.0.0",
    docs_url="/docs",        # Swagger UI will be available at /docs
    redoc_url="/redoc"       # Alternative documentation at /redoc
)

# Initialize dependency injection container
container = Container()

# Include routers
app.include_router(property_router, prefix="/api/v1", tags=["property"])
app.include_router(storage_router, prefix="/api/v1", tags=["storage"])

# Root endpoint
@app.get("/")
async def root():
    return {
        "message": "Welcome to Property Service API",
        "version": "1.0.0",
        "documentation": "/docs",
        "health": "/health"
    }

# Health check endpoint
@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "property_service"}

# Entry point for running the server
if __name__ == "__main__":
    import uvicorn
    print("Starting Property Service API...")
    print("Swagger documentation will be available at: http://localhost:8001/docs")
    uvicorn.run("services.property_service.main:app", host="0.0.0.0", port=8001, reload=True)
