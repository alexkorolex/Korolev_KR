from django.conf import settings
from django.test import Client, TestCase


class DictionaryTableTests(TestCase):
    def test_index_displays_synthetic_dictionary_data(self):
        response = self.client.get("/")

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Таблица словаря")
        self.assertContains(response, "Блокнот А5")
        self.assertContains(response, "249 ₽")

    def test_can_add_and_delete_a_dictionary_row(self):
        add_response = self.client.get(
            "/",
            {"action": "add", "key": "Цвет", "value": "Синий"},
        )

        self.assertRedirects(add_response, "/")
        response = self.client.get("/")
        self.assertContains(response, "Синий")
        self.assertContains(response, "Блокнот А5")

        table = self.client.session["table_rows"]
        row_id = next(
            row_id for row_id, row in table.items()
            if row["key"] == "Цвет" and row["value"] == "Синий"
        )
        delete_response = self.client.post(
            "/",
            {"action": "delete", "row_id": row_id},
        )

        self.assertRedirects(delete_response, "/")
        response = self.client.get("/")
        self.assertNotContains(response, "Синий")
        self.assertContains(response, "Блокнот А5")

    def test_get_add_and_csrf_protected_delete_work_from_replit_preview(self):
        if not settings.REPLIT_DEV_DOMAIN:
            self.skipTest("REPLIT_DEV_DOMAIN is not configured")

        client = Client(enforce_csrf_checks=True)
        host = f"{settings.REPLIT_DEV_DOMAIN}:5000"
        origin = f"https://{host}"

        page = client.get("/", secure=True, HTTP_HOST=host)
        self.assertEqual(page.status_code, 200)

        add_response = client.get(
            "/",
            {"action": "add", "key": "Цвет", "value": "Синий"},
            secure=True,
            HTTP_HOST=host,
        )

        self.assertEqual(add_response.status_code, 302)
        self.assertContains(client.get("/", secure=True, HTTP_HOST=host), "Синий")

        row_id = next(
            row_id for row_id, row in client.session["table_rows"].items()
            if row["key"] == "Цвет" and row["value"] == "Синий"
        )
        delete_response = client.post(
            "/",
            {
                "action": "delete",
                "row_id": row_id,
                "csrfmiddlewaretoken": client.cookies["csrftoken"].value,
            },
            secure=True,
            HTTP_HOST=host,
            HTTP_ORIGIN=origin,
        )

        self.assertEqual(delete_response.status_code, 302)
        self.assertContains(client.get("/", secure=True, HTTP_HOST=host), "Блокнот А5")
