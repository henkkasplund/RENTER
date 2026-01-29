import db

def add_listing(title, description, price, user_id):
    sql = """INSERT INTO listings (title, description, price, user_id) VALUES (?, ?, ?, ?)"""

    db.execute(sql, [title, description, price, user_id])

def get_listings():
    sql = "SELECT id, title FROM listings ORDER BY id DESC"
    return db.query(sql)

def get_listing(listing_id): #tähän vielä rating mukaan
    sql = """SELECT listings.title,
                    listings.description,
                    listings.price,
                    users.username
             FROM listings, users
             WHERE listings.user_id = users.id AND
                    listings.id = ?"""
    return db.query(sql, [listing_id])[0]