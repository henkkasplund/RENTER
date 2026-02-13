import sqlite3
from flask import Flask
from flask import abort, redirect, render_template, request, session
from flask import flash
import db
import config
import listings
import users
import re

app = Flask(__name__)
app.secret_key = config.secret_key

def demand_login():
    if "user_id" not in session:
        abort(403)

@app.route("/")
def index():
    all_listings = listings.get_listings()
    return render_template("index.html", listings=all_listings)

@app.route("/listing/<int:listing_id>")
def show_listing(listing_id):
    listing = listings.get_listing(listing_id)
    if not listing:
        abort(404)
    return render_template("show_listing.html", listing=listing)

@app.route("/user/<int:user_id>")
def user(user_id):
    user = users.get_user(user_id)
    user_listings = users.get_user_listings(user_id)
    if not user:
        abort(403)
    return render_template("user.html", user=user, listings=user_listings)

@app.route("/search_listings")
def search_listings():
    query = request.args.get("query")
    if not query:
        query = ""
    results = listings.search_listings(query) if query else []
    return render_template("search_listings.html", query=query, results=results)

@app.route("/new_listing")
def new_listing():
    demand_login()
    municipalities = listings.get_municipalities()
    return render_template("new_listing.html", municipalities=municipalities)

@app.route("/create_listing", methods=["POST"])
def create_listing():
    demand_login()
    user_id = session["user_id"]
    listing_data = listings.get_form_data()
    listings.add_listing(user_id, listing_data)
    return redirect("/")

@app.route("/edit_listing/<int:listing_id>", methods=["GET", "POST"])
def edit_listing(listing_id):
    demand_login()
    listing = listings.get_listing(listing_id)
    municipalities = listings.get_municipalities()
    if not listing:
        abort(404)
    if listing["user_id"] != session["user_id"]:
        abort(403)
    if request.method == "GET":
        return render_template("edit_listing.html", listing=listing, municipalities=municipalities)
    listing_data = listings.get_form_data()
    listings.update_listing(listing_id, listing_data)
    return redirect("/listing/" + str(listing_id))

@app.route("/remove_listing/<int:listing_id>", methods=["GET", "POST"])
def remove_listing(listing_id):
    demand_login()
    listing = listings.get_listing(listing_id)
    if not listing:
        abort(404)
    if listing["user_id"] != session["user_id"]:
        abort(403)
    if request.method == "GET":
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
    if not username or not password1:
        return "VIRHE: tyhjä käyttäjänimi tai salasana<br><a href='/register'>Takaisin</a>"
    if password1 != password2:
        return "VIRHE: salasanat eivät ole samat<br><a href='/register'>Takaisin</a>"
    try:
        users.create_user(username, password1)
    except sqlite3.IntegrityError:
        return "VIRHE: tunnus on jo varattu<br><a href='/register'>Takaisin</a>"

    sql = "SELECT id FROM users WHERE username = ?"
    user_id = db.query(sql, [username])[0]["id"]
    session["user_id"] = user_id
    session["username"] = username
    flash("Tunnus luotu!")
    return redirect("/")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        username = request.args.get("username", "")
        return render_template("login.html", username=username)
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        user_id = users.check_login(username, password)
        if user_id:
            session["user_id"] = user_id
            session["username"] = username
            return redirect("/")
        else:
            return f"VIRHE: väärä tunnus tai salasana<br><a href='/login?username={username}'>Takaisin</a>"

@app.route("/logout")
def logout():
    if "user_id" in session:
        del session["user_id"]
        del session["username"]
    return redirect("/")