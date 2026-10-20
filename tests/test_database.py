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
