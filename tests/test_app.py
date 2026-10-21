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
    assert db.get_expenses()[0][1] == 10


def test_comma_decimal_accepted(client, db):
    add(client, amount="12,50")
    assert db.get_expenses()[0][1] == 12.5


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


def test_edit_page_prefilled(client, db):
    add(client, amount="12,5", description="Lunch")
    expense_id = db.get_expenses()[0][0]
    body = client.get(f"/edit/{expense_id}").data
    assert b'value="12.50"' in body
    assert b'value="Lunch"' in body
    assert b'value="2026-10-01"' in body


def test_edit_saves_and_redirects(client, db):
    add(client)
    expense_id = db.get_expenses()[0][0]
    assert edit(client, expense_id).status_code == 302
    assert db.get_expense(expense_id) == (expense_id, 20, "Rent", "Flat", "2026-11-01")


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
    assert b'value="Changed"' in response.data
    assert db.get_expense(expense_id)[3] == "Lunch"


def test_edit_missing_expense_redirects(client):
    assert client.get("/edit/999").status_code == 302
    assert edit(client, 999).status_code == 302


def test_index_links_to_edit(client, db):
    add(client)
    expense_id = db.get_expenses()[0][0]
    assert f'href="/edit/{expense_id}"'.encode() in client.get("/").data
