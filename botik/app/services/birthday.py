from app.db.models.user import User

def birthday_text(user: User, days: int) -> str:
    if days == 0:
        return f"🎉 Сегодня день рождения у {user.name}!"
    return f"🎂 Через {days} дней день рождения у {user.name}"
