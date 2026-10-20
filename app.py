from datetime import date

from flask import Flask, render_template, request, redirect

from database import add_expense, delete_expense, get_total, get_total_by_category, init_db, get_expenses

app = Flask(__name__)
init_db()

@app.route("/")
def index():
    return render_index()

@app.route("/add", methods=["POST"])
def add():
    amount = request.form["amount"].strip().replace(",",".")
    category = request.form["category"].strip()
    description = request.form["description"].strip()
    date_text = request.form["date"] or None

    try:
        amount = float(amount)
    except ValueError:
        return render_index("Amount must be a number")

    if amount <= 0:
        return render_index("Amount must be positive")

    if not category:
        return render_index("Category can't be empty")

    if not description:
        return render_index("Description can't be empty")

    if date_text:
        try:
            date.fromisoformat(date_text)
        except ValueError:
            return render_index("Date must be YYYY-MM-DD")

    add_expense(amount, category, description, date_text)
    return redirect("/")

@app.route("/delete", methods=["POST"])
def delete():
    try:
        expense_id = int(request.form["expense_id"])
    except (KeyError, ValueError):
        return redirect("/")
    delete_expense(expense_id)
    return redirect("/")

def render_index(error=None):
    return render_template("index.html", expenses=get_expenses(), total=get_total(), by_category=get_total_by_category(), error=error)

if __name__ == "__main__":
    app.run(debug=True)
