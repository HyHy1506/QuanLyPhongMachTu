from flask import  render_template, request, redirect, url_for
from phongmachapp import app
import dao
import hashlib

@app.route('/')
def index():
    return render_template("index.html")

@app.route('/login', methods=['GET', 'POST'])
def login():

    if request.method.__eq__('POST'):
        username = request.form['username'].strip()
        password = request.form['password'].strip()
        user = dao.check_user(username, password)
        if user:
            return redirect('/doctor')

    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    password = str(hashlib.md5("123".encode('utf-8')).hexdigest())

    return render_template('signup.html')

@app.route('/doctor', methods=['GET', 'POST'])
def doctor():
    return render_template('doctor.html')

@app.route('/nurse', methods=['GET', 'POST'])
def nurse():
    return render_template('nurse.html')

@app.route('/patient', methods=['GET', 'POST'])
def patient():
    return render_template('patient.html')

if __name__ == '__main__':
    with app.app_context():
        app.run(debug=True)