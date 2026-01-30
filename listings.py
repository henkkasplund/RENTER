import db

def add_listing(user_id, rooms, size, rent, municipality, address, postcode, floor,
                floors, sauna, balcony, bath, elevator, laundry, cellar, pool, description):
    sql = """INSERT INTO listings (user_id, rooms, size,rent, municipality,
                                address, postcode,floor,floors, sauna, balcony,
                                bath, elevator, laundry, cellar, pool, description)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"""

    db.execute(sql, [user_id, rooms, size, rent, municipality, address, postcode, floor, floors, sauna, balcony,
                                bath, elevator, laundry, cellar, pool, description])

def get_listings():
    sql = "SELECT id, municipality, rooms, rent, size FROM listings ORDER BY id DESC"
    return db.query(sql)

def get_listing(listing_id): #tähän vielä rating mukaan
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
    return db.query(sql, [listing_id])[0]

def update_listing(listing_id, rooms, size, rent, municipality, address, postcode, floor,
                floors, sauna, balcony, bath, elevator, laundry, cellar, pool, description):
    sql = """UPDATE listings SET rooms = ?, size = ?, rent = ?,
                    municipality = ?, address = ?, postcode = ?,
                    floor = ?, floors = ?, sauna = ?, balcony = ?,
                    bath = ?, elevator = ?, laundry = ?, cellar = ?,
                    pool = ?, description = ?
            WHERE id = ?"""
    db.execute(sql, [rooms, size, rent, municipality, address, postcode, floor, floors, sauna, balcony,
                                bath, elevator, laundry, cellar, pool, description, listing_id])

def remove_listing(listing_id):
    sql = "DELETE FROM listings WHERE id = ?"
    db.execute(sql, [listing_id])

def search_listings(query):
    sql = """SELECT id, rooms, municipality, rent, size
            FROM listings
            WHERE municipality LIKE ? OR description LIKE ?
            ORDER BY id DESC"""
    result = "%" + query + "%"
    return db.query(sql, [result, result])