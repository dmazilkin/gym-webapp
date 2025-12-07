CREATE TABLE contacts(
    id_contact INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    phone_number TEXT NOT NULL,
    email TEXT NOT NULL
);

CREATE TABLE clients(
    id_client INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    name VARCHAR(20) NOT NULL,
    surname VARCHAR(20) NOT NULL,
    birthday DATE NOT NULL,
    sex CHAR(1) NOT NULL,
    discount FLOAT NOT NULL,
    id_contact INT REFERENCES contacts(id_contact) NOT NULL,
    is_admin BOOLEAN NOT NULL DEFAULT FALSE
);

CREATE TABLE passwords (
    id_password INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    id_client   INT NOT NULL UNIQUE REFERENCES clients(id_client),
    password_hash VARCHAR(255) NOT NULL,
    created_at  TIMESTAMP DEFAULT NOW()
);

CREATE TABLE trainers(
    id_trainer INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    name VARCHAR(20) NOT NULL,
    surname VARCHAR(20) NOT NULL,
    birthday DATE NOT NULL,
    sex CHAR(1) NOT NULL,
    id_contact INT REFERENCES contacts(id_contact) NOT NULL
);

CREATE TABLE contracts(
    id_contract INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    salary INT NOT NULL,
    contract_type TEXT NOT NULL,
    date_from DATE NOT NULL,
    date_to DATE NOT NULL,
    id_trainer INT REFERENCES trainers(id_trainer) NOT NULL
);

CREATE TABLE gyms(
    id_gym INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    country TEXT NOT NULL,
    city TEXT NOT NULL,
    postcode TEXT NOT NULL,
    street TEXT NOT NULL,
    building TEXT NOT NULL
);

CREATE TYPE WEEK_DAY AS ENUM('Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday');

CREATE TABLE groups(
    id_group INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    id_trainer INT REFERENCES trainers(id_trainer) NOT NULL,
    id_gym INT REFERENCES gyms(id_gym) NOT NULL,
    max_capacity INT NOT NULL,
    time_start TIME NOT NULL,
    time_finish TIME NOT NULL,
    week_day WEEK_DAY NOT NULL
);

CREATE TABLE registered(
    id_registered INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    id_group INT REFERENCES groups(id_group) NOT NULL,
    id_client INT REFERENCES clients(id_client) NOT NULL
);

CREATE TABLE opening_hours(
    id_opening_hours INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    id_gyms INT REFERENCES gyms(id_gym),
    week_day WEEK_DAY NOT NULL,
    time_open TIME NOT NULL,
    time_close TIME NOT NULL
);

CREATE TYPE PAYMENT_CURRENCY AS ENUM('CZK', 'EUR');

CREATE TABLE membership_types(
    id_membership_type INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    title TEXT NOT NULL,
    price MONEY NOT NULL,
    currency PAYMENT_CURRENCY NOT NULL,
    duration INT NOT NULL,
    description TEXT NOT NULL
);

CREATE TYPE MEMBERSHIP_STATUSES AS ENUM('Active', 'Suspended', 'Cancelled');

CREATE TABLE memberships(
    id_membership INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    id_client INT REFERENCES clients(id_client) NOT NULL,
    id_membership_type INT REFERENCES membership_types(id_membership_type) NOT NULL,
    id_gym INT REFERENCES gyms(id_gym) NOT NULL,
    membership_status MEMBERSHIP_STATUSES NOT NULL,
    membership_start DATE NOT NULL,
    membership_stop DATE NOT NULL
);

CREATE TYPE PAYMENT_STATUS AS ENUM('Pending', 'Successful', 'Failed');

CREATE TABLE payments(
    id_payment INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    payment_status PAYMENT_STATUS NOT NULL,
    amount MONEY NOT NULL,
    currency PAYMENT_CURRENCY NOT NULL,
    date_creation TIMESTAMP NOT NULL,
    date_payment TIMESTAMP NOT NULL,
    date_due_date TIMESTAMP NOT NULL,
    id_membership INT REFERENCES memberships(id_membership) NOT NULL
);