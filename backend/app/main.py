from contextlib import asynccontextmanager
from fastapi import FastAPI

from app.db.database import Base, get_db, engine
from app.route.claim_route import router as claim_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup code
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        yield


app = FastAPI(lifespan=lifespan)


@app.get("/")
async def read_root():
    return {"Hello": "World"}


app.include_router(claim_router)
