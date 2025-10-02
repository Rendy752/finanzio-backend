# app/main.py

from fastapi import FastAPI

# --- THIS IS THE CRITICAL LINE ---
app = FastAPI(
    title="Finanzio Backend API",
    version="1.0.0",
    # Add other metadata here
)
# ---------------------------------

# Import and include routers here
# from app.api.v1.endpoints import router as api_router
# app.include_router(api_router, prefix="/api/v1")

# Add initialization logic (like database connection) here
# @app.on_event("startup")
# async def startup_event():
#     from app.core.db import init_db
#     await init_db()

# Simple root endpoint for testing
@app.get("/")
def read_root():
    return {"message": "Finanzio API is running!"}