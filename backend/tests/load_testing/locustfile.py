import random
from locust import HttpUser, task, between


class WishlistUser(HttpUser):
    # Время ожидания между действиями пользователя (от 1 до 5 секунд)
    wait_time = between(1, 5)
    verify = False

    def on_start(self):
        """Выполняется при 'входе' пользователя — здесь можно задать токен"""
        self.auth_header = {"Authorization": "Bearer YOUR_TEST_TOKEN"}

    @task(3)
    def view_my_wishlists(self):
        """Самый частый запрос: просмотр своих списков"""
        self.client.get("/v1/wishlists/1", headers=self.auth_header)

    @task(1)
    def get_recommendations(self):
        """Тяжелый запрос: генерация рекомендаций"""
        # Мы имитируем запрос к API, который дергает RecommendationService
        self.client.get("/v1/recommendations/check/user/1", headers=self.auth_header)

    @task(2)
    def check_notifications(self):
        """Проверка настроек уведомлений"""
        self.client.get("/v1/notifications/settings", headers=self.auth_header)

    @task(1)
    def create_wish(self):
        """Запись в базу: создание желания"""
        self.client.post("/v1/wishes/", json={
            "title": f"Test Wish {random.randint(1, 1000)}",
            "description": "Load test description",
            "wishlist_id": 1
        }, headers=self.auth_header)