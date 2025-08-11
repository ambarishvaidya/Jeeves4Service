"""Main entry point for the user service FastAPI application"""

from fastapi import FastAPI
from services.inventory_service.routes.household import router as household_router
from services.inventory_service.app.di.containers import Container

# Create FastAPI instance
app = FastAPI(
    title="Household Service API",
    description="API for household management operations",
    version="1.0.0",
    docs_url="/docs",        # Swagger UI will be available at /docs
    redoc_url="/redoc"       # Alternative documentation at /redoc
)

# Initialize dependency injection container
container = Container()

# Include routers
app.include_router(household_router, prefix="/api/v1", tags=["household"])

# Root endpoint
@app.get("/")
async def root():
    return {
        "message": "Welcome to Inventory Service API",
        "version": "1.0.0",
        "documentation": "/docs",
        "health": "/health"
    }

# Health check endpoint
@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "inventory_service"}

# Entry point for running the server
if __name__ == "__main__":
    import uvicorn
    print("Starting Inventory Service API...")
    print("Swagger documentation will be available at: http://localhost:8002/docs")
    uvicorn.run("services.inventory_service.main:app", host="0.0.0.0", port=8002, reload=True)