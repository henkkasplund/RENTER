CREATE TABLE users (
    id INTEGER PRIMARY KEY,
    username TEXT UNIQUE,
    rating REAL DEFAULT 5,
    phone TEXT,
    email TEXT,
    password_hash TEXT
);
CREATE TABLE classes (
    id INTEGER PRIMARY KEY,
    title TEXT,
    value TEXT
);
CREATE TABLE offers (
    id INTEGER PRIMARY KEY,
    listing_id INTEGER REFERENCES listings ON DELETE CASCADE,
    user_id INTEGER REFERENCES users ON DELETE CASCADE,
    price INTEGER,
    owner_accepted INTEGER DEFAULT 0,
    UNIQUE(user_id, listing_id)
);
CREATE TABLE listings (
    id INTEGER PRIMARY KEY,
    user_id INTEGER REFERENCES users,
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
    rooms_id INTEGER REFERENCES classes(id),
    municipality_id INTEGER REFERENCES classes(id),
    condition_id INTEGER REFERENCES classes(id),
    property_type_id INTEGER REFERENCES classes(id)
);
CREATE TABLE likes (
    id INTEGER PRIMARY KEY,
    user_id INTEGER REFERENCES users ON DELETE CASCADE,
    listing_id INTEGER REFERENCES listings ON DELETE CASCADE,
    UNIQUE(user_id, listing_id)
);