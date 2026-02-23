from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database import Base, engine
import electricity
import water
import cleaning
import analysis
import achievements

# Auto-create all tables on startup (non-fatal if DB not yet configured)
try:
    Base.metadata.create_all(bind=engine)
    print("✅ EcoSense: Database tables ready")
except Exception as e:
    print(f"⚠️  EcoSense: DB not connected — update DB_PASSWORD in backend/.env\n   Error: {e}")

app = FastAPI(
    title="EcoSense API",
    description="Backend for EcoSense — Smart Home Resource Analyzer",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
)

# Allow all origins for hackathon (tighten for production)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://ecosense-frontend-beta.vercel.app",  # Your main frontend URL
        "https://ecosense-frontend.vercel.app",        # Your Vercel project URL
        "http://localhost:3000",                        # For local development (optional)
        "http://127.0.0.1:3000"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount routers
app.include_router(electricity.router,   prefix="/api/electricity",   tags=["Electricity"])
app.include_router(water.router,         prefix="/api/water",         tags=["Water"])
app.include_router(cleaning.router,      prefix="/api/cleaning",      tags=["Cleaning"])
app.include_router(analysis.router,      prefix="/api/analysis",      tags=["Analysis"])
app.include_router(achievements.router,  prefix="/api/achievements",  tags=["Achievements"])


@app.get("/")
def root():
    return {"message": "EcoSense API is running 🌿", "docs": "/api/docs"}

@app.get("/api/health")
def health_check():
    return {"status": "ok", "message": "Backend is running!"}
