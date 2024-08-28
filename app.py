from flask import Flask, render_template, request, redirect, url_for, session
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3

# Create instance of Flask class
app = Flask(__name__)

# Secret key for session management
app.secret_key = 'secret_key'

# Connect to SQLite database
def connect_db():
    # Connect to users.db database
    conn = sqlite3.connect('users.db')
    return conn

# Create users table in database
def create_table():
    # Connect to database
    conn = connect_db()
    c = conn.cursor()
    # Create table if it does not exist
    c.execute('''CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, username TEXT, email TEXT, password TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS games ("id" INTEGER NOT NULL, "gamename" TEXT NULL, "type" TEXT NULL, "datelastplayed" TEXT NULL DEFAULT NULL, "noofacheivements" INTEGER NULL, "isstarred" CHAR(50) NULL DEFAULT NULL, "userid" INTEGER NULL, PRIMARY KEY ("id"), CONSTRAINT "0" FOREIGN KEY ("userid") REFERENCES "user" ("id") ON UPDATE NO ACTION ON DELETE NO ACTION);''')
    # Commit changes and close connection
    conn.commit()
    c.close()
    conn.close()

# Create table when the script runs
create_table()


@app.route('/')
def home():
    return render_template('index.html')


@app.route('/members')
def members():
    if 'username' in session:
        conn = connect_db()
        c = conn.cursor()
        c.execute("SELECT * FROM games WHERE userid = ?", (session['userid'],))
        gamelist = c.fetchall()
        c.close()
        conn.close()
        return render_template('members.html', username=session['username'], gamelist=gamelist)
    else:
        return redirect(url_for('login'))

# Signup route
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    # Handle POST request
    if request.method == 'POST':
        # Get form data
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']

        # Hash password
        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')

        # Insert user into database
        conn = connect_db()
        c = conn.cursor()
        c.execute("INSERT INTO users (username, email, password) VALUES (?, ?, ?)", (username, email, hashed_password))
        conn.commit()
        c.close()
        conn.close()

        # Redirect to login page
        return redirect(url_for('login'))

    # Handle GET request
    return render_template('signup.html')

# Login route
@app.route('/login', methods=['GET', 'POST'])
def login():
    # Handle POST request
    if request.method == 'POST':
        # Get form data
        username = request.form['username']
        password = request.form['password']

        # Fetch user from database
        conn = connect_db()
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE username = ?", (username,))
        user = c.fetchone()
        c.close()
        conn.close()

        if user:
            # Compare hashed password
            if check_password_hash(user[3], password):
                # Set session variables
                session['logged_in'] = True
                session['username'] = user[1]
                session['userid'] = user[0]
                # Redirect to members area
                return redirect(url_for('members'))
            else:
                # Render login page with error message
                return render_template('login.html', error='Invalid username or password')

    # Handle GET request
    return render_template('login.html')

@app.route('/add', methods = ['POST'])
def add():
    con = connect_db()
    cur = con.cursor()
    gamename = request.form['gamename']
    gametype = request.form['gametype']
    userid = session['userid']
    cur.execute('INSERT INTO games (gamename, type, userid) VALUES (?,?,?)', (gamename, gametype, userid))
    con.commit()
    con.close()
    return redirect(url_for('members'))

@app.route('/edit/<int:id>')
def edit(id):
    con = connect_db()
    cur = con.cursor()
    cur.execute('SELECT * FROM games WHERE id = ?', (id,))
    pet = cur.fetchone()
    con.close()
    return render_template('edit.html', pet = pet)

@app.route('/update/<int:id>', methods = ['POST'])
def update(id):
    con = connect_db()
    cur = con.cursor()
    gamename = request.form['gamename']
    gametype = request.form['gametype']
    cur.execute('UPDATE games SET gamename = ?, type = ? WHERE id = ?', (gamename, gametype, id))
    con.commit()
    con.close()
    return redirect(url_for('members'))

@app.route('/delete/<int:id>')
def delete(id):
    con = connect_db()
    cur = con.cursor()
    cur.execute('DELETE FROM games WHERE id = ?', (id,))
    con.commit()
    con.close()
    return redirect(url_for('members'))

# Logout route
@app.route('/logout')
def logout():
    # Remove session variables
    session.pop('logged_in', None)
    session.pop('username', None)
    session.pop('userid', None)
    # Redirect to home page
    return redirect(url_for('home'))

#Run the app
if __name__ == '__main__':
    app.run(port=3000)

