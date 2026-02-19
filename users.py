from flask import abort
from werkzeug.security import check_password_hash, generate_password_hash
import db
import re
import ratings


def get_user(user_id):
    sql = "SELECT id, username, rating, phone, email FROM users WHERE id = ?"
    result = db.query(sql, [user_id])
    return result[0] if result else None

def update_contact(user_id, phone, email):
    if phone and not re.search("^[0-9+ -]{5,20}$", phone):
        abort(403)
    if email and not re.search("^[^@]+@[^@]+\.[^@]+$", email):
        abort(403)
    sql = "UPDATE users SET phone = ?, email = ? WHERE id = ?"
    db.execute(sql, [phone, email, user_id])

def get_user_listings(user_id):
    sql = """SELECT listings.id,
                    listings.rent,
                    listings.size,
                    r.value AS rooms,
                    m.value AS municipality
             FROM listings
             JOIN classes r ON r.id = listings.rooms_id
             JOIN classes m ON m.id = listings.municipality_id
             WHERE listings.user_id = ?
             ORDER BY listings.id DESC"""
    return db.query(sql, [user_id])

def get_liked(user_id):
    sql = """SELECT listings.id,
                    listings.rent,
                    listings.size,
                    r.value AS rooms,
                    m.value AS municipality
            FROM likes
            JOIN listings ON likes.listing_id = listings.id
            JOIN classes r ON r.id = listings.rooms_id
            JOIN classes m ON m.id = listings.municipality_id
            WHERE likes.user_id = ?
            ORDER BY listings.id DESC"""
    return db.query(sql, [user_id])

def create_user(username, password):
    password_hash = generate_password_hash(password)
    sql = "INSERT INTO users (username, password_hash) VALUES (?, ?)"
    db.execute(sql, [username, password_hash])

def delete_user(user_id):
    sql = "DELETE FROM users WHERE id = ?"
    db.execute(sql, [user_id])

def check_login(username, password):
    sql = "SELECT id, password_hash, rating FROM users WHERE username = ?"
    matching_username = db.query(sql, [username])
    if not matching_username:
        return None
    user = matching_username[0]
    if check_password_hash(user["password_hash"], password):
        return {"id": user["id"], "rating": user["rating"]}
    return None

def update_rating(user_id):
    rating = ratings.calculate_rating(user_id)
    sql = "UPDATE users SET rating = ? WHERE id = ?"
    db.execute(sql, [rating, user_id])