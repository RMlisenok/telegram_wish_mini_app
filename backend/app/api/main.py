import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routers import user, questionnaire

# Настройка логов
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Подари мне API",
    description="API для Telegram Mini-App управления вишлистами и подарками",
    version="1.0.0"
)

# Настройка CORS для Mini App
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # В продакшене укажи конкретные домены
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(user.router)
app.include_router(questionnaire.router) # Подключаем анкеты

@app.get("/")
async def root():
    return {"message": "Welcome to Podari Mne API"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)