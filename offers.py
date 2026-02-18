import db
from flask import abort, request
import re


def rental_status(listing_id):
    sql = "SELECT 1 FROM offers WHERE listing_id = ? AND owner_accepted = 1"
    return bool(db.query(sql, [listing_id]))

def add_offer(listing_id, user_id, price):
    if rental_status(listing_id):
        abort(403)
    sql = """SELECT 1 FROM offers
             WHERE listing_id = ? AND user_id = ?"""
    if db.query(sql, [listing_id, user_id]):
        abort(403)
    sql = """INSERT INTO offers (listing_id, user_id, price)
             VALUES (?, ?, ?)"""
    db.execute(sql, [listing_id, user_id, price])
    
def get_offer_data():
    price = request.form["price"]
    if not price or len(price) > 20:
        abort(403)
    if not re.search("^[1-9][0-9]{0,4}$", price):
        abort(403)
    listing_id = request.form["listing_id"]
    if not re.search("^[0-9]+$", listing_id):
        abort(403)
    return {"price": int(price), "listing_id": int(listing_id)}

def handle_offer(offer_id, decision):
    offer = get_offer(offer_id)
    if not offer:
        abort(404)
    if decision == "accept":
        sql = "UPDATE offers SET owner_accepted = 1 WHERE id = ?"
        db.execute(sql, [offer_id])
        sql = "DELETE FROM offers WHERE user_id = ? AND id != ?"
        db.execute(sql, [offer["user_id"], offer_id])
        sql = "DELETE FROM offers WHERE listing_id = ? AND id != ?"
        db.execute(sql, [offer["listing_id"], offer_id])
    elif decision == "reject":
        sql = "DELETE FROM offers WHERE id = ?"
        db.execute(sql, [offer_id])
    else:
        abort(403)

def modify_offer(offer_id, user_id, action, price=None):
    sql = """SELECT owner_accepted
             FROM offers
             WHERE id = ? AND user_id = ?"""
    offer = db.query(sql, [offer_id, user_id])
    if not offer:
        abort(403)
    if offer[0]["owner_accepted"]:
        abort(403)
    if action == "update":
        if not price or not re.search("^[1-9][0-9]{0,4}$", price):
            abort(403)
        sql = "UPDATE offers SET price = ? WHERE id = ?"
        db.execute(sql, [int(price), offer_id])
    elif action == "delete":
        sql = "DELETE FROM offers WHERE id = ?"
        db.execute(sql, [offer_id])
    else:
        abort(403)
def get_offers(listing_id, viewer_id, owner_id):
    if not viewer_id:
        return []
    sql = """SELECT offers.id,
                    offers.price,
                    offers.owner_accepted,
                    users.id AS user_id,
                    users.username,
                    users.rating,
                    users.phone,
                    users.email
             FROM offers
             JOIN users ON offers.user_id = users.id
             WHERE offers.listing_id = ?"""
    values = [listing_id]
    if viewer_id != owner_id:
        sql += " AND offers.user_id = ?"
        values.append(viewer_id)
    sql += " ORDER BY offers.id DESC"
    return db.query(sql, values)

def get_offer(offer_id):
    sql = """SELECT id, listing_id, user_id, price, owner_accepted
             FROM offers
             WHERE id = ?"""
    result = db.query(sql, [offer_id])
    return result[0] if result else None

def get_user_offers(user_id):
    sql = """SELECT offers.id AS offer_id,
                    offers.price,
                    offers.owner_accepted,
                    listings.id AS listing_id,
                    listings.rent,
                    listings.size,
                    m.value AS municipality,
                    r.value AS rooms
            FROM offers
            JOIN listings ON offers.listing_id = listings.id
            JOIN classes m ON m.id = listings.municipality_id
            JOIN classes r ON r.id = listings.rooms_id
            WHERE offers.user_id = ?
            ORDER BY offers.id DESC"""
    return db.query(sql, [user_id])