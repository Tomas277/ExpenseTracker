# ExpenseTracker

Small Flask + SQLite web app for tracking personal expenses. Add expenses with an amount, category, description and date, see the total and per-category totals, and delete entries.

## Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Run

```bash
python app.py
```

Open http://127.0.0.1:5000. The SQLite database (`expenses.db`) is created next to the app on first run.

## Layout

- `app.py` – Flask routes and input validation
- `database.py` – SQLite access
- `templates/`, `static/` – HTML and CSS
