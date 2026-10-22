from datetime import date
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP

from flask import Flask, render_template, request, redirect, url_for

from database import add_expense, delete_expense, get_categories, get_expense, get_months, get_total, get_total_by_category, init_db, get_expenses, update_expense

MAX_CENTS = 10**12

def create_app():
    app = Flask(__name__)
    app.jinja_env.filters["money"] = format_cents
    init_db()

    @app.route("/")
    def index():
        month = parse_month(request.args.get("month"))
        return render_index(month=month, edit_id=request.args.get("edit", type=int))

    @app.route("/add", methods=["POST"])
    def add():
        month = parse_month(request.form.get("month"))
        values, error = parse_expense_form()
        if error:
            return render_index(error, month=month)
        add_expense(*values)
        return redirect(url_for("index", month=month))

    @app.route("/edit/<int:expense_id>", methods=["GET", "POST"])
    def edit(expense_id):
        if get_expense(expense_id) is None:
            return redirect("/")

        if request.method == "GET":
            return redirect(url_for("index", edit=expense_id))

        month = parse_month(request.form.get("month"))
        values, error = parse_expense_form()
        if error:
            return render_index(error, month=month, edit_id=expense_id, edit_form=request.form)
        update_expense(expense_id, *values)
        return redirect(url_for("index", month=month))

    @app.route("/delete", methods=["POST"])
    def delete():
        month = parse_month(request.form.get("month"))
        try:
            expense_id = int(request.form["expense_id"])
        except (KeyError, ValueError):
            return redirect(url_for("index", month=month))
        delete_expense(expense_id)
        return redirect(url_for("index", month=month))

    return app

def parse_month(text):
    if not text or len(text) != 7:
        return None
    try:
        date.fromisoformat(text + "-01")
    except ValueError:
        return None
    return text

def parse_cents(text):
    try:
        amount = Decimal(text)
        if not amount.is_finite():
            return None
        return int((amount * 100).quantize(Decimal(1), rounding=ROUND_HALF_UP))
    except InvalidOperation:
        return None

def format_cents(cents):
    sign = "-" if cents < 0 else ""
    cents = abs(cents)
    return f"{sign}{cents // 100}.{cents % 100:02d}"

def parse_expense_form():
    amount = request.form["amount"].strip().replace(",",".")
    category = request.form["category"].strip()
    description = request.form["description"].strip()
    date_text = request.form["date"] or None

    cents = parse_cents(amount)
    if cents is None:
        return None, "Amount must be a number"

    if cents <= 0:
        return None, "Amount must be positive"

    if cents > MAX_CENTS:
        return None, "Amount is too large"

    if not category:
        return None, "Category can't be empty"

    if not description:
        return None, "Description can't be empty"

    if date_text:
        try:
            date_text = date.fromisoformat(date_text).isoformat()
        except ValueError:
            return None, "Date must be YYYY-MM-DD"

    return (cents, category, description, date_text), None

def render_index(error=None, edit_id=None, edit_form=None, month=None):
    expenses = get_expenses(month)
    if edit_id is not None and edit_form is None:
        match = next((e for e in expenses if e[0] == edit_id), None)
        if match:
            _, amount_cents, category, description, date_text = match
            edit_form = {"amount": format_cents(amount_cents), "category": category, "description": description, "date": date_text}
    if edit_form is None:
        edit_id = None
    return render_template("index.html", expenses=expenses, total=get_total(month), by_category=get_total_by_category(month), categories=get_categories(), months=get_months(), month=month, error=error, edit_id=edit_id, edit_form=edit_form)

if __name__ == "__main__":
    create_app().run(debug=True)
