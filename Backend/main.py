from fastapi import FastAPI
from db.mongodb import lifespan
from routers import auth, responses, generate

from pathlib import Path
from fastapi.staticfiles import StaticFiles

app = FastAPI(lifespan=lifespan)

UPLOAD_DIR = Path(__file__).resolve().parent / "uploads"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=str(UPLOAD_DIR)), name="uploads")


@app.get("/", include_in_schema=False)
async def landing_page():
    return {"message": "Poshu Sheba AI API is running"}


# Include routers
app.include_router(auth.router)
app.include_router(responses.router)
app.include_router(generate.router)
