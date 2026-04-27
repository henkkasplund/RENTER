import re
from flask import abort, request
import db
from validation import validation_error


def rental_status(listing_id):
    sql = "SELECT 1 FROM offers WHERE listing_id = ? AND status = 'confirmed'"
    return bool(db.query(sql, [listing_id]))

def add_offer(listing_id, user_id, price):
    if rental_status(listing_id):
        abort(403)
    sql = """SELECT id, status, price
            FROM offers
            WHERE listing_id = ?
            AND user_id = ?"""
    result = db.query(sql, [listing_id, user_id])
    if not result:
        db.execute("INSERT INTO offers (listing_id, user_id, price) VALUES (?, ?, ?)",
                   [listing_id, user_id, price])
        offer_id = db.last_insert_id()
        db.execute("INSERT INTO offer_history (offer_id, price, event) VALUES (?, ?, ?)",
                   [offer_id, price, "sent"])
        return
    offer = result[0]
    if offer["status"] in ("pending", "accepted", "confirmed"):
        abort(403)
    max_rejected = get_max_rejected(offer["id"])
    if int(price) <= max_rejected:
        validation_error(f"VIRHE: uuden tarjouksen oltava suurempi kuin {max_rejected} €/kk")
    db.execute("UPDATE offers SET price = ?, status = 'pending' WHERE id = ?",
               [price, offer["id"]])
    db.execute("INSERT INTO offer_history (offer_id, price, event) VALUES (?, ?, ?)",
               [offer["id"], price, "sent"])

def get_offer_data():
    price = request.form["price"]
    if not price or len(price) > 20:
        abort(403)
    if not re.search(r"^[1-9][0-9]{0,4}$", price):
        abort(403)
    listing_id = request.form["listing_id"]
    if not re.search(r"^[0-9]+$", listing_id):
        abort(403)
    return {"price": int(price), "listing_id": int(listing_id)}

def handle_offer(offer_id, decision):
    offer = get_offer(offer_id)
    if not offer:
        abort(404)
    if decision == "accept":
        if offer["status"] != "pending":
            abort(403)
        db.execute("UPDATE offers SET status = 'accepted' WHERE id = ?", [offer_id])
        db.execute("INSERT INTO offer_history (offer_id, price, event) VALUES (?, ?, ?)",
               [offer_id, offer["price"], "accepted"])
    elif decision == "reject":
        if offer["status"] != "pending":
            abort(403)
        db.execute("UPDATE offers SET status = 'rejected' WHERE id = ?", [offer_id])
        db.execute("INSERT INTO offer_history (offer_id, price, event) VALUES (?, ?, ?)",
               [offer_id, offer["price"], "rejected"])
    elif decision == "cancel_accept":
        if offer["status"] != "accepted":
            abort(403)
        db.execute("UPDATE offers SET status = 'pending' WHERE id = ?", [offer_id])
        db.execute("INSERT INTO offer_history (offer_id, price, event) VALUES (?, ?, ?)",
               [offer_id, offer["price"], "cancel_accept"])
    else:
        abort(403)

def modify_offer(offer_id, user_id, action, price=None):
    sql = "SELECT id, status, price FROM offers WHERE id = ? AND user_id = ?"
    result = db.query(sql, [offer_id, user_id])
    if not result:
        abort(403)
    offer = result[0]
    status = offer["status"]
    if action == "update":
        if status not in ("pending", "rejected", "withdrawn"):
            abort(403)
        if not price or not re.search(r"^[1-9][0-9]{0,4}$", price):
            abort(403)
        max_rejected = get_max_rejected(offer["id"])
        if int(price) <= max_rejected:
            validation_error(f"VIRHE: uuden tarjouksen oltava suurempi kuin {max_rejected} €/kk")
        db.execute("UPDATE offers SET price = ?, status = 'pending' WHERE id = ?",
                    [price, offer_id])
        db.execute("INSERT INTO offer_history (offer_id, price, event) VALUES (?, ?, ?)",
                    [offer_id, price, "updated"])
    elif action == "delete":
        if status == "pending":
            db.execute("""DELETE FROM offer_history WHERE id = (
                SELECT id FROM offer_history
                WHERE offer_id = ?
                ORDER BY id DESC
                LIMIT 1)""", [offer_id])
            db.execute("UPDATE offers SET status = 'withdrawn' WHERE id = ?", [offer_id])
        elif status == "accepted":
            db.execute("UPDATE offers SET status = 'withdrawn' WHERE id = ?", [offer_id])
            db.execute("INSERT INTO offer_history (offer_id, price, event) VALUES (?, ?, ?)",
                    [offer_id, offer["price"], "withdrawn"])
        else:
            abort(403)
    else:
        abort(403)

def confirm_rental(offer_id):
    offer = get_offer(offer_id)
    if not offer:
        abort(404)
    if offer["status"] != "accepted":
        abort(403)
    if rental_status(offer["listing_id"]):
        abort(403)
    other_offers = db.query(
        "SELECT id, price FROM offers WHERE listing_id = ? AND id != ?",
        [offer["listing_id"], offer_id])
    db.execute("UPDATE offers SET status = 'confirmed' WHERE id = ?", [offer_id])
    db.execute("INSERT INTO offer_history (offer_id, price, event) VALUES (?, ?, ?)",
               [offer_id, offer["price"], "confirmed"])
    db.execute("UPDATE offers SET status = 'rejected' WHERE listing_id = ? AND id != ?",
               [offer["listing_id"], offer_id])
    for other in other_offers:
        db.execute("INSERT INTO offer_history (offer_id, price, event) VALUES (?, ?, ?)",
                   [other["id"], other["price"], "rejected"])

def get_offers(listing_id, viewer_id, owner_id):
    if not viewer_id:
        return []
    sql = """SELECT offers.id,
                    offers.price,
                    offers.status,
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
    sql = """SELECT offers.id,
                    offers.listing_id,
                    offers.user_id,
                    offers.price,
                    offers.status,
                    users.username,
                    users.phone,
                    users.email,
                    users.rating
             FROM offers
             JOIN users ON offers.user_id = users.id
             WHERE offers.id = ?"""
    result = db.query(sql, [offer_id])
    return result[0] if result else None

def get_sent_offers(user_id):
    sql = """SELECT offers.id,
                    offers.price,
                    offers.status,
                    listings.id AS listing_id,
                    listings.rent,
                    listings.size,
                    listings.address,
                    m.value AS municipality,
                    r.value AS rooms,
                    users.username AS owner_username,
                    users.phone AS owner_phone,
                    users.email AS owner_email,
                    users.id AS owner_id,
                    users.rating AS owner_rating
                FROM offers
                JOIN listings ON offers.listing_id = listings.id
                JOIN users ON users.id = listings.user_id
                JOIN classes m ON m.id = listings.municipality_id
                JOIN classes r ON r.id = listings.rooms_id
                WHERE offers.user_id = ?
                ORDER BY offers.id DESC"""
    return db.query(sql, [user_id])

def get_received_offers(user_id):
    sql = """SELECT offers.id,
                    offers.price,
                    offers.status,
                    offers.user_id AS tenant_id,
                    users.username AS tenant_username,
                    users.phone AS tenant_phone,
                    users.email AS tenant_email,
                    users.rating AS tenant_rating,
                    listings.id AS listing_id,
                    listings.rent,
                    listings.size,
                    listings.address,
                    m.value AS municipality,
                    r.value AS rooms
            FROM offers
            JOIN listings ON offers.listing_id = listings.id
            JOIN users ON users.id = offers.user_id
            JOIN classes m ON m.id = listings.municipality_id
            JOIN classes r ON r.id = listings.rooms_id
            WHERE listings.user_id = ?
            ORDER BY offers.id DESC"""
    return db.query(sql, [user_id])

def get_offer_stats(user_id):
    sent_offers = get_sent_offers(user_id)
    received_offers = get_received_offers(user_id)
    withdrawn_sent = sum(
        1 for offer in sent_offers if offer['status'] == "withdrawn"
    )
    inactive_received = sum(
        1 for offer in received_offers if offer['status'] in ("withdrawn", "rejected")
    )
    return {
        "sent_offers": sent_offers,
        "received_offers": received_offers,
        "active_sent": len(sent_offers) - withdrawn_sent,
        "active_received": len(received_offers) - inactive_received,
    }

def get_offer_history(offer_id):
    sql = """SELECT price, created_at, event
             FROM offer_history
             WHERE offer_id = ?
             ORDER BY id DESC"""
    return db.query(sql, [offer_id])

def confirmed_deal(viewer_id, user_id):
    sql = """SELECT 1 FROM offers
            JOIN listings ON offers.listing_id = listings.id
            WHERE offers.status = 'confirmed'
            AND ((offers.user_id = ? AND listings.user_id = ?)
            OR (offers.user_id = ? AND listings.user_id = ?))
            LIMIT 1"""
    return bool(db.query(sql, [viewer_id, user_id, user_id, viewer_id]))

def get_max_rejected(offer_id):
    sql = """SELECT MAX(price) as max_rejected
             FROM offer_history
             WHERE offer_id = ? AND event = 'rejected'"""
    result = db.query(sql, [offer_id])
    return result[0]["max_rejected"] if result[0]["max_rejected"] else 0
