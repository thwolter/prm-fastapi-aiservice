from fastapi import FastAPI

from app.services.router import router as service_router
from app.keywords.router import router as keywords_router

app = FastAPI()

app.include_router(service_router)
app.include_router(keywords_router)


@app.get("/")
async def root():
    return {"message": "Hello World"}
