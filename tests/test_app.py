import pytest


def add(client, **overrides):
    data = {"amount": "10", "category": "Food", "description": "Lunch", "date": "2026-10-01"}
    data.update(overrides)
    return client.post("/add", data=data)


def test_index_ok(client):
    assert client.get("/").status_code == 200


def test_add_redirects_and_saves(client, db):
    response = add(client)
    assert response.status_code == 302
    assert db.get_expenses()[0][1] == 1000


def test_comma_decimal_accepted(client, db):
    add(client, amount="12,50")
    assert db.get_expenses()[0][1] == 1250


@pytest.mark.parametrize("amount", ["abc", "", "nan", "inf", "-inf", "1e999"])
def test_invalid_amount_rejected(client, db, amount):
    response = add(client, amount=amount)
    assert b"Amount must be a number" in response.data
    assert db.get_expenses() == []


@pytest.mark.parametrize("amount", ["0", "-5"])
def test_non_positive_amount_rejected(client, db, amount):
    response = add(client, amount=amount)
    assert b"Amount must be positive" in response.data
    assert db.get_expenses() == []


def test_empty_category_rejected(client, db):
    assert b"Category can&#39;t be empty" in add(client, category="  ").data
    assert db.get_expenses() == []


def test_empty_description_rejected(client, db):
    assert b"Description can&#39;t be empty" in add(client, description="").data
    assert db.get_expenses() == []


def test_bad_date_rejected(client, db):
    assert b"Date must be YYYY-MM-DD" in add(client, date="not-a-date").data
    assert db.get_expenses() == []


def test_date_normalized(client, db):
    add(client, date="20261020")
    assert db.get_expenses()[0][4] == "2026-10-20"


def test_blank_date_defaults_to_today(client, db):
    from datetime import date

    add(client, date="")
    assert db.get_expenses()[0][4] == date.today().isoformat()


def test_delete(client, db):
    add(client)
    expense_id = db.get_expenses()[0][0]
    assert client.post("/delete", data={"expense_id": expense_id}).status_code == 302
    assert db.get_expenses() == []


def test_delete_bad_id_does_not_crash(client):
    assert client.post("/delete", data={"expense_id": "x"}).status_code == 302
    assert client.post("/delete", data={}).status_code == 302


def test_html_is_escaped(client):
    add(client, description="<script>alert(1)</script>")
    body = client.get("/").data
    assert b"<script>alert(1)</script>" not in body
    assert b"&lt;script&gt;" in body


def test_new_category_suggested_on_index(client):
    add(client, category="Groceries")
    assert b'<li role="option">Groceries</li>' in client.get("/").data


def test_category_suggestion_is_escaped(client):
    add(client, category='"><script>')
    data = client.get("/").data
    assert b'"><script>' not in data
    assert b"&#34;&gt;&lt;script&gt;" in data


def edit(client, expense_id, **overrides):
    data = {"amount": "20", "category": "Rent", "description": "Flat", "date": "2026-11-01"}
    data.update(overrides)
    return client.post(f"/edit/{expense_id}", data=data)


def test_edit_row_prefilled_in_place(client, db):
    add(client, amount="12,5", description="Lunch")
    add(client, description="Other", date="2026-09-01")
    expense_id = db.get_expenses()[0][0]
    body = client.get(f"/?edit={expense_id}").data
    assert b'action="/edit/%d"' % expense_id in body
    assert b'value="12.50"' in body
    assert b'value="Lunch"' in body
    assert b'value="2026-10-01"' in body
    assert body.count(b'class="editing"') == 1
    assert b"Other" in body


def test_edit_unknown_id_shows_normal_page(client, db):
    add(client)
    assert b'class="editing"' not in client.get("/?edit=999").data
    assert b'class="editing"' not in client.get("/?edit=abc").data


def test_edit_get_redirects_to_row(client, db):
    add(client)
    expense_id = db.get_expenses()[0][0]
    response = client.get(f"/edit/{expense_id}")
    assert response.status_code == 302
    assert response.headers["Location"].endswith(f"/?edit={expense_id}")


def test_edit_saves_and_redirects(client, db):
    add(client)
    expense_id = db.get_expenses()[0][0]
    assert edit(client, expense_id).status_code == 302
    assert db.get_expense(expense_id) == (expense_id, 2000, "Rent", "Flat", "2026-11-01")


def test_edit_blank_date_keeps_existing(client, db):
    add(client)
    expense_id = db.get_expenses()[0][0]
    edit(client, expense_id, date="")
    assert db.get_expense(expense_id)[4] == "2026-10-01"


def test_edit_invalid_rejected_and_input_kept(client, db):
    add(client)
    expense_id = db.get_expenses()[0][0]
    response = edit(client, expense_id, amount="abc", description="Changed")
    assert b"Amount must be a number" in response.data
    assert b'class="editing"' in response.data
    assert b'value="Changed"' in response.data
    assert db.get_expense(expense_id)[3] == "Lunch"


def test_edit_missing_expense_redirects(client):
    assert client.get("/edit/999").status_code == 302
    assert edit(client, 999).status_code == 302


def test_index_links_to_edit(client, db):
    add(client)
    expense_id = db.get_expenses()[0][0]
    assert f'href="/?edit={expense_id}"'.encode() in client.get("/").data


def test_import_does_not_touch_database(tmp_path, monkeypatch):
    import importlib

    import app as app_module
    import database

    path = tmp_path / "untouched.db"
    monkeypatch.setattr(database, "DB_PATH", str(path))
    importlib.reload(app_module)
    assert not path.exists()


@pytest.mark.parametrize("amount, cents", [("12.345", 1235), ("0.1", 10), ("5", 500), ("1,05", 105), ("0.005", 1)])
def test_amount_stored_as_whole_cents(client, db, amount, cents):
    add(client, amount=amount)
    assert db.get_expenses()[0][1] == cents


def test_amount_rounding_to_zero_rejected(client, db):
    assert b"Amount must be positive" in add(client, amount="0.004").data
    assert db.get_expenses() == []


def test_huge_amount_rejected(client, db):
    assert b"Amount is too large" in add(client, amount="1e20").data
    assert db.get_expenses() == []


def test_amounts_displayed_with_two_decimals(client):
    add(client, amount="3")
    add(client, amount="0,1", category="Snacks", description="dime")
    body = client.get("/").data
    assert body.count("3.00 €".encode()) == 2
    assert body.count("0.10 €".encode()) == 2
    assert b"3.10 \xe2\x82\xac" in body
