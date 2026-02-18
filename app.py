import sqlite3
from flask import Flask
from flask import abort, redirect, render_template, request, session
from flask import flash
import db
import config
import listings
import users
import offers
import markupsafe
import secrets

app = Flask(__name__)
app.secret_key = config.secret_key


def check_csrf():
    if request.form["csrf_token"] != session["csrf_token"]:
        abort(403)

@app.template_filter()
def show_lines(content):
    content = str(markupsafe.escape(content))
    content = content.replace("\n", "<br />")
    return markupsafe.Markup(content)

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
    viewer_id = session.get("user_id")
    likes = listings.get_likes(viewer_id, listing_id)
    listing_offers = offers.get_offers(listing_id, viewer_id, listing["user_id"])
    user_offer = listing_offers[0] if listing_offers else None
    rented = offers.rental_status(listing_id)
    return render_template("show_listing.html", listing=listing, likes=likes, offers=listing_offers,
                                                user_offer=user_offer, rented=rented)

@app.route("/user/<int:user_id>", methods=["GET", "POST"])
def user(user_id):
    demand_login()
    user = users.get_user(user_id)
    user_listings = users.get_user_listings(user_id)
    liked = users.get_liked(user_id)
    deals = users.get_deals(user_id)
    if not user:
        abort(403)
    if request.method == "POST":
        demand_login()
        check_csrf()
        if session["user_id"] != user_id:
            abort(403)
        phone = request.form["phone"]
        email = request.form["email"]
        users.update_contact(user_id, phone, email)
        flash("Yhteystiedot päivitetty!")
        return redirect("/user/" + str(user_id))
    return render_template("user.html", user=user, listings=user_listings, liked=liked, deals=deals)

@app.route("/search_listings")
def search_listings():
    user = request.args.get("user", "")
    size = request.args.get("size", "")
    max_rent = request.args.get("max_rent", "")
    min_rent = request.args.get("min_rent", "")
    rooms_id = request.args.get("rooms_id", "" )
    property_type_id = request.args.get("property_type_id", "")
    municipality_id = request.args.get("municipality_id", "")
    condition_id = request.args.get("condition_id", "")
    searched = bool(request.args)
    results = listings.search_listings(user, size, min_rent, max_rent, rooms_id,
                                       property_type_id, municipality_id, condition_id)
    return render_template("search_listings.html",
                           user=user, size=size, max_rent=max_rent, min_rent=min_rent,
                           rooms_id=rooms_id, property_type_id=property_type_id,
                           municipality_id=municipality_id, condition_id=condition_id,
                           searched = searched, results=results,
                           rooms=listings.get_classes("rooms"),
                           municipalities=listings.get_classes("municipality"),
                           property_types=listings.get_classes("property_type"),
                           conditions=listings.get_classes("condition"))

@app.route("/new_listing")
def new_listing():
    demand_login()
    municipalities = listings.get_classes("municipality")
    conditions = listings.get_classes("condition")
    property_types = listings.get_classes("property_type")
    rooms = listings.get_classes("rooms")
    return render_template("new_listing.html",
                           municipalities=municipalities, conditions=conditions,
                           property_types=property_types, rooms=rooms)

@app.route("/create_listing", methods=["POST"])
def create_listing():
    print("SESSION:", dict(session))
    print("FORM:", dict(request.form))

    demand_login()
    check_csrf()
    user_id = session["user_id"]
    listing_data = listings.get_listings_data()
    listings.add_listing(user_id, listing_data)
    return redirect("/")

@app.route("/edit_listing/<int:listing_id>", methods=["GET", "POST"])
def edit_listing(listing_id):
    demand_login()
    listing = listings.get_listing(listing_id)
    if not listing:
        abort(404)
    if listing["user_id"] != session["user_id"]:
        abort(403)
    municipalities = listings.get_classes("municipality")
    rooms = listings.get_classes("rooms")
    conditions = listings.get_classes("condition")
    property_types = listings.get_classes("property_type")
    if request.method == "GET":
        return render_template("edit_listing.html",
                               listing=listing, municipalities=municipalities, rooms = rooms,
                               conditions=conditions, property_types=property_types)
    if request.method == "POST":
        check_csrf()
        listing_data = listings.get_listings_data()
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
        check_csrf()
        if "remove" in request.form:
            listings.remove_listing(listing_id)
            return redirect("/")
        else:
            return redirect("/listing/" + str(listing_id))

@app.route("/register")
def register():
    return render_template("register.html")

@app.route("/create_account", methods=["POST"])
def create_account():
    username = request.form["username"]
    password1 = request.form["password1"]
    password2 = request.form["password2"]
    if not username or not password1:
        flash("VIRHE: tyhjä käyttäjänimi tai salasana")
        return render_template("register.html", username=username)
    if password1 != password2:
        flash("VIRHE: salasanat eivät ole samat")
        return render_template("register.html", username=username)
    try:
        users.create_user(username, password1)
    except sqlite3.IntegrityError:
        flash("VIRHE: tunnus on jo varattu")
        return render_template("register.html")

    sql = "SELECT id, rating FROM users WHERE username = ?"
    user = db.query(sql, [username])[0]
    session["user_id"] = user["id"]
    session["username"] = username
    session["rating"] = user["rating"]
    session["csrf_token"] = secrets.token_hex(16)
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
        user = users.check_login(username, password)
        if user:
            session["user_id"] = user["id"]
            session["username"] = username
            session["rating"] = user["rating"]
            session["csrf_token"] = secrets.token_hex(16)
            return redirect("/")
        else:
            flash("VIRHE: väärä tunnus tai salasana")
            return render_template("login.html", username=username)

@app.route("/logout", methods=["POST"])
def logout():
    demand_login()
    check_csrf()
    del session["user_id"]
    del session["username"]
    del session["rating"]
    del session["csrf_token"]
    return redirect("/")

@app.route("/toggle_like/<int:listing_id>", methods=["POST"])
def toggle_like(listing_id):
    demand_login()
    check_csrf()
    user_id = session["user_id"]
    likes = listings.get_likes(user_id, listing_id)
    if likes["liked"]:
        listings.like_unlike(user_id, listing_id, False)
    else:
        listings.like_unlike(user_id, listing_id, True)
    return redirect(request.referrer)

@app.route("/create_offer", methods=["POST"])
def create_offer():
    demand_login()
    check_csrf()
    offer_data = offers.get_offer_data()
    listing = listings.get_listing(offer_data["listing_id"])
    if not listing:
        abort(404)
    user_id = session["user_id"]
    offers.add_offer(offer_data["listing_id"], user_id, offer_data["price"])
    return redirect("/listing/" + str(offer_data["listing_id"]))

@app.route("/handle_offer/<int:offer_id>", methods=["POST"])
def handle_offer(offer_id):
    demand_login()
    check_csrf()
    decision = request.form["decision"]
    user_id = session["user_id"]
    offer = offers.get_offer(offer_id)
    if not offer:
        abort(404)
    listing = listings.get_listing(offer["listing_id"])
    if not listing:
        abort(404)
    if listing["user_id"] != user_id:
        abort(403)
    offers.handle_offer(offer_id, decision)
    return redirect("/listing/" + str(offer["listing_id"]))

@app.route("/edit_offer/<int:offer_id>", methods=["POST"])
def edit_offer(offer_id):
    demand_login()
    check_csrf()
    action = request.form["action"]
    user_id = session["user_id"]
    offer = offers.get_offer(offer_id)
    if not offer:
        abort(404)
    if action == "update":
        price = request.form["price"]
        offers.modify_offer(offer_id, user_id, action, price)
    elif action == "delete":
        offers.modify_offer(offer_id, user_id, action)
    else:
        abort(403)
    return redirect("/listing/" + str(offer["listing_id"]))