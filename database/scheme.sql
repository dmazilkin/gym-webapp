CREATE TABLE contacts(
    id_contact PRIMARY KEY,
    phone_number TEXT NOT NULL,
    email TEXT NOT NULL,
);

CREATE TABLE clients(
    id_client PRIMARY KEY,
    name VARCHAR(20) NOT NULL,
    surname VARCHAR(20) NOT NULL,
    birthday DATE NOT NULL,
    sex CHAR(1) NOT NULL,
    id_contact REFERENCES contacts(id_contact) NOT NULL,
);

CREATE TABLE trainers(
    id_trainer PRIMARY KEY,
    name VARCHAR(20) NOT NULL,
    surname VARCHAR(20) NOT NULL,
    birthday DATE NOT NULL,
    sex CHAR(1) NOT NULL,
    id_contact REFERENCES contacts(id_contact) NOT NULL,
);

CREATE TABLE contracts(
    id_contract PRIMARY KEY,
    salary INT NOT NULL,
    contract_type TEXT NOT NULL,
    date_from DATE NOT NULL,
    date_to DATE NOT NULL,
    id_trainer REFERENCES trainers(id_trainer) NOT NULL,
);

CREATE TYPE WEEK_DAY AS ENUM('Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday');

CREATE TABLE groups(
    id_group PRIMARY KEY,
    id_trainer REFERENCES trainers(id_trainer) NOT NULL,
    id_gym REFERENCES gyms(id_gym) NOT NULL,
    max_capacity INT NOT NULL,
    time_start TIME NOT NULL,
    time_finish TIME NOT NULL,
    week_day WEEK_DAY NOT NULL,
);

CREATE TABLE registered(
    id_registered PRIMARY KEY,
    id_group REFERENCES groups(id_group) NOT NULL,
    id_client REFERENCES clients(id_client) NOT NULL,
);

CREATE TABLE gyms(
    id_gym PRIMARY KEY,
    country TEXT NOT NULL,
    city TEXT NOT NULL,
    postcode TEXT NOT NULL,
    street TEXT NOT NULL,
    building TEXT NOT NULL,
);

CREATE TABLE opening_hours(
    id_opening_hours PRIMARY KEY,
    id_gyms REFERENCES gyms(id_gym),
    week_day WEEKDAY NOT NULL,
    time_open TIME NOT NULL,
    time_close TIME NOT NULL,
);

CREATE TYPE PAYMENT_STATUS AS ENUM('Pending', 'Successful', 'Failed');

CREATE TYPE PAYMENT_CURRENCY AS ENUM('CZK', 'EUR');

CREATE TABLE payments(
    id_payment PRIMARY KEY,
    payment_status PAYMENT_STATUS NOT NULL,
    amount MONEY NOT NULL,
    currency PAYMENT_CURRENCY NOT NULL,
    date_creation DATETIME NOT NULL,
    date_payment DATETIME NOT NULL,
    date_due_date DATETIME NOT NULL,
    id_membership REFERENCES memberships(id_membership) NOT NULL,
);

CREATE TYPE MEMBERSHIP_STATUSES ('Active', 'Suspended', 'Cancelled');

CREATE TABLE memberships(
    id_membership PRIMARY KEY,
    id_client REFERENCES clients(id_client) NOT NULL,
    id_membership_type REFERENCES membership_types(id_membership_type) NOT NULL,
    id_gym REFERENCES gyms(id_gym) NOT NULL,
    membership_status MEMBERSHIP_STATUSES NOT NULL,
    discount FLOAT NOT NULL
    membership_start DATE NOT NULL,
    membership_stop DATE NOT NULL,
);

CREATE TABLE membership_types(
    id_membership_type PRIMARY KEY,
    title TEXT NOT NULL,
    price MONEY NOT NULL,
    currency PAYMENT_CURRENCY NOT NULL,
    duration DATE NOT NULL,
    description TEXT NOT NULL,
);