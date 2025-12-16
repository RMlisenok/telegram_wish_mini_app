from fastapi import FastAPI


app = FastAPI()


@app.get('/')
async def root():
    return {'message': 'Backend Telegramm mini app work'}