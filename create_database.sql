
-- Drop tables in reverse dependency order
DROP TABLE IF EXISTS test_event CASCADE;
DROP TABLE IF EXISTS expert CASCADE;
DROP TABLE IF EXISTS airplane CASCADE;
DROP TABLE IF EXISTS airplane_model CASCADE;
DROP TABLE IF EXISTS faa_test CASCADE;
DROP TABLE IF EXISTS manager CASCADE;
DROP TABLE IF EXISTS technician CASCADE;
DROP TABLE IF EXISTS atc CASCADE;
DROP TABLE IF EXISTS employee CASCADE;

-- Table Definitions
CREATE TABLE employee (
    ssn CHAR(9) PRIMARY KEY,
    name TEXT NOT NULL,
    password TEXT NOT NULL,
    address TEXT,
    phone TEXT,
    salary NUMERIC(100, 2) CHECK (salary >= 0)
);

CREATE TABLE manager (
    ssn CHAR(9) PRIMARY KEY REFERENCES employee(ssn)
);

CREATE TABLE technician (
    ssn CHAR(9) PRIMARY KEY REFERENCES employee(ssn)
);

CREATE TABLE atc (
    ssn CHAR(9) PRIMARY KEY REFERENCES employee(ssn)
);

CREATE TABLE airplane_model (
    model_number TEXT PRIMARY KEY,
    capacity INTEGER CHECK (capacity > 0),
    weight INTEGER CHECK (weight > 0)
);

CREATE TABLE airplane (
    reg_number TEXT PRIMARY KEY,
    model_number TEXT REFERENCES airplane_model(model_number)
);

CREATE TABLE faa_test (
    test_number INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    max_score INTEGER CHECK (max_score > 0)
);

CREATE TABLE expert (
    ssn CHAR(9),
    model_number TEXT,
    PRIMARY KEY (ssn, model_number),
    FOREIGN KEY (ssn) REFERENCES employee(ssn),
    FOREIGN KEY (model_number) REFERENCES airplane_model(model_number)
);

CREATE TABLE test_event (
    test_number INTEGER,
    ssn CHAR(9),
    reg_number TEXT,
    date DATE NOT NULL,
    duration INTERVAL,
    score INTEGER,
    PRIMARY KEY (test_number, ssn, reg_number),
    FOREIGN KEY (test_number) REFERENCES faa_test(test_number),
    FOREIGN KEY (ssn) REFERENCES technician(ssn),
    FOREIGN KEY (reg_number) REFERENCES airplane(reg_number)
);

-- Stored Procedure to enforce technician expertise
CREATE OR REPLACE FUNCTION insert_test_event(
    p_test_number INTEGER,
    p_ssn CHAR(9),
    p_reg_number TEXT,
    p_date DATE,
    p_duration INTERVAL,
    p_score INTEGER
)
RETURNS VOID AS $$
DECLARE
    v_model TEXT;
BEGIN
    SELECT model_number INTO v_model FROM airplane WHERE reg_number = p_reg_number;

    IF NOT EXISTS (
        SELECT 1 FROM expert
        WHERE ssn = p_ssn AND model_number = v_model
    ) THEN
        RAISE EXCEPTION 'Technician % is not an expert on model %', p_ssn, v_model;
    END IF;

    INSERT INTO test_event(test_number, ssn, reg_number, date, duration, score)
    VALUES (p_test_number, p_ssn, p_reg_number, p_date, p_duration, p_score);
END;
$$ LANGUAGE plpgsql;
