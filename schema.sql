CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email VARCHAR NOT NULL UNIQUE,
    phone VARCHAR,
    fam VARCHAR,
    name VARCHAR,
    otc VARCHAR
);

CREATE TABLE coords (
    id SERIAL PRIMARY KEY,
    latitude DOUBLE PRECISION NOT NULL,
    longitude DOUBLE PRECISION NOT NULL,
    height INTEGER NOT NULL
);

CREATE TABLE pereval_added (
    id SERIAL PRIMARY KEY,
    beautyTitle VARCHAR NOT NULL,
    title VARCHAR NOT NULL,
    other_titles VARCHAR,
    connect VARCHAR,
    add_time TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    user_id INTEGER NOT NULL REFERENCES users(id),
    coord_id INTEGER NOT NULL REFERENCES coords(id),
    winter_level VARCHAR,
    summer_level VARCHAR,
    autumn_level VARCHAR,
    spring_level VARCHAR,
    status VARCHAR NOT NULL DEFAULT 'new',
    CONSTRAINT check_pereval_status
        CHECK (status IN ('new', 'pending', 'accepted', 'rejected'))
);

CREATE TABLE pereval_images (
    id SERIAL PRIMARY KEY,
    pereval_id INTEGER NOT NULL REFERENCES pereval_added(id),
    title VARCHAR,
    img BYTEA,
    date_added TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);
