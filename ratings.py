import db
from flask import abort
import re
import offers


def calculate_rating(user_id):
    sql = """SELECT COUNT(*) AS count, SUM(rating) AS total
            FROM ratings
            WHERE target_id = ?"""
    result = db.query(sql, [user_id])[0]
    count = result["count"] + 1
    total = (result["total"] or 0) + 5
    avg = total / count
    rating = int(avg)
    if rating < avg:
        rating += 1
    return max(0, min(5, rating))

def get_rating(rater_id, target_id):
    sql = "SELECT rating FROM ratings WHERE rater_id = ? AND target_id = ?"
    result = db.query(sql, [rater_id, target_id])
    return result[0]["rating"] if result else None

def set_rating(rater_id, target_id, rating):
    rating_permission = offers.confirmed_deal(rater_id, target_id)
    if not rating_permission:
        abort(403)
    if not re.search("^[0-5]$", str(rating)):
        abort(403)
    rating = int(rating)
    sql = """INSERT INTO ratings (rater_id, target_id, rating)
             VALUES (?, ?, ?)
             ON CONFLICT(rater_id, target_id)
             DO UPDATE SET rating = excluded.rating"""
    db.execute(sql, [rater_id, target_id, rating])