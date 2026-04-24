import sqlite3
from flask import Flask
from flask import abort, redirect, render_template, make_response, request, session
from flask import flash
import db
import config
import listings
import users
import offers
import ratings
import markupsafe
import secrets
from datetime import datetime
import math
import time
from flask import g

app = Flask(__name__)
app.secret_key = config.secret_key


def guarantee_csrf():
    if "csrf_token" not in session:
        session["csrf_token"] = secrets.token_hex(16)

def check_csrf():
    if request.form["csrf_token"] != session["csrf_token"]:
        abort(403)

@app.before_request
def last_visited():
    if request.method == "GET" \
        and not request.path.startswith("/image") \
        and not request.path.startswith("/static") \
        and not request.path.startswith("/.well-known"):
        session["last_visited"] = session.get("visited")
        session["visited"] = request.url

@app.template_filter()
def show_lines(content):
    content = str(markupsafe.escape(content))
    content = content.replace("\n", "<br />")
    return markupsafe.Markup(content)

@app.template_filter()
def format_size(value):
    value = float(value)
    if value.is_integer():
        return int(value)
    return str(value).replace(".", ",")

@app.template_filter()
def get_timespan(value):
    dt = datetime.fromisoformat(value)
    now = datetime.now()
    diff = (now - dt).days
    if diff == 0:
        return "Tänään"
    elif diff == 1:
        return "Eilen"
    elif diff < 7:
        return f"{diff} pv sitten"
    elif diff < 30:
        return f"{diff // 7} vk sitten"
    elif diff < 365:
        return f"{diff // 30} kk sitten"
    else:
        return f"{diff // 365} v sitten"

@app.template_filter()
def get_date(value):
    dt = datetime.fromisoformat(value)
    return dt.strftime("%-d.%-m.%Y")

def demand_login():
    if "user_id" not in session:
        abort(403)

@app.route("/")
@app.route("/<int:page>")
def index(page=1):
    page_size = 20
    count = listings.listing_count()
    page_count = max(math.ceil(count / page_size), 1)
    if page < 1:
        return redirect("/1")
    if page > page_count:
        return redirect("/" + str(page_count))
    all_listings = listings.get_listings(page, page_size)
    return render_template("index.html", listings=all_listings,
                           page=page, page_count=page_count)

@app.route("/user/<int:user_id>", methods=["GET", "POST"])
def user(user_id):
    demand_login()
    user = users.get_user(user_id)
    user_listings = users.get_user_listings(user_id)
    liked = users.get_liked(user_id)
    sent_offers = offers.get_sent_offers(user_id)
    withdrawn_sent_offers = sum(1 for offer in sent_offers if offer['status'] == "withdrawn")
    active_sent_offers = len(sent_offers) - withdrawn_sent_offers
    received_offers = offers.get_received_offers(user_id)
    inactive_received_offers = sum(1 for offer in received_offers if offer['status'] in ("withdrawn", "rejected"))
    active_received_offers = len(received_offers) - inactive_received_offers
    edit_contact = request.args.get("edit_contact") == "1"
    edit_rating = request.args.get("edit_rating") == "1"
    viewer_id = session["user_id"]
    rental_deal = offers.confirmed_deal(viewer_id, user_id)
    user_rating = ratings.get_rating(session["user_id"], user_id) if rental_deal else None
    view = request.args.get("view", "listings")
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
        return redirect("/user/" + str(user_id) + "?view=profile")
    return render_template("user.html",
                            user=user, listings=user_listings, liked=liked,
                            sent_offers=sent_offers, received_offers=received_offers,
                            edit_contact=edit_contact, edit_rating=edit_rating,
                            rental_deal=rental_deal, user_rating=user_rating, view=view,
                            withdrawn_sent_offers=withdrawn_sent_offers,
                            active_sent_offers=active_sent_offers,
                            inactive_received_offers=inactive_received_offers,
                            active_received_offers=active_received_offers)

@app.route("/register")
def register():
    guarantee_csrf()
    return render_template("register.html")

@app.route("/create_account", methods=["POST"])
def create_account():
    check_csrf()
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
    session.clear()
    session["user_id"] = user["id"]
    session["username"] = username
    session["csrf_token"] = secrets.token_hex(16)
    flash("Tunnus luotu!")
    return redirect("/")

@app.route("/delete_account", methods=["GET", "POST"])
def delete_account():
    demand_login()
    user_id = session["user_id"]
    user = users.get_user(user_id)
    if not user:
        abort(404)
    if request.method == "GET":
        return render_template("delete_account.html", user=user)
    if request.method == "POST":
        check_csrf()
        if "delete" in request.form:
            users.delete_user(user_id)
            del session["user_id"]
            del session["username"]
            del session["csrf_token"]
            flash("Käyttäjätili poistettu!")
            return redirect("/")
        else:
            return redirect("/user/" + str(user_id))

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        guarantee_csrf()
        username = request.args.get("username", "")
        return render_template("login.html", username=username)
    if request.method == "POST":
        check_csrf()
        username = request.form["username"]
        password = request.form["password"]
        user = users.check_login(username, password)
        if user:
            session.clear()
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
    del session["csrf_token"]
    return redirect("/")

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
    demand_login()
    check_csrf()
    user_id = session["user_id"]
    listing_data = listings.get_listings_data()
    listings.add_listing(user_id, listing_data)
    return redirect("/")

@app.route("/search_listings")
def search_listings():
    rating = request.args.get("rating", "")
    size = request.args.get("size", "")
    max_rent = request.args.get("max_rent", "")
    min_rent = request.args.get("min_rent", "")
    rooms_id = request.args.get("rooms_id", "" )
    property_type_id = request.args.get("property_type_id", "")
    municipality_id = request.args.get("municipality_id", "")
    condition_id = request.args.get("condition_id", "")
    edit_search = request.args.get("edit_search") == "1"
    searched = bool(request.args)
    page = int(request.args.get("page", 1))
    page_size = 20
    results, count = listings.search_listings(rating, size, min_rent, max_rent,
                                       rooms_id, property_type_id, municipality_id,
                                       condition_id, page, page_size)
    page_count = max(math.ceil(count / page_size), 1)
    return render_template("search_listings.html",
                           size=size, max_rent=max_rent, min_rent=min_rent,
                           rooms_id=rooms_id, property_type_id=property_type_id,
                           municipality_id=municipality_id, condition_id=condition_id,
                           searched = searched, results=results, rating=rating,
                           edit_search=edit_search, rooms=listings.get_classes("rooms"),
                           municipalities=listings.get_classes("municipality"),
                           property_types=listings.get_classes("property_type"),
                           conditions=listings.get_classes("condition"),
                           page=page, page_count=page_count)

@app.route("/listing/<int:listing_id>")
def show_listing(listing_id):
    listing = listings.get_listing(listing_id)
    if not listing:
        abort(404)
    viewer_id = session.get("user_id")
    likes = listings.get_likes(viewer_id, listing_id)
    images = listings.get_images(listing_id)
    listing_offers = offers.get_offers(listing_id, viewer_id, listing["user_id"])
    pending_offers = sum(1 for offer in listing_offers if offer['status'] == "pending")
    accepted_offers = sum(1 for offer in listing_offers if offer['status'] == "accepted")
    offer_history = {offer["id"]: offers.get_offer_history(offer["id"]) for offer in listing_offers}
    user_offer = None
    if viewer_id and viewer_id != listing["user_id"] and listing_offers:
        user_offer = listing_offers[0]
    rented = offers.rental_status(listing_id)
    edit_offer = request.args.get("edit_offer") == "1"
    view = request.args.get("view", "listing")
    max_rejected = offers.get_max_rejected(user_offer["id"]) if user_offer else 0
    return render_template("show_listing.html", listing=listing, likes=likes, images=images,
                                                offers=listing_offers, user_offer=user_offer,
                                                rented=rented, edit_offer=edit_offer, view=view,
                                                offer_history=offer_history, pending_offers=pending_offers,
                                                accepted_offers=accepted_offers, max_rejected=max_rejected)

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
        if "update" in request.form:
            listing_data = listings.get_listings_data()
            listings.update_listing(listing_id, listing_data)
            return redirect("/listing/" + str(listing_id))
        else:
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

@app.route("/add_images", methods=["POST"])
def add_images():
    demand_login()
    check_csrf()
    listing_id = request.form["listing_id"]
    listing = listings.get_listing(listing_id)
    if not listing:
        abort(404)
    if listing["user_id"] != session["user_id"]:
        abort(403)
    files = request.files.getlist("images")
    images_added = 0
    for file in files:
        if not file.filename:
            continue
        mimetype = file.mimetype
        if mimetype not in ["image/jpeg", "image/png"]:
            return "VIRHE: väärä tiedostomuoto"
        image = file.read()
        if len(image) > 100 * 1024:
            return "VIRHE: liian suuri kuva"
        listings.add_images(listing_id, image, mimetype)
        images_added += 1
    if images_added > 1:
        flash("Kuvat lisätty!")
    elif images_added == 1:
        flash("Kuva lisätty!")
    return redirect("/images/" + str(listing_id))

@app.route("/remove_images", methods=["POST"])
def remove_images():
    demand_login()
    check_csrf()
    listing_id = request.form["listing_id"]
    listing = listings.get_listing(listing_id)
    if not listing:
        abort(404)
    if listing["user_id"] != session["user_id"]:
        abort(403)
    images = request.form.getlist("image_id")
    for image_id in images:
        listings.remove_image(listing_id, image_id)
    if len(images) > 1:
        flash("Kuvat poistettu!")
    elif len(images) == 1:
        flash("Kuva poistettu!")
    return redirect("/images/" + str(listing_id))

@app.route("/image/<int:image_id>")
def show_image(image_id):
    image = listings.get_image(image_id)
    if not image:
        abort(404)
    response = make_response(image["image"])
    response.headers.set("Content-Type", image["mimetype"])
    return response

@app.route("/images/<int:listing_id>")
def edit_images(listing_id):
    demand_login()
    listing = listings.get_listing(listing_id)
    if not listing:
        abort(404)
    if listing["user_id"] != session["user_id"]:
        abort(403)
    images = listings.get_images(listing_id)
    add_images = request.args.get("add_images") == "1"
    return render_template("images.html", listing=listing, images=images, add_images=add_images)

@app.route("/toggle_like/<int:listing_id>", methods=["POST"])
def toggle_like(listing_id):
    demand_login()
    check_csrf()
    user_id = session["user_id"]
    listing = listings.get_listing(listing_id)
    if not listing:
        abort(404)
    if listing["user_id"] == user_id:
        abort(403)
    likes = listings.get_likes(user_id, listing_id)
    if likes["liked"]:
        listings.like_unlike(user_id, listing_id, False)
    else:
        listings.like_unlike(user_id, listing_id, True)
    return redirect(session.get("last_visited") or "/")

@app.route("/create_offer", methods=["POST"])
def create_offer():
    demand_login()
    check_csrf()
    if "back" in request.form:
        listing_id = request.form["listing_id"]
        return redirect("/listing/" + str(listing_id))
    offer_data = offers.get_offer_data()
    listing = listings.get_listing(offer_data["listing_id"])
    if not listing:
        abort(404)
    user_id = session["user_id"]
    if listing["user_id"] == user_id:
        abort(403)
    offers.add_offer(offer_data["listing_id"], user_id, offer_data["price"])
    return redirect("/listing/" + str(offer_data["listing_id"]))

@app.route("/offer/<int:offer_id>")
def show_offer(offer_id):
    demand_login()
    offer = offers.get_offer(offer_id)
    if not offer:
        abort(404)
    listing = listings.get_listing(offer["listing_id"])
    if not listing:
        abort(404)
    if session["user_id"] not in (offer["user_id"], listing["user_id"]):
        abort(403)
    history = offers.get_offer_history(offer_id)
    likes = listings.get_likes(session.get("user_id"), offer["listing_id"])
    edit_offer = request.args.get("edit_offer") == "1"
    max_rejected = offers.get_max_rejected(offer["id"])
    return render_template("show_offer.html",
                           offer=offer, listing=listing, history=history,
                           likes=likes, edit_offer=edit_offer, max_rejected=max_rejected)

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
    return redirect(session.get("last_visited") or "/listing/" + str(offer["listing_id"]))

@app.route("/edit_offer/<int:offer_id>", methods=["POST"])
def edit_offer(offer_id):
    demand_login()
    check_csrf()
    action = request.form["action"]
    user_id = session["user_id"]
    offer = offers.get_offer(offer_id)
    if not offer:
        abort(404)
    if offer["user_id"] != user_id:
        abort(403)
    if action == "update":
        price = request.form["price"]
        offers.modify_offer(offer_id, user_id, action, price)
        flash("Hakemus päivitetty!")
        return redirect("/offer/" + str(offer_id))
    elif action == "delete":
        offers.modify_offer(offer_id, user_id, action)
        flash("Hakemus poistettu!")
    else:
        abort(403)
    return redirect(session.get("last_visited") or "/listing/" + str(offer["listing_id"]))

@app.route("/confirm_offer/<int:offer_id>", methods=["POST"])
def confirm_offer(offer_id):
    demand_login()
    check_csrf()
    user_id = session["user_id"]
    offer = offers.get_offer(offer_id)
    if not offer:
        abort(404)
    if offer["user_id"] != user_id:
        abort(403)
    if offer["status"] != "accepted":
        abort(403)
    offers.confirm_rental(offer_id)
    flash("Vuokraus vahvistettu!")
    return redirect("/listing/" + str(offer["listing_id"]))

@app.route("/rate_user/<int:user_id>", methods=["POST"])
def rate_user(user_id):
    demand_login()
    check_csrf()
    rater_id = session["user_id"]
    rating_value = request.form["rating"]
    ratings.set_rating(rater_id, user_id, rating_value)
    users.update_rating(user_id)
    flash("Arvosana annettu")
    return redirect("/user/" + str(user_id))

@app.before_request
def before_request():
    g.start_time = time.time()

@app.after_request
def after_request(response):
    elapsed_time = round(time.time() - g.start_time, 2)
    print("elapsed time:", elapsed_time, "s")
    return response