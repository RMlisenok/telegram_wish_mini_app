import random
from locust import HttpUser, task, between


class WishlistStressTest(HttpUser):
    # Уменьшим время ожидания, чтобы быстрее набрать статистику
    wait_time = between(0.1, 0.5)

    # 20 сценариев (проверь, чтобы в Host в браузере НЕ БЫЛО слэша в конце)
    endpoints = [
        ("/v1/notifications/settings", "GET"),
        ("/v1/recommendations/check/user/1", "GET"),
        ("/v1/wishlists/1", "GET"),
        ("/v1/wishes/", "POST"),
        ("/v1/users/me", "GET"),
        ("/v1/subscriptions/my", "GET"),
        ("/v1/reservation/incoming", "GET"),
        ("/v1/reservation/outgoing", "GET"),
        ("/v1/questionnaire/active", "GET"),
        ("/v1/access-requests/pending", "GET"),
        ("/v1/auth/status", "GET"),
        ("/v1/wishlists/1/wishes", "GET"),
        ("/v1/tags/", "GET"),
        ("/v1/gifts/popular", "GET"),
        ("/v1/notifications/history", "GET"),
        ("/v1/s3/upload-url", "POST"),
        ("/v1/wishlists/search", "GET"),
        ("/v1/users/search", "GET"),
        ("/v1/recommendations/daily", "GET"),
        ("/v1/wishlists/my", "GET")
    ]

    @task
    def stress_test(self):
        path, method = random.choice(self.endpoints)

        # catch_response=True — КЛЮЧЕВОЙ параметр, чтобы подсветить ошибки красным
        with self.client.request(
                method=method,
                url=path,
                catch_response=True,
                verify=False
        ) as response:
            # Вместо длинного if/elif сделайте так:
            if response.status_code in [200, 201]:
                response.success()
            else:
                response.failure(f"Error: {response.status_code}")
            # Если получили 401 — помечаем как ОШИБКУ (для красоты отчета)
            # if response.status_code == 401:
            #     response.failure(f"🔒 Auth required (401)")
            # # Если 404
            # elif response.status_code == 404:
            #     response.failure("❗ Not Found (404)")
            # # Если 500 и выше
            # elif response.status_code >= 500:
            #     response.failure(f"💥 Server Error ({response.status_code})")
            # # Все остальное (200, 201) — успех
            # else:
            #     response.success()
