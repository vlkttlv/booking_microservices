CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email VARCHAR NOT NULL,
    hashed_password VARCHAR NOT NULL,
    role VARCHAR DEFAULT 'user'
);

CREATE TABLE hotels (
    id SERIAL PRIMARY KEY,
    name VARCHAR NOT NULL,
    location VARCHAR NOT NULL,
    services TEXT[],
    rooms_quantity INTEGER NOT NULL
);

CREATE TABLE rooms (
    id SERIAL PRIMARY KEY,
    hotel_id INTEGER REFERENCES hotels(id) NOT NULL,
    name VARCHAR NOT NULL,
    description VARCHAR NOT NULL,
    price INTEGER NOT NULL,
    services TEXT[],
    quantity INTEGER NOT NULL
);

CREATE TABLE bookings (
    id SERIAL PRIMARY KEY,
    room_id INTEGER REFERENCES rooms(id),
    user_id INTEGER REFERENCES users(id),
    date_from DATE NOT NULL,
    date_to DATE NOT NULL,
    price INTEGER NOT NULL,
    payment_status VARCHAR DEFAULT 'not paid'
);

CREATE TABLE payments (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    booking_id INTEGER REFERENCES bookings(id),
    amount INTEGER NOT NULL,
    date_to DATE NOT NULL,
    status VARCHAR
);
