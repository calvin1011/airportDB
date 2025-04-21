import os
import pyodbc
import hashlib
from functools import wraps
from flask import Flask, session, request, render_template, redirect, url_for
from password import hash_password

# Define the DSN for the ODBC connection to your PostgreSQL database.
DSN = (
    "DRIVER={PostgreSQL ODBC Driver(UNICODE)};"
    "SERVER=localhost;"
    "PORT=6543;"
    "DATABASE=C837785579;"
    "UID=C837785579;"
    "PWD=837785579"
)


app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(24)

def login_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if 'username' not in session:
            return redirect(url_for('login'))
        return func(*args, **kwargs)
    return wrapper


def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()


def verify_password(password, hashed):
    return hash_password(password) == hashed


def parse_float(value):
    return float(value) if value.replace('.', '', 1).isdigit() else None


def parse_int(value):
    return int(value) if value.isdigit() else None


def get_employees():
    # START-STUDENT-CODE
    # 1. Connect to the database using pyodbc and DSN.
    # 2. Retrieve employees with their roles (Manager, Technician, ATC) or blank.
    # 3. Close the connection and return the result.

    employees = []

    # END-STUDENT-CODE
    return employees


def get_airplane_models():
    # START-STUDENT-CODE
    # 1. Connect to the database
    # 2. Retrieve all airplane models (model_number, capacity, weight)
    # 3. Close the connection

    models = []

    # END-STUDENT-CODE
    return models


def get_airplanes():
    # START-STUDENT-CODE
    # 1. Connect to the database
    # 2. Retrieve all airplanes (reg_number, model_number)
    # 3. Close the connection

    airplanes = []

    # END-STUDENT-CODE
    return airplanes


def get_faa_tests():
    # START-STUDENT-CODE
    # 1. Connect to the database
    # 2. Retrieve all FAA tests (test_number, name, max_score)
    # 3. Close the connection

    faa_tests = []

    # END-STUDENT-CODE
    return faa_tests


def get_airworthiness_tests():
    # START-STUDENT-CODE
    # 1. Connect to the database
    # 2. Retrieve all airworthiness test events (test_number, ssn, reg_number, date, duration, score)
    # 3. Close the connection

    tests = []

    # END-STUDENT-CODE
    return tests


@app.route('/')
@login_required
def index():
    return render_template('index.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username'].strip()
        password = request.form['password'].strip()

        # 1. Connect to the DB
        cnxn = pyodbc.connect(DSN)
        cursor = cnxn.cursor()
        # 2. Select manager based on SSN and retrieve the password
        cursor.execute('''
            SELECT e.password
            FROM employee e
            JOIN manager m ON e.ssn = m.ssn
            WHERE e.ssn = ?
        ''', (username,))
        user = cursor.fetchone()
        # 3. Close the connection
        cnxn.close()


        if user and verify_password(password, user[0]):
            session['username'] = username
            return redirect(url_for('index'))
        else:
            return render_template('login.html', message="Authentication error!")

    return render_template('login.html')


@app.route('/logout')
@login_required
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))


@app.route('/employee/add', methods=['GET', 'POST'])
@login_required
def employee_add():
    employees = get_employees()

    if request.method == 'POST':
        ssn = request.form['ssn'].strip()
        name = request.form['name'].strip() or None
        password = request.form['password'].strip() or None
        address = request.form['address'].strip() or None
        phone = request.form['phone'].strip() or None
        salary = request.form['salary'].strip()
        specialization = request.form.get('specialization')

        salary = parse_float(salary)
        password_hashed = hash_password(password) if password else None

        # 1. Connect to DB
        cnxn = pyodbc.connect(DSN)
        cursor = cnxn.cursor()

        # 2. Check if this SSN already exists
        cursor.execute("SELECT 1 FROM employee WHERE ssn = ?", (ssn,))
        exists = cursor.fetchone()

        # 3. If not, insert into employee and handle specialization
        if not exists:
            cursor.execute('''
                INSERT INTO employee (ssn, name, password, address, phone, salary)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (ssn, name, password_hashed, address, phone, salary))

        # 4. Close connection
        cnxn.commit()
        cnxn.close()


        return redirect(url_for('employee_add'))

    return render_template('employees.html', employees=employees, action='Add')


@app.route('/employee/update', methods=['GET', 'POST'])
@login_required
def employee_update():
    employees = get_employees()

    if request.method == 'POST':
        ssn = request.form['ssn'].strip()
        name = request.form['name'].strip() or None
        password = request.form['password'].strip() or None
        address = request.form['address'].strip() or None
        phone = request.form['phone'].strip() or None
        salary = request.form['salary'].strip()
        specialization = request.form.get('specialization')

        salary = parse_float(salary)
        password_hashed = hash_password(password) if password else None

        # 1. Connect to DB
        cnxn = pyodbc.connect(DSN)
        cursor = cnxn.cursor()

        # 2. Check if employee with SSN exists
        cursor.execute("SELECT 1 FROM employee WHERE ssn = ?", (ssn))
        if cursor.fetchone():
            #Build update query
            fields = []
            values = []

            if name:
                fields.append("name = ?")
                values.append(name)
            if password_hashed:
                fields.append("password = ?")
                values.append(password_hashed)
            if address:
                fields.append("address = ?")
                values.append(address)
            if phone:
                fields.append("phone = ?")
                values.append(phone)
            if salary:
                fields.append("salary = ?")
                values.append(salary)

            if fields:
                update_query = f"UPDATE employee SET {', '.join(fields)} WHERE ssn = ?"
                values.append(ssn)
                cursor.execute(update_query, values)
                cnxn.commit()
        # 5. Close connection
        cnxn.close()

        return redirect(url_for('employee_update'))

    return render_template('employees.html', employees=employees, action='Update')


@app.route('/employee/delete', methods=['GET', 'POST'])
@login_required
def employee_delete():
    employees = get_employees()

    if request.method == 'POST':
        ssn = request.form['ssn'].strip()

        # 1. Connect to DB
        cnxn = pyodbc.connect(DSN)
        cursor = cnxn.cursor()

        # 2. Delete the employee's specializations
        cursor.execute("DELETE FROM manager WHERE ssn = ?", (ssn,))
        cursor.execute("DELETE FROM technician WHERE ssn = ?", (ssn,))
        cursor.execute("DELETE FROM atc WHERE ssn = ?", (ssn,))
        cursor.execute("DELETE FROM expert WHERE ssn = ?", (ssn,))

        # 3. Delete from employee
        cursor.execute("DELETE FROM employee WHERE ssn = ?", (ssn,))
        cnxn.commit()

        # 4. Close connection
        cnxn.close()

        return redirect(url_for('employee_delete'))

    return render_template('employees.html', employees=employees, action='Delete')


@app.route('/expertise', methods=['GET', 'POST'])
@login_required
def expertise():

    if request.method == 'POST':
        ssn = request.form.get('ssn','').strip()
    model_number = request.form.get('model_number', '').strip()
    action = request.form.get('action','').strip()

    # 1. Connect to DB
    cnxn = pyodbc.connect(DSN)
    cursor = cnxn.cursor()

    # 2. If POST, add or remove expertise from 'expert' table
    if action == "add":
        cursor.execute("INSERT INTO expert (ssn, model_number) VALUES (?, ?)", (ssn, model_number))
    elif action == "remove":
        cursor.execute("DELETE FROM expert WHERE ssn = ? AND model_number = ?", (ssn, model_number))

    cnxn.commit()
    cnxn.close()

    # Get technicians and models for dropdowns
    cnxn = pyodbc.connect(DSN)
    cursor = cnxn.cursor()

    cursor.execute('''
        SELECT t.ssn, e.name, m.model_number
        FROM technician t
        JOIN employee e ON t.ssn = e.ssn
        LEFT JOIN expert m ON t.ssn = m.ssn
    ''')
    technicians = cursor.fetchall()

    cursor.execute("SELECT model_number FROM airplane_model")
    models = cursor.fetchall()

    # 4. Close connection
    cnxn.close()

    formatted_technicians = [
        (tech[0], tech[1], tech[2] if tech[2] else '') for tech in technicians
    ]

    # END-STUDENT-CODE

    return render_template('expertise.html', technicians=formatted_technicians, models=models)


@app.route('/update_salaries', methods=['GET', 'POST'])
@login_required
def update_salaries():
    if request.method == 'POST':
        percentage = parse_float(request.form['percentage'].strip())
        if percentage is not None:
            percentage = round(percentage, 2) / 100

            # START-STUDENT-CODE
            # 1. Connect to DB
            # 2. Increase salary by 'percentage' for all employees
            # 3. Close connection

            # END-STUDENT-CODE

        return redirect(url_for('index'))

    return render_template('salary.html')


@app.route('/models/add', methods=['GET', 'POST'])
@login_required
def model_add():
    if request.method == 'POST':
        model_number = request.form['model_number'].strip()
        capacity = parse_int(request.form['capacity'].strip())
        weight = parse_float(request.form['weight'].strip())

        # 1. Connect to DB
        cnxn = pyodbc.connect(DSN)
        cursor = cnxn.cursor()

        # Check if model exists first
        cursor.execute("SELECT * FROM airplane_model WHERE model_number = ?", (model_number,))
        exists = cursor.fetchone()

        if not exists:
            cursor.execute(
                "INSERT INTO airplane_model (model_number, capacity, weight) VALUES (?, ?, ?)",
                (model_number, capacity, weight)
            )
            cnxn.commit()

        # 3. Close connection
        cnxn.close()

    return render_template('models.html', models=get_airplane_models(), action="Add")


@app.route('/models/update', methods=['GET', 'POST'])
@login_required
def model_update():
    if request.method == 'POST':
        model_number = request.form['model_number'].strip()
        capacity = request.form['capacity'].strip() or None
        weight = request.form['weight'].strip() or None

        # Parse inputs safely
        capacity = parse_int(capacity) if capacity else None
        weight = parse_float(weight) if weight else None

        # 1. Connect to DB
        cnxn = pyodbc.connect(DSN)
        cursor = cnxn.cursor()

        # Check if the model exists
        cursor.execute("SELECT * FROM airplane_model WHERE model_number = ?", (model_number,))
        existing = cursor.fetchone()

        if existing:
            # Only update the fields that are non-empty
            if capacity is not None:
                cursor.execute("UPDATE airplane_model SET capacity = ? WHERE model_number = ?", (capacity, model_number))
            if weight is not None:
                cursor.execute("UPDATE airplane_model SET weight = ? WHERE model_number = ?", (weight, model_number))
            cnxn.commit()

        cnxn.close()

    return render_template('models.html', models=get_airplane_models(), action="Update")


@app.route('/models/delete', methods=['GET', 'POST'])
@login_required
def model_delete():
    if request.method == 'POST':
        model_number = request.form['model_number'].strip()

        # 1. Connect to DB
        cnxn = pyodbc.connect(DSN)
        cursor = cnxn.cursor()

        # 2. Delete the model if it exists
        cursor.execute("SELECT * FROM airplane WHERE model_number = ?", (model_number,))
        in_use = cursor.fetchone()

        if not in_use:
            cursor.execute("DELETE FROM airplane_model WHERE model_number = ?", (model_number,))
            cnxn.commit()

        # 3. Close connection
        cnxn.close()

    return render_template('models.html', models=get_airplane_models(), action="Delete")


@app.route('/airplanes/add', methods=['GET', 'POST'])
@login_required
def airplane_add():
    # START-STUDENT-CODE
    # 1. Connect to DB
    # 2. If POST, check if the airplane reg_number exists, otherwise insert
    # 3. Retrieve list of airplane_model for dropdown
    # 3. Close connection

    if request.method == 'POST':
        reg_number = request.form['reg_number'].strip()
        model_number = request.form['model_number'].strip()

    models = []

    # END-STUDENT-CODE

    return render_template('airplanes.html', airplanes=get_airplanes(), models=models, action="Add")


@app.route('/airplanes/update', methods=['GET', 'POST'])
@login_required
def airplane_update():
    if request.method == 'POST':
        reg_number = request.form.get('reg_number', '').strip()
        model_number = request.form.get('model_number', '').strip()

        cnxn = pyodbc.connect(DSN)
        cursor = cnxn.cursor()

        # Check if the airplane exists
        cursor.execute("SELECT * FROM airplane WHERE reg_number = ?", (reg_number,))
        existing = cursor.fetchone()

        if existing:
            # Update the model number
            cursor.execute(
                "UPDATE airplane SET model_number = ? WHERE reg_number = ?",
                (model_number, reg_number)
            )
            cnxn.commit()

        cnxn.close()

    models = get_airplane_models()
    return render_template('airplanes.html', airplanes=get_airplanes(), models=models, action="Update")

@app.route('/airplanes/delete', methods=['GET', 'POST'])
@login_required
def airplane_delete():
    # START-STUDENT-CODE
    # 1. Connect to DB
    # 2. If airplane exists, delete it
    # 3. Close connection

    if request.method == 'POST':
        reg_number = request.form['reg_number'].strip()

    # END-STUDENT-CODE

    return render_template('airplanes.html', airplanes=get_airplanes(), action="Delete")


@app.route('/faa_tests/add', methods=['GET', 'POST'])
@login_required
def faa_test_add():
    # START-STUDENT-CODE
    # 1. Connect to DB
    # 2. If test_number doesn't exist, insert new FAA test
    # 3. Close connection

    if request.method == 'POST':
        test_number = request.form['test_number'].strip()
        name = request.form['name'].strip()
        max_score = parse_float(request.form['max_score'].strip())

    # END-STUDENT-CODE

    return render_template('faa_tests.html', faa_tests=get_faa_tests(), action="Add")


@app.route('/faa_tests/update', methods=['GET', 'POST'])
@login_required
def faa_test_update():
    # START-STUDENT-CODE
    # 1. Connect to DB
    # 2. If test_number exists, update name/max_score
    # 3. Close connection

    if request.method == 'POST':
        test_number = request.form['test_number'].strip()
        name = request.form['name'].strip() or None
        max_score = request.form['max_score'].strip() or None
        max_score = parse_float(max_score) if max_score else None

    # END-STUDENT-CODE

    return render_template('faa_tests.html', faa_tests=get_faa_tests(), action="Update")


@app.route('/faa_tests/delete', methods=['GET', 'POST'])
@login_required
def faa_test_delete():
    # START-STUDENT-CODE
    # 1. Connect to DB
    # 2. If test_number exists, delete from faa_test
    # 3. Close connection

    if request.method == 'POST':
        test_number = request.form['test_number'].strip()

    # END-STUDENT-CODE

    return render_template('faa_tests.html', faa_tests=get_faa_tests(), action="Delete")

@app.route('/test_connection')
def test_connection():
    try:
        cnxn = pyodbc.connect(DSN)
        cursor = cnxn.cursor()
        cursor.execute("SELECT COUNT(*) FROM employee;")
        count = cursor.fetchone()[0]
        cnxn.close()
        return f"Connection successful. {count} employees in the database."
    except Exception as e:
        return f"Connection failed: {e}"

@app.route('/tests')
@login_required
def tests():
    return render_template('tests.html', tests=get_airworthiness_tests())


if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1', port=5000)
