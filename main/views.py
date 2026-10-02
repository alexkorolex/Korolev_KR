from uuid import uuid4

from django.shortcuts import redirect, render


SESSION_TABLE_KEY = "table_rows"


def index(request):
    table = request.session.get(SESSION_TABLE_KEY, {})
    if not isinstance(table, dict):
        table = {}

    error = None
    if request.method == "POST":
        action = request.POST.get("action")

        if action == "add":
            key = request.POST.get("key", "").strip()
            value = request.POST.get("value", "").strip()

            if not key or not value:
                error = "Заполните оба поля, чтобы добавить строку."
            else:
                table[str(uuid4())] = {"key": key, "value": value}
                request.session[SESSION_TABLE_KEY] = table
                return redirect("index")

        elif action == "delete":
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
