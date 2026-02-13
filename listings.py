import db
from flask import abort, request
import re

def add_listing(user_id, listing_data):
    sql = """INSERT INTO listings (user_id, rooms, size, rent, municipality,
                                address, postcode,floor, floors, sauna, balcony,
                                bath, elevator, laundry, cellar, pool, description)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"""

    db.execute(sql, [user_id, listing_data["rooms"], listing_data["size"], listing_data["rent"],
                     listing_data["municipality"], listing_data["address"], listing_data["postcode"],
                     listing_data["floor"], listing_data["floors"], listing_data["sauna"],
                     listing_data["balcony"], listing_data["bath"], listing_data["elevator"],
                     listing_data["laundry"], listing_data["cellar"], listing_data["pool"],
                     listing_data["description"]])

def get_listings():
    sql = "SELECT id, municipality, rooms, rent, size FROM listings ORDER BY id DESC"
    return db.query(sql)

def get_listing(listing_id): # User rating coming!
    sql = """SELECT listings.id,
                    listings.rooms,
                    listings.size,
                    listings.rent,
                    listings.municipality,
                    listings.address,
                    listings.postcode,
                    listings.floor,
                    listings.floors,
                    listings.sauna,
                    listings.balcony,
                    listings.bath,
                    listings.elevator,
                    listings.laundry,
                    listings.cellar,
                    listings.pool,
                    listings.description,
                    users.id user_id,
                    users.username
             FROM listings, users
             WHERE listings.user_id = users.id AND
                    listings.id = ?"""
    result = db.query(sql, [listing_id])
    return result[0] if result else None

def get_form_data():
    rooms = request.form["rooms"]
    if not re.search("^[1-9][0-9]?$", rooms):
        abort(403)
    size = request.form["size"]
    if not size or len(size) > 20:
        abort(403)
    if not re.search("^[1-9][0-9]{0,3}(,5)?$", size):
        abort(403)
    size = size.replace(",", ".")
    rent = request.form["rent"]
    if not rent or len(rent) > 20:
        abort(403)
    if not re.search("^[1-9][0-9]{0,4}$", rent):
        abort(403)
    municipality = request.form["municipality"]
    if not municipality or len(municipality) > 30:
        abort(403)
    address = request.form["address"]
    if not address or len(address) > 50:
        abort(403)
    postcode = request.form["postcode"]
    if not postcode or len(postcode) > 5:
        abort(403)
    if not re.search("^[0-9]{5}$", postcode):
        abort(403)
    floor = request.form["floor"]
    if not floor or len(floor) > 10:
        abort(403)
    if not re.search("^(-1|[0-9]{1,2})$", floor):
        abort(403)
    floors = request.form["floors"]
    if not floors or len(floors) > 10:
        abort(403)
    if not re.search("^[1-9][0-9]?$", floors):
        abort(403)
    sauna = 1 if "sauna" in request.form else 0
    balcony = 1 if "balcony" in request.form else 0
    bath = 1 if "bath" in request.form else 0
    elevator = 1 if "elevator" in request.form else 0
    laundry = 1 if "laundry" in request.form else 0
    cellar = 1 if "cellar" in request.form else 0
    pool = 1 if "pool" in request.form else 0
    description = request.form["description"]
    if len(description) > 300:
        abort(403)
    return {
        "rooms": rooms,
        "size": size,
        "rent": rent,
        "municipality": municipality,
        "address": address,
        "postcode": postcode,
        "floor": floor,
        "floors": floors,
        "sauna": sauna,
        "balcony": balcony,
        "bath": bath,
        "elevator": elevator,
        "laundry": laundry,
        "cellar": cellar,
        "pool": pool,
        "description": description
    }

def update_listing(listing_id, listing_data):
    sql = """UPDATE listings SET rooms = ?, size = ?, rent = ?,
                    municipality = ?, address = ?, postcode = ?,
                    floor = ?, floors = ?, sauna = ?, balcony = ?,
                    bath = ?, elevator = ?, laundry = ?, cellar = ?,
                    pool = ?, description = ?
            WHERE id = ?"""
    db.execute(sql, [listing_data["rooms"], listing_data["size"], listing_data["rent"],
                     listing_data["municipality"], listing_data["address"], listing_data["postcode"],
                     listing_data["floor"], listing_data["floors"], listing_data["sauna"],
                     listing_data["balcony"], listing_data["bath"], listing_data["elevator"],
                     listing_data["laundry"], listing_data["cellar"], listing_data["pool"],
                     listing_data["description"], listing_id])

def remove_listing(listing_id):
    sql = "DELETE FROM listings WHERE id = ?"
    db.execute(sql, [listing_id])

def search_listings(query):
    sql = """SELECT listings.id,
                    listings.rooms,
                    listings.municipality,
                    listings.rent,
                    listings.size,
                    users.username,
                    users.id AS user_id
            FROM listings
            JOIN users ON listings.user_id = users.id
            WHERE listings.municipality LIKE ? OR listings.description LIKE ?
            ORDER BY listings.id DESC"""
    result = "%" + query + "%"
    return db.query(sql, [result, result])

def get_municipalities():
    sql = "SELECT name FROM municipalities ORDER BY name"
    return db.query(sql)