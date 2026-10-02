from django.test import TestCase


class DictionaryTableTests(TestCase):
    def test_index_displays_empty_table(self):
        response = self.client.get("/")

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Таблица словаря")
        self.assertContains(response, "В словаре пока нет строк.")

    def test_can_add_and_delete_a_dictionary_row(self):
        add_response = self.client.post(
            "/",
            {"action": "add", "key": "Цвет", "value": "Синий"},
        )

        self.assertRedirects(add_response, "/")
        self.assertContains(self.client.get("/"), "Синий")

        table = self.client.session["table_rows"]
        row_id = next(iter(table))
        delete_response = self.client.post(
            "/",
            {"action": "delete", "row_id": row_id},
        )

        self.assertRedirects(delete_response, "/")
        self.assertContains(self.client.get("/"), "В словаре пока нет строк.")
