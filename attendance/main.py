from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3
from functools import wraps

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Database initialization
def init_db():
    conn = sqlite3.connect('attendance.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS attendance
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, rfid TEXT)''')
    conn.commit()
    conn.close()

# Decorator for login required routes
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'logged_in' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# Login route
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        if request.form['username'] == 'admin' and request.form['password'] == 'admin':
            session['logged_in'] = True
            return redirect(url_for('dashboard'))
        else:
            return render_template('login.html', error='Invalid credentials')
    return render_template('login.html')

# Logout route
@app.route('/logout')
@login_required
def logout():
    session.pop('logged_in', None)
    return redirect(url_for('login'))

# Dashboard route
@app.route('/dashboard')
@login_required
def dashboard():
    conn = sqlite3.connect('attendance.db')
    c = conn.cursor()
    c.execute("SELECT * FROM attendance ORDER BY timestamp DESC")
    records = c.fetchall()
    conn.close()
    return render_template('dashboard.html', records=records)

# Endpoint to receive RFID data from NodeMCU
@app.route('/post-attendance', methods=['POST'])
def post_attendance():
    if request.method == 'POST':
        rfid = request.form['rfid']
        conn = sqlite3.connect('attendance.db')
        c = conn.cursor()
        c.execute("INSERT INTO attendance (rfid) VALUES (?)", (rfid,))
        conn.commit()
        conn.close()
        return 'Success'
    return 'Failure'

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
