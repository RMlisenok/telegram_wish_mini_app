import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("8558976967:AAFnChpNZ6TBoXOai-5OAilw0Mc1Dv_a7Go")
DATABASE_URL = os.getenv("postgresql+asyncpg://tguser:1@localhost:5432/tgminiapp")
