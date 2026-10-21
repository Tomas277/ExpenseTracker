from datetime import date
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP

from flask import Flask, render_template, request, redirect

from database import add_expense, delete_expense, get_categories, get_expense, get_total, get_total_by_category, init_db, get_expenses, update_expense

MAX_CENTS = 10**12

def create_app():
    app = Flask(__name__)
    app.jinja_env.filters["money"] = format_cents
    init_db()

    @app.route("/")
    def index():
        return render_index()

    @app.route("/add", methods=["POST"])
    def add():
        values, error = parse_expense_form()
        if error:
            return render_index(error)
        add_expense(*values)
        return redirect("/")

    @app.route("/edit/<int:expense_id>", methods=["GET", "POST"])
    def edit(expense_id):
        expense = get_expense(expense_id)
        if expense is None:
            return redirect("/")

        if request.method == "POST":
            values, error = parse_expense_form()
            if not error:
                update_expense(expense_id, *values)
                return redirect("/")
            form = request.form
        else:
            _, amount_cents, category, description, date_text = expense
            form = {"amount": format_cents(amount_cents), "category": category, "description": description, "date": date_text}
            error = None

        return render_template("edit.html", expense_id=expense_id, form=form, categories=get_categories(), error=error)

    @app.route("/delete", methods=["POST"])
    def delete():
        try:
            expense_id = int(request.form["expense_id"])
        except (KeyError, ValueError):
            return redirect("/")
        delete_expense(expense_id)
        return redirect("/")

    return app

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

def render_index(error=None):
    return render_template("index.html", expenses=get_expenses(), total=get_total(), by_category=get_total_by_category(), categories=get_categories(), error=error)

if __name__ == "__main__":
    create_app().run(debug=True)
