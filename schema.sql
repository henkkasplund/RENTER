CREATE TABLE users (
    id INTEGER PRIMARY KEY,
    username TEXT UNIQUE,
    rating INTEGER DEFAULT 5 CHECK(rating BETWEEN 0 AND 5),
    phone TEXT,
    email TEXT,
    password_hash TEXT,
    image BLOB
);
CREATE TABLE ratings (
    id INTEGER PRIMARY KEY,
    rater_id INTEGER REFERENCES users(id) ON DELETE SET NULL,
    target_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    rating INTEGER NOT NULL CHECK(rating BETWEEN 0 AND 5),
    UNIQUE(rater_id, target_id)
);
CREATE TABLE classes (
    id INTEGER PRIMARY KEY,
    title TEXT,
    value TEXT
);
CREATE TABLE offers (
    id INTEGER PRIMARY KEY,
    listing_id INTEGER REFERENCES listings(id) ON DELETE CASCADE,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    price INTEGER,
    status TEXT DEFAULT "pending",
    UNIQUE(user_id, listing_id)
);
CREATE TABLE offer_history (
    id INTEGER PRIMARY KEY,
    offer_id INTEGER REFERENCES offers(id) ON DELETE CASCADE,
    price INTEGER,
    event TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE listings (
    id INTEGER PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    size REAL,
    rent INTEGER,
    address TEXT,
    postcode TEXT,
    floor TEXT,
    floors TEXT,
    sauna INTEGER,
    balcony INTEGER,
    dishwasher INTEGER,
    washing_machine INTEGER,
    bath INTEGER,
    elevator INTEGER,
    laundry INTEGER,
    cellar INTEGER,
    gym INTEGER,
    pool INTEGER,
    description TEXT,
    rooms_id INTEGER REFERENCES classes(id),
    municipality_id INTEGER REFERENCES classes(id),
    condition_id INTEGER REFERENCES classes(id),
    property_type_id INTEGER REFERENCES classes(id),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE likes (
    id INTEGER PRIMARY KEY,
    user_id INTEGER REFERENCES users ON DELETE CASCADE,
    listing_id INTEGER REFERENCES listings(id) ON DELETE CASCADE,
    UNIQUE(user_id, listing_id)
);
CREATE TABLE images (
    id INTEGER PRIMARY KEY,
    listing_id INTEGER REFERENCES listings(id) ON DELETE CASCADE,
    featured BOOLEAN DEFAULT false,
    image BLOB,
    mimetype TEXT
);
CREATE INDEX idx_listings_user ON listings (user_id);
CREATE INDEX idx_offers_listing ON offers (listing_id);
CREATE INDEX idx_offers_user ON offers (user_id);