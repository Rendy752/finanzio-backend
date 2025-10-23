from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.core.db import init_db
from app.api.v1.endpoints import router as api_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    print("Application startup complete.")
    yield
    print("Application shutdown complete.")

app = FastAPI(
    title="Finanzio Backend API",
    version="1.0.0",
    description="Backend services for the multiplatform personal finance and SME bookkeeping application.",
    lifespan=lifespan
)
# ---------------------------------

# 1. Tentukan origins yang diizinkan. Gunakan "*" untuk development agar 
# bisa diakses dari port localhost manapun (e.g., Flutter web development server).
origins = [
    "*", # Izinkan semua origins (Hanya untuk DEVELOPMENT!)
    # "http://localhost:59986", # Anda bisa spesifik jika tahu port Flutter
    # "http://localhost:8080",
    # "http://localhost:3000",
]

# 2. Tambahkan middleware CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True, # Mengizinkan cookies, header otorisasi, dll.
    allow_methods=["*"], # Mengizinkan semua method (POST, GET, PUT, DELETE)
    allow_headers=["*"], # Mengizinkan semua header (termasuk Content-Type yang dibutuhkan Dio)
)

# ---------------------------------

# Include API routes
app.include_router(api_router, prefix="/api/v1")

@app.get("/")
def read_root():
    return {"message": "Finanzio API is running! Go to /docs for endpoints."}