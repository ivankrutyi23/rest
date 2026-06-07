import random
from locust import HttpUser, between, task


class BookBrowser(HttpUser):
    """Simulates concurrent users browsing the book catalog endpoint."""

    wait_time = between(1, 3)

    @task(5)
    def browse_default(self):
        with self.client.get(
            "/books/",
            name="GET /books/ [default]",
            catch_response=True,
        ) as resp:
            if resp.status_code == 200:
                body = resp.json()
                if "items" in body and "total" in body:
                    resp.success()
                else:
                    resp.failure("Unexpected response shape")
            else:
                resp.failure(f"HTTP {resp.status_code}")

    @task(3)
    def browse_paginated(self):
        page_size = random.choice([5, 10, 20])
        page_num = random.randint(0, 8)
        with self.client.get(
            f"/books/?limit={page_size}&offset={page_num * page_size}",
            name="GET /books/ [paginated]",
            catch_response=True,
        ) as resp:
            resp.success() if resp.status_code == 200 else resp.failure(f"HTTP {resp.status_code}")

    @task(2)
    def browse_sorted_by_year(self):
        with self.client.get(
            "/books/?sort_by=year",
            name="GET /books/ [sort_by=year]",
            catch_response=True,
        ) as resp:
            resp.success() if resp.status_code == 200 else resp.failure(f"HTTP {resp.status_code}")

    @task(2)
    def browse_by_status(self):
        chosen_status = random.choice(["free", "on_loan"])
        with self.client.get(
            f"/books/?status={chosen_status}",
            name="GET /books/ [status filter]",
            catch_response=True,
        ) as resp:
            resp.success() if resp.status_code == 200 else resp.failure(f"HTTP {resp.status_code}")

    @task(1)
    def browse_combined_filters(self):
        chosen_status = random.choice(["free", "on_loan"])
        chosen_sort = random.choice(["title", "year"])
        page_size = random.choice([5, 10])
        with self.client.get(
            f"/books/?status={chosen_status}&sort_by={chosen_sort}&limit={page_size}&offset=0",
            name="GET /books/ [combined]",
            catch_response=True,
        ) as resp:
            resp.success() if resp.status_code == 200 else resp.failure(f"HTTP {resp.status_code}")
