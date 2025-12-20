from aiogram import Router, types

router = Router()

@router.message(commands=["start"])
async def start(message: types.Message):
    await message.answer(
        "Привет! 👋\n\n"
        "Нажми «Что подарить», и я подберу идеи 🎁"
    )
