def test_add_and_get(db):
    db.add_expense(12.5, "Food", "Lunch", "2026-10-01")
    rows = db.get_expenses()
    assert len(rows) == 1
    _, amount, category, description, date_text = rows[0]
    assert (amount, category, description, date_text) == (12.5, "Food", "Lunch", "2026-10-01")


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
    conn.execute("INSERT INTO expenses (amount, category, description, date) VALUES (1, 'Old', 'x', '2026-01-01')")
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
    db.update_expense(expense_id, 7.5, "Rent", "y", "2026-02-02")
    assert db.get_expense(expense_id) == (expense_id, 7.5, "Rent", "y", "2026-02-02")
    assert db.get_categories() == ["Food", "Rent"]


def test_update_expense_keeps_date_when_none(db):
    db.add_expense(5, "Food", "x", "2026-01-01")
    expense_id = db.get_expenses()[0][0]
    db.update_expense(expense_id, 6, "Food", "x")
    assert db.get_expense(expense_id)[4] == "2026-01-01"
