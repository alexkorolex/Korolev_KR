from uuid import uuid4

from django.shortcuts import redirect, render


SESSION_TABLE_KEY = "table_rows"
SESSION_INITIALIZED_KEY = "table_initialized"
SAMPLE_ROWS = (
    ("Товар", "Блокнот А5"),
    ("Категория", "Канцелярия"),
    ("Цвет", "Тёмно-синий"),
    ("Цена", "249 ₽"),
    ("Остаток", "18 шт."),
)


def index(request):
    if not request.session.get(SESSION_INITIALIZED_KEY):
        existing_table = request.session.get(SESSION_TABLE_KEY)
        if not isinstance(existing_table, dict):
            existing_table = {}

        existing_keys = {
            row.get("key")
            for row in existing_table.values()
            if isinstance(row, dict)
        }
        for key, value in SAMPLE_ROWS:
            if key not in existing_keys:
                existing_table[str(uuid4())] = {"key": key, "value": value}

        request.session[SESSION_TABLE_KEY] = existing_table
        request.session[SESSION_INITIALIZED_KEY] = True

    table = request.session.get(SESSION_TABLE_KEY, {})
    if not isinstance(table, dict):
        table = {}

    error = None
    if request.method == "GET" and request.GET.get("action") == "add":
        key = request.GET.get("key", "").strip()
        value = request.GET.get("value", "").strip()

        if not key or not value:
            error = "Заполните оба поля, чтобы добавить строку."
        else:
            table[str(uuid4())] = {"key": key, "value": value}
            request.session[SESSION_TABLE_KEY] = table
            return redirect("index")

    elif request.method == "POST":
        action = request.POST.get("action")

        if action == "delete":
            row_id = request.POST.get("row_id", "")
            if row_id in table:
                del table[row_id]
                request.session[SESSION_TABLE_KEY] = table
            return redirect("index")

    rows = [
        {"id": row_id, "key": row["key"], "value": row["value"]}
        for row_id, row in table.items()
        if isinstance(row, dict) and "key" in row and "value" in row
    ]
    return render(request, "main/index.html", {
        "rows": rows,
        "error": error,
    }, using="jinja2")
