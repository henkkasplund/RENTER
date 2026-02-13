import db
from flask import abort, request
import re

def add_listing(user_id, listing_data):
    sql = """INSERT INTO listings (user_id, rooms, size, rent,
                                address, postcode,floor, floors, sauna, balcony,
                                bath, elevator, laundry, cellar, pool, description,
                                municipality_id, condition_id, property_type_id)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"""

    db.execute(sql, [user_id, listing_data["rooms"], listing_data["size"],
                     listing_data["rent"], listing_data["address"],
                     listing_data["postcode"],listing_data["floor"],
                     listing_data["floors"], listing_data["sauna"],
                     listing_data["balcony"], listing_data["bath"],
                     listing_data["elevator"], listing_data["laundry"],
                     listing_data["cellar"], listing_data["pool"],
                     listing_data["description"], listing_data["municipality_id"],
                     listing_data["condition_id"], listing_data["property_type_id"]])

def get_listings():
    sql = """SELECT listings.id,
                    listings.rooms,
                    listings.rent,
                    listings.size,
                    m.value AS municipality
             FROM listings
             JOIN classes m ON m.id = listings.municipality_id
             ORDER BY listings.id DESC"""
    return db.query(sql)

def get_listing(listing_id):
    sql = """SELECT listings.*,
                    users.id AS user_id,
                    users.username,
                    m.id AS municipality_id,
                    m.value AS municipality,
                    c.id AS condition_id,
                    c.value AS condition,
                    p.id AS property_type_id,
                    p.value AS property_type
            FROM listings
            JOIN users ON users.id = listings.user_id
            JOIN classes m ON m.id = listings.municipality_id
            JOIN classes c ON c.id = listings.condition_id
            JOIN classes p ON p.id = listings.property_type_id
            WHERE listings.id = ?"""
    result = db.query(sql, [listing_id])
    return result[0] if result else None

def get_classes(title):
    sql = "SELECT id, value FROM classes WHERE title = ? ORDER BY id"
    return db.query(sql, [title])

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
    municipality_id = request.form["municipality_id"]
    if not re.search("^[0-9]+$", municipality_id):
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
    condition_id = request.form["condition_id"]
    if not re.search("^[0-9]+$", condition_id):
        abort(403)
    property_type_id = request.form["property_type_id"]
    if not re.search("^[0-9]+$", property_type_id):
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
        "municipality_id": municipality_id,
        "address": address,
        "postcode": postcode,
        "floor": floor,
        "floors": floors,
        "condition_id": condition_id,
        "property_type_id": property_type_id,
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
                    address = ?, postcode = ?, floor = ?, floors = ?,
                    sauna = ?, balcony = ?, bath = ?, elevator = ?, laundry = ?,
                    cellar = ?, pool = ?, description = ?, municipality_id = ?,
                    condition_id = ?, property_type_id = ?
            WHERE id = ?"""
    db.execute(sql, [listing_data["rooms"], listing_data["size"],
                     listing_data["rent"], listing_data["address"],
                     listing_data["postcode"], listing_data["floor"],
                     listing_data["floors"], listing_data["sauna"],
                     listing_data["balcony"], listing_data["bath"],
                     listing_data["elevator"], listing_data["laundry"],
                     listing_data["cellar"], listing_data["pool"],
                     listing_data["description"], listing_data["municipality_id"],
                     listing_data["condition_id"], listing_data["property_type_id"],listing_id])

def remove_listing(listing_id):
    db.execute("DELETE FROM listings WHERE id = ?", [listing_id])

def search_listings(query):
    sql = """SELECT listings.id,
                    listings.rooms,
                    listings.rent,
                    listings.size,
                    users.username,
                    users.id AS user_id,
                    m.value AS municipality
             FROM listings
             JOIN users ON listings.user_id = users.id
             JOIN classes m ON m.id = listings.municipality_id
             WHERE m.value LIKE ? OR listings.description LIKE ?
             ORDER BY listings.id DESC"""

    result = "%" + query + "%"
    return db.query(sql, [result, result])