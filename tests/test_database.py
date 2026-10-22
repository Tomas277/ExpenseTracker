def test_add_and_get(db):
    db.add_expense(1250, "Food", "Lunch", "2026-10-01")
    rows = db.get_expenses()
    assert len(rows) == 1
    _, amount, category, description, date_text = rows[0]
    assert (amount, category, description, date_text) == (1250, "Food", "Lunch", "2026-10-01")


def test_default_date_is_today(db):
    from datetime import date

    db.add_expense(1, "Food", "x")
    assert db.get_expenses()[0][4] == date.today().isoformat()


def test_expenses_sorted_newest_first(db):
    db.add_expense(1, "a", "old", "2026-01-01")
    db.add_expense(1, "a", "new", "2026-06-01")
    assert [r[3] for r in db.get_expenses()] == ["new", "old"]


def test_delete(db):
    db.add_expense(1, "a", "x", "2026-01-01")
    expense_id = db.get_expenses()[0][0]
    db.delete_expense(expense_id)
    assert db.get_expenses() == []


def test_totals(db):
    db.add_expense(10, "Food", "a", "2026-01-01")
    db.add_expense(5, "Food", "b", "2026-01-02")
    db.add_expense(20, "Rent", "c", "2026-01-03")
    assert db.get_total() == 35
    assert dict(db.get_total_by_category()) == {"Food": 15, "Rent": 20}


def test_empty_total_is_zero(db):
    assert db.get_total() == 0
    assert db.get_total_by_category() == []


def test_categories_empty_on_fresh_db(db):
    assert db.get_categories() == []


def test_add_expense_saves_category(db):
    db.add_expense(1, "Food", "x", "2026-01-01")
    db.add_expense(1, "Rent", "y", "2026-01-02")
    assert db.get_categories() == ["Food", "Rent"]


def test_categories_deduplicated_case_insensitive(db):
    db.add_expense(1, "Food", "x", "2026-01-01")
    db.add_expense(1, "food", "y", "2026-01-02")
    assert db.get_categories() == ["Food"]


def test_category_kept_after_expense_deleted(db):
    db.add_expense(1, "Food", "x", "2026-01-01")
    db.delete_expense(db.get_expenses()[0][0])
    assert db.get_categories() == ["Food"]


def test_init_db_backfills_categories(db):
    import sqlite3

    conn = sqlite3.connect(db.DB_PATH)
    conn.execute("INSERT INTO expenses (amount_cents, category, description, date) VALUES (1, 'Old', 'x', '2026-01-01')")
    conn.commit()
    conn.close()
    db.init_db()
    assert db.get_categories() == ["Old"]


def test_get_expense(db):
    db.add_expense(5, "Food", "x", "2026-01-01")
    expense_id = db.get_expenses()[0][0]
    assert db.get_expense(expense_id) == (expense_id, 5, "Food", "x", "2026-01-01")
    assert db.get_expense(999) is None


def test_update_expense(db):
    db.add_expense(5, "Food", "x", "2026-01-01")
    expense_id = db.get_expenses()[0][0]
    db.update_expense(expense_id, 750, "Rent", "y", "2026-02-02")
    assert db.get_expense(expense_id) == (expense_id, 750, "Rent", "y", "2026-02-02")
    assert db.get_categories() == ["Food", "Rent"]


def test_update_expense_keeps_date_when_none(db):
    db.add_expense(5, "Food", "x", "2026-01-01")
    expense_id = db.get_expenses()[0][0]
    db.update_expense(expense_id, 6, "Food", "x")
    assert db.get_expense(expense_id)[4] == "2026-01-01"


def test_totals_are_exact_for_cents(db):
    for _ in range(10):
        db.add_expense(10, "Food", "dime", "2026-01-01")
    db.add_expense(20, "Food", "x", "2026-01-01")
    assert db.get_total() == 120


def test_init_db_migrates_float_amounts_to_cents(tmp_path, monkeypatch):
    import sqlite3

    import database

    path = str(tmp_path / "old.db")
    monkeypatch.setattr(database, "DB_PATH", path)
    conn = sqlite3.connect(path)
    conn.execute("CREATE TABLE expenses (id INTEGER PRIMARY KEY AUTOINCREMENT, amount REAL NOT NULL, category TEXT NOT NULL, description TEXT, date TEXT NOT NULL)")
    conn.executemany(
        "INSERT INTO expenses (amount, category, description, date) VALUES (?, ?, ?, ?)",
        [(12.5, "Food", "a", "2026-01-01"), (0.1 + 0.2, "Rent", "b", "2026-01-02"), (980.75, "Food", "c", "2026-01-03")],
    )
    conn.commit()
    conn.close()

    database.init_db()
    assert [(r[0], r[1]) for r in database.get_expenses()[::-1]] == [(1, 1250), (2, 30), (3, 98075)]

    database.init_db()
    assert database.get_total() == 1250 + 30 + 98075
    database.add_expense(100, "Food", "new", "2026-01-04")
    assert database.get_expenses()[0][0] == 4


def add_two_months(db):
    db.add_expense(1000, "Food", "oct food", "2026-10-05")
    db.add_expense(2000, "Rent", "oct rent", "2026-10-01")
    db.add_expense(500, "Food", "sep food", "2026-09-20")


def test_get_expenses_filtered_by_month(db):
    add_two_months(db)
    assert [r[3] for r in db.get_expenses(month="2026-10")] == ["oct food", "oct rent"]
    assert [r[3] for r in db.get_expenses(month="2026-09")] == ["sep food"]


def test_no_month_returns_everything(db):
    add_two_months(db)
    assert len(db.get_expenses()) == 3
    assert len(db.get_expenses(month=None)) == 3
    assert len(db.get_expenses(month="")) == 3
    assert db.get_total() == 3500


def test_total_filtered_by_month(db):
    add_two_months(db)
    assert db.get_total(month="2026-10") == 3000
    assert db.get_total(month="2026-09") == 500


def test_total_by_category_filtered_by_month(db):
    add_two_months(db)
    assert dict(db.get_total_by_category(month="2026-10")) == {"Food": 1000, "Rent": 2000}
    assert dict(db.get_total_by_category(month="2026-09")) == {"Food": 500}


def test_month_without_expenses_is_empty(db):
    add_two_months(db)
    assert db.get_expenses(month="2026-01") == []
    assert db.get_total(month="2026-01") == 0
    assert db.get_total_by_category(month="2026-01") == []


def test_month_filter_does_not_match_other_years(db):
    db.add_expense(100, "Food", "this year", "2026-10-05")
    db.add_expense(100, "Food", "last year", "2025-10-05")
    assert [r[3] for r in db.get_expenses(month="2026-10")] == ["this year"]


def test_month_filter_uses_parameter_not_sql_text(db):
    add_two_months(db)
    assert db.get_expenses(month="2026-10' OR '1'='1") == []


def test_get_months_newest_first_and_distinct(db):
    assert db.get_months() == []
    add_two_months(db)
    db.add_expense(100, "Food", "older", "2025-12-31")
    assert db.get_months() == ["2026-10", "2026-09", "2025-12"]
