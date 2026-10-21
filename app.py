import math
from datetime import date

from flask import Flask, render_template, request, redirect

from database import add_expense, delete_expense, get_categories, get_expense, get_total, get_total_by_category, init_db, get_expenses, update_expense

app = Flask(__name__)
init_db()

@app.route("/")
def index():
    return render_index()

def parse_expense_form():
    amount = request.form["amount"].strip().replace(",",".")
    category = request.form["category"].strip()
    description = request.form["description"].strip()
    date_text = request.form["date"] or None

    try:
        amount = float(amount)
    except ValueError:
        return None, "Amount must be a number"

    if not math.isfinite(amount):
        return None, "Amount must be a number"

    if amount <= 0:
        return None, "Amount must be positive"

    if not category:
        return None, "Category can't be empty"

    if not description:
        return None, "Description can't be empty"

    if date_text:
        try:
            date_text = date.fromisoformat(date_text).isoformat()
        except ValueError:
            return None, "Date must be YYYY-MM-DD"

    return (amount, category, description, date_text), None

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
        _, amount, category, description, date_text = expense
        form = {"amount": "%.2f" % amount, "category": category, "description": description, "date": date_text}
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

def render_index(error=None):
    return render_template("index.html", expenses=get_expenses(), total=get_total(), by_category=get_total_by_category(), categories=get_categories(), error=error)

if __name__ == "__main__":
    app.run(debug=True)
