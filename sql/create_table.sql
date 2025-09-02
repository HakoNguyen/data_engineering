CREATE TABLE listings (
    id BIGINT PRIMARY KEY,
    name TEXT,
    host_name TEXT,
    neighbourhood TEXT,
    latitude FLOAT,
    longitude FLOAT,
    room_type TEXT,
    price INT,
    minimum_nights INT,
    number_of_reviews INT,
    calculated_host_listings_count INT,
    license TEXT
);

CREATE TABLE reviews (
    review_id SERIAL PRIMARY KEY,
    listing_id BIGINT NOT NULL,
    review_date DATE NOT NULL,
    FOREIGN KEY (listing_id) REFERENCES listings(id)
);
