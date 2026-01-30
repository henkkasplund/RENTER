import sqlite3
from flask import Flask
from flask import redirect, render_template, request, session
from werkzeug.security import check_password_hash, generate_password_hash
import db
import config
import listings

app = Flask(__name__)
app.secret_key = config.secret_key

@app.route("/")
def index():
    all_listings = listings.get_listings()
    return render_template("index.html", listings=all_listings)

@app.route("/listing/<int:listing_id>")
def show_listing(listing_id):
    listing = listings.get_listing(listing_id)
    return render_template("show_listing.html", listing=listing)

@app.route("/search_listings")
def search_listings():
    query = request.args.get("query")
    if not query:
        query = ""
    results = listings.search_listings(query) if query else []
    return render_template("search_listings.html", query=query, results=results)

@app.route("/new_listing")
def new_listing():
    return render_template("new_listing.html")

@app.route("/create_listing", methods=["POST"])
def create_listing():
    title = request.form["title"]
    description = request.form["description"]
    price = request.form["price"]
    user_id = session["user_id"]
    
    listings.add_listing(title, description, price, user_id)

    return redirect("/")

@app.route("/edit_listing/<int:listing_id>", methods=["GET", "POST"])
def edit_listing(listing_id):
    if request.method == "GET":
        listing = listings.get_listing(listing_id)
        return render_template("/edit_listing.html", listing=listing)

    if request.method == "POST":
        if "edit" in request.form:
            listing_id = request.form["listing_id"]
            title = request.form["title"]
            description = request.form["description"]
            price = request.form["price"]

            listings.update_listing(listing_id, title, description, price)
            return redirect("/listing/" + str(listing_id))

@app.route("/remove_listing/<int:listing_id>", methods=["GET", "POST"])
def remove_listing(listing_id):
    if request.method == "GET":
        listing = listings.get_listing(listing_id)
        return render_template("remove_listing.html", listing=listing)

    if request.method == "POST":
        if "remove" in request.form:
            listings.remove_listing(listing_id)
            return redirect("/")
        else:
            return redirect("/listing/" + str(listing_id))

@app.route("/register")
def register():
    return render_template("register.html")

@app.route("/create_account", methods=["POST"])
def create():
    username = request.form["username"]
    password1 = request.form["password1"]
    password2 = request.form["password2"]
    if password1 != password2:
        return "VIRHE: salasanat eivät ole samat<br><a href='/register'>Takaisin</a>"
    password_hash = generate_password_hash(password1)

    try:
        sql = "INSERT INTO users (username, password_hash) VALUES (?, ?)"
        db.execute(sql, [username, password_hash])
    except sqlite3.IntegrityError:
        return "VIRHE: tunnus on jo varattu<br><a href='/register'>Takaisin</a>"

    return "Tunnus luotu"

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        username = request.args.get("username", "")
        return render_template("login.html", username=username)

    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        sql = "SELECT id, password_hash FROM users WHERE username = ?"
        matching_username = db.query(sql, [username])
        if not matching_username:
            return "VIRHE: väärä tunnus<br><a href='/login'>Takaisin</a>"
        result = matching_username[0]

        user_id = result["id"]
        password_hash = result["password_hash"]

        if check_password_hash(password_hash, password):
            session["user_id"] = user_id
            session["username"] = username
            return redirect("/")
        else:                                                                                    # jos tunnus on oikein mutta salasana väärin
            return f"VIRHE: väärä salasana<br><a href='/login?username={username}'>Takaisin</a>" # täyttää kenttään valmiiksi jo syötetyn tunnuksen

@app.route("/logout")
def logout():
    del session["user_id"]
    del session["username"]
    return redirect("/")