CREATE TABLE users (
    id INTEGER PRIMARY KEY,
    username TEXT UNIQUE,
    rating INTEGER,
    password_hash TEXT
);
CREATE TABLE listings (
    id INTEGER PRIMARY KEY,
    user_id INTEGER REFERENCES users,
    rooms INTEGER,
    size REAL,
    rent INTEGER,
    address TEXT,
    postcode TEXT,
    floor TEXT,
    floors TEXT,
    sauna INTEGER,
    balcony INTEGER,
    bath INTEGER,
    elevator INTEGER,
    laundry INTEGER,
    cellar INTEGER,
    pool INTEGER,
    description TEXT,
    municipality_id INTEGER REFERENCES classes(id),
    condition_id INTEGER REFERENCES classes(id),
    property_type_id INTEGER REFERENCES classes(id)
);
CREATE TABLE classes (
    id INTEGER PRIMARY KEY,
    title TEXT,
    value TEXT
);
CREATE TABLE likes (
    id INTEGER PRIMARY KEY,
    user_id INTEGER REFERENCES users,
    listing_id INTEGER REFERENCES listings,
    UNIQUE(user_id, listing_id)
);