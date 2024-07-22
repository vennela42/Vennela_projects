from flask import Flask, render_template, request, redirect, url_for
import mysql.connector

app = Flask(__name__)

try:
    connection = mysql.connector.connect(
        host='localhost',
        user='root',
        password='Vennelahari@28',
        db='hospital_db',
    )
    Cursor = connection.cursor()
except mysql.connector.Error as e:
    print('Error connecting to MYSQL:', e)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/service')
def service():
    return render_template('service.html')

@app.route('/doctors')
def doctors():
    return render_template('doctors.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/display', methods=['POST', 'GET'])
def display():
    if request.method == 'POST':
        firstname = request.form['firstname']
        lastname = request.form['lastname']
        email = request.form['email']
        mobile = request.form['mobile']
        sex = request.form['sex']
        appointment_date = request.form['appointment_date']
        message = request.form['message']
        try:
            Cursor.execute("INSERT INTO hospitals(firstname,lastname,email,mobile,sex,appointment_date,message) VALUES (%s, %s,%s,%s,%s,%s,%s)", 
                           (firstname, lastname, email, mobile, sex, appointment_date, message))
            connection.commit()
            return redirect(url_for('dashboard'))
        except mysql.connector.Error as er:
            print('System error', er)
        return redirect(url_for('dashboard'))
    else:
        pass

@app.route("/dashboard")
def dashboard():
    try:
        Cursor.execute("SELECT * FROM hospitals")
        data = Cursor.fetchall()
        return render_template('dashboard.html', data=data)
    except mysql.connector.Error as e:
        print("System error", e)
        return "Error fetching data from the database"

# @app.route('/update/<id>')
# def update(id):
#     Cursor.execute('SELECT * FROM hospitals WHERE id = %s', (id,))
#     data = Cursor.fetchone()
#     return render_template("edit.html", data=data)

@app.route('/delete/<id>')
def delete(id):
    try:
        Cursor.execute('DELETE FROM hospitals WHERE id = %s', (id,))
        connection.commit()  # Commit the deletion
        return redirect(url_for('dashboard'))
    except mysql.connector.Error as e:
        print("System error", e)
        return "Error deleting data from the database"

@app.route('/update/<id>', methods=['GET', 'POST'])
def update(id):
    
        if request.method == 'POST' and 'firstname' in request.form and 'lastname' in request.form and 'email' in request.form and 'number' in request.form and 'sex' in request.form and 'appointment_date' in request.form and 'message' in request.form:
            firstname=request.form['firstname']
            lastname=request.form['lastname']
            mobile = request.form['mobile']
            email = request.form['email']
            sex=request.form['sex']
            appointment_date=request.form['appointment_date']
            message=request.form['message']
            try:
                Cursor.execute('UPDATE hospitals SET firstname = %s, lastname= %s,email=%s,mobile=%s,sex=%s,appointment_date=%s,message=%s WHERE id = %s', (firstname,lastname,email,message,appointment_date,mobile,id,sex,))
                connection.commit()
                msg = 'details updated successfully!'
            except mysql.connector.Error as e:
                print("Error executing SQL query:", e)
                msg = 'An error occurred. Please try again later.'
            return redirect(url_for('dashboard'))
        Cursor.execute('SELECT * FROM hospitals WHERE id = %s', (id,))
        data = Cursor.fetchall()

        if data:

             return render_template('edit.html', data=data)
        else:
            msg = 'record not found!'

if __name__ == '__main__':
 app.run(debug=True)