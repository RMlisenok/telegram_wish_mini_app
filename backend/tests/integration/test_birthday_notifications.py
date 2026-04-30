import pytest
from datetime import datetime, timedelta # noqa
from freezegun import freeze_time
from app.services.notification_service_bot import NotificationService


class TestScenario15BirthdayNotifications:

    @pytest.mark.asyncio
    @freeze_time("2024-03-08")  # За 7 дней до ДР (15 марта)
    async def test_birthday_reminder_7_days(
        self, client, test_users, auth_headers, mock_telegram_bot, db_session
    ):

        await client.put(
            "/v1/users/me",
            json={"birth_date": "1990-03-15"},
            headers=auth_headers["user_a"]
        )

        subscribe_data = {"target_user_id": test_users["user_a"].id}
        await client.post(
            "/v1/subscriptions/users",
            json=subscribe_data,
            headers=auth_headers["user_b"]
        )

        service = NotificationService()
        await service.check_birthdays_and_notify(db_session)

        user_b_telegram_id = test_users["user_b"].telegram_id
        messages = mock_telegram_bot.get_messages_for_user(user_b_telegram_id)

        assert "Через неделю день рождения" in messages[-1]["text"]

    @pytest.mark.asyncio
    @freeze_time("2024-03-14")  # За 1 день до ДР
    async def test_birthday_reminder_1_day(
        self, client, test_users, auth_headers, mock_telegram_bot, db_session
    ):
        await client.put(
            "/v1/users/me",
            json={"birth_date": "1990-03-15"},
            headers=auth_headers["user_a"]
        )

        subscribe_data = {"target_user_id": test_users["user_a"].id}
        await client.post(
            "/v1/subscriptions/users",
            json=subscribe_data,
            headers=auth_headers["user_b"]
        )

        from app.services.notification_service_bot import NotificationService

        service = NotificationService()
        await service.check_birthdays_and_notify(db_session)

        user_b_telegram_id = test_users["user_b"].telegram_id
        messages = mock_telegram_bot.get_messages_for_user(user_b_telegram_id)

        assert "Завтра день рождения" in messages[-1]["text"]

    @pytest.mark.asyncio
    @freeze_time("2024-03-15")  # В день ДР
    async def test_birthday_reminder_today(
        self, client, test_users, auth_headers, mock_telegram_bot, db_session
    ):

        await client.put(
            "/v1/users/me",
            json={"birth_date": "1990-03-15"},
            headers=auth_headers["user_a"]
        )

        subscribe_data = {"target_user_id": test_users["user_a"].id}
        await client.post(
            "/v1/subscriptions/users",
            json=subscribe_data,
            headers=auth_headers["user_b"]
        )

        service = NotificationService()
        await service.check_birthdays_and_notify(db_session)

        user_b_telegram_id = test_users["user_b"].telegram_id
        messages = mock_telegram_bot.get_messages_for_user(user_b_telegram_id)

        assert "Сегодня день рождения" in messages[-1]["text"]
