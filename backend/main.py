from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from config import CORS_ORIGINS
from db.database import init_db
from db.seed import seed
from routes.clients import router as clients_router
from routes.alerts import router as alerts_router
from routes.agents import router as agents_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    seed()
    yield


app = FastAPI(title="WS Shadow API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(clients_router)
app.include_router(alerts_router)
app.include_router(agents_router)


@app.get("/")
async def root():
    return {"app": "WS Shadow", "status": "running"}
