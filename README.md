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

## About

The initial version was hand-coded as a practice project to remind myself of the tech behind a small web app. Development continues with Claude Code (security checks, polish, new features).

Tech and concepts used:
- Flask routes and form handling
- Jinja templates
- Raw `sqlite3` with parameterized queries
- POST-redirect-GET pattern
- Server-side input validation

Ideas for later: edit expenses, filter by month, CSV export.
