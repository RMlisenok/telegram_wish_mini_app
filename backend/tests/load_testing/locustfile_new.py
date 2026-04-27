import random
from locust import HttpUser, task, between


class WishlistStressTest(HttpUser):
    wait_time = between(0.5, 1.5)

    # Список сценариев
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
    def run_scenarios(self):
        path, method = random.choice(self.endpoints)

        # Важно: используем catch_response=True
        with self.client.request(
                method,
                path,
                catch_response=True,
                verify=False
        ) as response:
            # Если мы получили 401, мы хотим, чтобы в отчете это было ФЕЙЛОМ
            if response.status_code == 401:
                response.failure(f"❌ Security Block: {response.status_code}")
            # Если 404 — тоже фейл
            elif response.status_code == 404:
                response.failure("🚫 Route Not Found")
            # Если 500 — критический фейл
            elif response.status_code >= 500:
                response.failure("🔥 Server Crash")
            # Если вдруг пришел 200/201 (без токена это странно, но вдруг)
            elif response.status_code in [200, 201]:
                response.success()
            else:
                response.failure(f"Unknown status: {response.status_code}")