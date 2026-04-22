import random
import sqlite3

db = sqlite3.connect("database.db")

db.execute("DELETE FROM offer_history")
db.execute("DELETE FROM offers")
db.execute("DELETE FROM likes")
db.execute("DELETE FROM images")
db.execute("DELETE FROM listings")
db.execute("DELETE FROM users")

user_count = 100
listing_count = 1000

for i in range(1, user_count + 1):
    db.execute("INSERT INTO users (username, password_hash) VALUES (?, ?)",
               [f"user{i}", "test"])

municipality_ids = [row[0] for row in db.execute("SELECT id FROM classes WHERE title = 'municipality'").fetchall()]
rooms_ids = [row[0] for row in db.execute("SELECT id FROM classes WHERE title = 'rooms'").fetchall()]
condition_ids = [row[0] for row in db.execute("SELECT id FROM classes WHERE title = 'condition'").fetchall()]
property_type_ids = [row[0] for row in db.execute("SELECT id FROM classes WHERE title = 'property_type'").fetchall()]

for i in range(1, listing_count + 1):
    user_id = random.randint(1, user_count)
    db.execute("""INSERT INTO listings (user_id, address, postcode, municipality_id,
                  rooms_id, condition_id, property_type_id, size, rent, floors, description)
                  VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
               [user_id, f"Testikatu {i}", "00100",
                random.choice(municipality_ids),
                random.choice(rooms_ids),
                random.choice(condition_ids),
                random.choice(property_type_ids),
                random.randint(20, 150),
                random.randint(500, 3000),
                str(random.randint(1, 8)),
                f"Testikuvaus ilmoitukselle {i}"])

db.commit()
db.close()