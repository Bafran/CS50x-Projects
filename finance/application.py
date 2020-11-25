import os

from cs50 import SQL
from flask import Flask, flash, jsonify, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import apology, login_required, lookup, usd
import datetime

# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

# Custom filter
app.jinja_env.filters["usd"] = usd

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///finance.db")

# Make sure API key is set
if not os.environ.get("API_KEY"):
    raise RuntimeError("API_KEY not set")


@app.route("/")
@login_required
def index():

    positions = db.execute("SELECT * FROM userportfolio WHERE user_id = :user_id AND amount > 0", user_id = session['user_id'])
    symbols = db.execute("SELECT symbol FROM userportfolio WHERE user_id = :user_id AND amount > 0", user_id = session['user_id'])
    cashonhand = db.execute("SELECT cash FROM users where id = :user_id", user_id = session['user_id'])[0]['cash']
    cashonhand = round(cashonhand, 2)
    actualcashonhand = cashonhand

    for i in range(len(positions)):
        quote = lookup(positions[i]['symbol'])
        positions[i]['compname'] = quote['name']
        positions[i]['currprice'] = quote['price']
        positions[i]['totalcost'] = round(float(quote['price']) * float(positions[i]['amount']), 2)

    for i in range(len(positions)):
        cashonhand += positions[i]['totalcost']

    return render_template("index.html", positions = positions, cashonhand = cashonhand, actualcashonhand = actualcashonhand)


@app.route("/buy", methods=["GET", "POST"])
@login_required
def buy():
    """Buy shares of stock"""
    if request.method == "GET":
        return render_template("buy.html")
    else:
        symbol = request.form.get("symbol")
        shares = int(request.form.get("amount"))

        if not ((shares and symbol) or shares < 1):
            return apology("INVALID SHARES")

        quote = lookup(symbol)

        if quote:
            print("smile")
        else:
            return apology("INVALID SYMBOL")

        priceofone = quote["price"]
        price = quote["price"] * int(shares)
        cashonhand = db.execute("SELECT cash FROM users where id = :user_id", user_id = session['user_id'])[0]['cash']

        if cashonhand < price:
            return apology("NEED MORE CASH")
        else:
            owns = db.execute("SELECT * FROM userportfolio WHERE user_id = :user_id AND amount > 0 AND symbol = :symbol", user_id = session['user_id'], symbol = symbol)
            if owns:
                #If owns stock, add shares
                db.execute("UPDATE userportfolio SET amount = amount + :shares WHERE symbol = :symbol AND user_id = :user_id", user_id = session['user_id'], symbol = symbol, shares = shares)
            else:
                #If new purchase, insert new transaction
                db.execute("INSERT INTO userportfolio (user_id, symbol, amount) VALUES(:user_id, :symbol, :amount)", user_id = session['user_id'], symbol = symbol, amount = shares)

            #Log transaction
            date = datetime.datetime.now()
            db.execute("INSERT INTO transactions (user_id, symbol, price, amount, time) VALUES (:user_id, :symbol, :price, :amount, :time)",
            user_id = session['user_id'], symbol = symbol, price = priceofone, amount = shares, time = date)

            #Charge the User
            chargedprice = -price
            db.execute("UPDATE users SET cash = cash + :newBalance WHERE id = :user_id", user_id = session['user_id'], newBalance = chargedprice)
            return redirect("/")
        return apology("DEBUG")


@app.route("/history")
@login_required
def history():
    """Show history of transactions"""
    positions = db.execute("SELECT * FROM transactions WHERE user_id = :user_id", user_id = session['user_id'])

    for i in range(len(positions)):
        positions[i]['totalcost'] = round(-1 * float(positions[i]['price']) * float(positions[i]['amount']), 2)

    return render_template("history.html", positions = positions)


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = :username",
                          username=request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


@app.route("/quote", methods=["GET", "POST"])
@login_required
def quote():
    """Get stock quote."""
    if request.method == "GET":
        return render_template("quote.html")
    else:
        symbol = request.form.get("symbol")
        price = lookup(symbol)
        return render_template("quote.html", price = price["price"])


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    if request.method == "GET":
        return render_template("register.html")
    else:
        username = request.form.get("username")
        password = request.form.get("password")
        confirmationpass = request.form.get("confirmation")

        if username == "":
            return apology ("USERNAME FIELD CANNOT BE BLANK")

        if confirmationpass != password:
            return apology ("PASSWORDS DO NOT MATCH")

        if username in db.execute("SELECT username FROM users WHERE username = ?", username):
            return apology ("USERNAME ALREADY TAKEN")

        register = db.execute("INSERT INTO users (username, hash) VALUES(?, ?)", username, generate_password_hash(password))
        return redirect("/login")



@app.route("/sell", methods=["GET", "POST"])
@login_required
def sell():
    """Sell shares of stock"""
    if request.method == "GET":
        return render_template("sell.html")
    else:
        symbol = request.form.get("symbol")
        shares = int(request.form.get("amount"))

        if not ((shares and symbol) or shares < 1):
            return apology("INVALID SHARES")

        quote = lookup(symbol)

        if quote:
            print("smile")
        else:
            return apology("INVALID SYMBOL")

        priceofone = quote["price"]
        price = quote["price"] * int(shares)
        cashonhand = db.execute("SELECT cash FROM users where id = :user_id", user_id = session['user_id'])[0]['cash']

        owns = db.execute("SELECT * FROM userportfolio WHERE user_id = :user_id AND amount > 0 AND symbol = :symbol", user_id = session['user_id'], symbol = symbol)

        if owns:
            #If owns stock, sell shares
            db.execute("UPDATE userportfolio SET amount = amount - :shares WHERE symbol = :symbol AND user_id = :user_id", user_id = session['user_id'], symbol = symbol, shares = shares)
        else:
            return apology("DO NOT OWN")

        #Log transaction
        date = datetime.datetime.now()
        db.execute("INSERT INTO transactions (user_id, symbol, price, amount, time) VALUES (:user_id, :symbol, :price, :amount, :time)",
        user_id = session['user_id'], symbol = symbol, price = priceofone, amount = -shares, time = date)

        #Charge the User
        chargedprice = price
        db.execute("UPDATE users SET cash = cash + :newBalance WHERE id = :user_id", user_id = session['user_id'], newBalance = chargedprice)
        return redirect("/")

    return apology("DEBUG")


def errorhandler(e):
    """Handle error"""
    if not isinstance(e, HTTPException):
        e = InternalServerError()
    return apology(e.name, e.code)


# Listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)
