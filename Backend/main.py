from fastapi import FastAPI
from db.mongodb import lifespan
from routers import auth, responses, generate

app = FastAPI(lifespan=lifespan)


@app.get("/", include_in_schema=False)
async def landing_page():
    return {"message": "Poshu Sheba AI API is running"}


# Include routers
app.include_router(auth.router)
app.include_router(responses.router)
app.include_router(generate.router)
