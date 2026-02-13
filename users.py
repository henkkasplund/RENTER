from werkzeug.security import check_password_hash, generate_password_hash
import db

def get_user(user_id):
    sql = "SELECT id, username FROM users WHERE id = ?"
    result = db.query(sql, [user_id])
    return result[0] if result else None

def get_user_listings(user_id):
    sql = """SELECT listings.id,
                    listings.rooms,
                    listings.rent,
                    listings.size,
                    m.value AS municipality
            FROM listings
            JOIN classes m ON m.id = listings.municipality_id
            WHERE listings.user_id = ?
            ORDER BY listings.id DESC"""
    return db.query(sql, [user_id])

def create_user(username, password):
    password_hash = generate_password_hash(password)
    sql = "INSERT INTO users (username, password_hash) VALUES (?, ?)"
    db.execute(sql, [username, password_hash])

def check_login(username, password):
    sql = "SELECT id, password_hash FROM users WHERE username = ?"
    matching_username = db.query(sql, [username])
    if not matching_username:
        return None
    user_id = matching_username[0]["id"]
    password_hash = matching_username[0]["password_hash"]
    if check_password_hash(password_hash, password):
        return user_id
    return None