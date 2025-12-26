from aiogram import Router, F, types
from sqlalchemy import update, select
from app.core.db import AsyncSessionLocal
from app.models.access import AccessRequest
from app.models.subscription import Subscription

router = Router()

@router.callback_query(F.data.startswith("approve_"))
async def approve_access_callback(callback: types.CallbackQuery):
    request_id = int(callback.data.split("_")[1])

    async with AsyncSessionLocal() as session:
        try:
            await session.commit()
            await callback.message.edit_text(
                text=callback.message.text + "\n\n✅ <b>Доступ одобрен</b>",
                parse_mode="HTML"
            )
        except Exception as e:
            await callback.answer("Ошибка при обработке заявки")


@router.callback_query(F.data.startswith("reject_"))
async def reject_access_callback(callback: types.CallbackQuery):
    request_id = int(callback.data.split("_")[1])

    async with AsyncSessionLocal() as session:
        await callback.message.edit_text(
            text=callback.message.text + "\n\n❌ <b>Доступ отклонен</b>",
            parse_mode="HTML"
        )
        await callback.answer("Заявка отклонена")


@router.callback_query(F.data == "move_to_executed")
async def move_to_executed_callback(callback: types.CallbackQuery):
    async with AsyncSessionLocal() as session:
        # query = update(Wish).where(user_id=..., status='booked').values(status='executed')
        await session.commit()

    await callback.message.edit_text("✅ Ваши желания перемещены в список исполненных!")
    await callback.answer()


@router.callback_query(F.data == "keep_as_is")
async def keep_as_is_callback(callback: types.CallbackQuery):
    async with AsyncSessionLocal() as session:
        await session.commit()

    await callback.message.edit_text("❌ Метки бронирования сняты, желания снова доступны всем.")
    await callback.answer()