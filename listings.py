import db

def add_listing(title, description, price, user_id):
    sql = """INSERT INTO listings (title, description, price, user_id) VALUES (?, ?, ?, ?)"""

    db.execute(sql, [title, description, price, user_id])