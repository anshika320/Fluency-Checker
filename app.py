from flask import Flask, render_template, request, jsonify, redirect, url_for, session, flash
import speech_recognition as sr
import time
from flask_mysqldb import MySQL, MySQLdb

app = Flask(__name__)

app.secret_key = "root_anshi"
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'anshi'
app.config['MYSQL_PASSWORD'] = 'root_anshi'
app.config['MYSQL_DB'] = 'project'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'

mysql = MySQL(app)


@app.route('/', methods=["GET", "POST"])
def login():
    if request.method == 'POST':
        email = request.form['email']
        pwd = request.form['pwd']

        cursor = mysql.connection.cursor()
        cursor.execute("SELECT * FROM user_details WHERE emailid = %s and pwd= %s", (email, pwd))
        user = cursor.fetchone()
        cursor.close()

        if user is not None and user['pwd'] == pwd:
            session['logged_in'] = True
            session['email'] = email
            return redirect(url_for('search'))
        else:
           flash("Invalid username or password. Please try again.", "error")

    return render_template("login.html")

@app.route('/add_fluency', methods=['POST'])
def add_fluency():
    data = request.json
    email = data['email']
    fluency = data['fluency']
    cursor = mysql.connection.cursor()
    
    # Check if the user exists
    cursor.execute("SELECT * FROM user_details WHERE emailid = %s", (email,))
    user = cursor.fetchone()

    if user:
        # Check the number of uses
        cursor.execute("SELECT f1, f2, f3 FROM user_details WHERE emailid = %s", (email,))
        fluency_uses = cursor.fetchone()
        if fluency_uses[0] is None:
            cursor.execute("UPDATE user_details SET f1 = %s WHERE emailid = %s", (fluency, email))
        elif fluency_uses[1] is None:
            cursor.execute("UPDATE user_details SET f2 = %s WHERE emailid = %s", (fluency, email))
        elif fluency_uses[2] is None:
            cursor.execute("UPDATE user_details SET f3 = %s WHERE emailid = %s", (fluency, email))
        else:
            return jsonify({"message": "You have reached the maximum limit of fluency uses."}), 400

        mysql.connection.commit()
        cursor.close()
        return jsonify({"message": "Fluency added successfully."}), 200
    else:
        return jsonify({"message": "User does not exist."}), 404

@app.route('/home')
def index():
    return render_template("index.html")
@app.route('/search')
def search():
    return render_template("search.html")

@app.route('/pwd_rec', methods=['GET', 'POST'])
def pwd_rec():
    if request.method == 'POST':
        email = request.form.get('email')
        security_answer = request.form.get('security_answer')
        new_password = request.form.get('password')

        if not new_password:
            flash('Please enter a new password.')
            return render_template('pwd_rec.html')
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT * FROM user_details WHERE emailid = %s and security_details=%s ", (email,security_answer))
        user = cursor.fetchone()

        if user is not None:
            if user['security_details'] == security_answer:
                cursor.execute("update user_details set pwd= %s where emailid= %s", (new_password, email))
                flash('Password updated successfully. You can now log in with your new password.')
                cursor.close()
                return redirect(url_for('login'))
            else:
                flash('Email not found. Please check the entered email address.')
                cursor.close()
        else:
            
            flash('Security answer is incorrect. Please check your credentials.')
            cursor.close()

    return render_template('pwd_rec.html')

@app.route('/logout')
def logout():
    session.pop('email', None)
    return redirect('login.html')

@app.route('/signup', methods=["GET", "POST"])
def signup():
    if request.method == 'GET':
        return render_template("signup.html")
    else:
        email = request.form['email']
        psw = request.form['psw']
        psw_confirm = request.form['psw1']
        no = request.form['number']
        na = request.form['name']
        security_answer = request.form['security_answer']
        if len(no) != 10 or not no.isdigit():
            flash("Phone number must be of 10 digits.","error")
            return redirect(url_for('signup'))
        if psw != psw_confirm:
            flash("Passwords do not match.","error")
            return redirect(url_for('signup'))
        cur = mysql.connection.cursor()
        cur.execute("insert into user_details Values(%s,%s,%s,%s,%s)", (email, psw, na, no,security_answer))
        mysql.connection.commit()
        session['email'] = request.form['email']
        session['psw'] = request.form['psw']
        return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
