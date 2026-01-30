CREATE TABLE users (
    id INTEGER PRIMARY KEY,
    username TEXT UNIQUE,
    password_hash TEXT
);
CREATE TABLE listings (
    id INTEGER PRIMARY KEY,
    user_id INTEGER REFERENCES users,
    rooms INTEGER,
    size REAL,
    rent INTEGER,
    municipality TEXT,
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
    description TEXT
);