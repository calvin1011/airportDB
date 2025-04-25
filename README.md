# ✈️ Airport Management System

This project is a full-stack airport management system built as part of a database course assignment. It integrates a PostgreSQL database with both a **Flask web application (for managers)** and a **Java Swing desktop application (for technicians)**. It supports full CRUD operations, secure authentication, and test event recording using JDBC/ODBC.

---
Setup Instructions
Part 1: Database Setup

    Connect to the CS PostgreSQL server.

    Run the create_database.sql script:

    cspsql < create_database.sql

Part 2: Manager Web App (Flask)

    Set up a Python virtual environment:

python3 -m venv venv
source venv/bin/activate
pip install flask pyodbc

Run the app:

python manager_app.py

Access it in the browser:

    http://127.0.0.1:5000

    Ensure you’re SSH tunneling port 6543 to faure.cs.colostate.edu:5432 before running.

Part 3: Technician App (Java + JDBC)

    Ensure you have the JDBC driver (postgresql-42.7.5.jar) in the same directory.

    Compile and run:

    javac AirplaneTestApp.java
    java -cp ".;postgresql-42.7.5.jar" AirplaneTestApp

    On Linux/macOS, replace ; with : in the classpath.

    Login as a technician using an SSN and hashed password stored in the employee table.

Features
Web App (Manager)

    Secure login via SHA-256

    Manage employees (CRUD)

    Assign roles (Manager, Technician, ATC)

    Link technicians to aircraft models

    Create/update airplane models

    Manage FAA test definitions

    Record/view airworthiness test data

    Increase employee salaries by percentage

Java App (Technician)

    Technician login via hashed password

    Dropdown selection for airplanes and tests

    Record duration (H:M:S) and score

    Submit new test_event to the database

Security

    All passwords are hashed with SHA-256 before storage or comparison.

    Only managers can access the web portal.

    Only technicians can log in and record test events in the Java app.

Testing

    Use SQL to verify:

    SELECT * FROM test_event;

    Confirm successful insertions after form submissions.

Authors & Acknowledgments

    Developed by: [Your Name]

    Guided by: CSU Department of Computer Science

    JDBC Driver: PostgreSQL Global Development Group

License

This project is for educational purposes only. Redistribution for commercial use is not permitted.