from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import init_db
from app.routers import user_routes, verb_routes


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Управление жизненным циклом приложения"""
    # Инициализация БД при запуске
    await init_db()
    yield
    # Очистка ресурсов при остановке (если необходимо)


app = FastAPI(
    title="FastAPI Project",
    description="FastAPI application with PostgreSQL",
    version="1.0.0",
    lifespan=lifespan
)

# Настройка CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Подключение роутеров
app.include_router(user_routes.router)
app.include_router(verb_routes.router)


@app.get("/")
async def root():
    """Корневой endpoint"""
    return {"message": "FastAPI application is running"}


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}


