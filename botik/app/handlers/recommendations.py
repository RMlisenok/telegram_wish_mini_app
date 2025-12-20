from aiogram import Router, types
from aiogram import F
from app.recommendations.service import recommend_by_tag

router = Router()

@router.message(F.text == "Что подарить")
async def recommend_handler(message: types.Message):
    user_id = message.from_user.id
    tag = "гарри поттер"

    await message.answer("📨 Отправили вам подборку в личные сообщения")

    items = await recommend_by_tag(user_id, tag)

    text = f"🎁 Подборка по тегу «{tag}»:\n\n"
    for i, item in enumerate(items, 1):
        text += f"{i}. {item['title']}\n{item['url']}\n\n"

    await message.answer(text[:2000])
