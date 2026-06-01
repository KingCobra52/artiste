import sqlite3
from flask import Flask, render_template, request, redirect, url_for
from flask_login import LoginManager, login_user, logout_user, login_required, current_user, UserMixin 
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3 

app = Flask(__name__)
app.secret_key = "dev-secret-key"
login_manager = LoginManager(app)
login_manager.login_view = "login"

class User(UserMixin):
    def __init__(self, id, username, email, bars):
        self.id = id
        self.username = username 
        self.email = email
        self.bars = bars 

@login_manager.user_loader
def load_user(user_id):
    db = get_db()
    user = db.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
    if user:
        return User(user["id"], user["username"], user["email"], user["bars"])
    return None 

def get_db():
    conn = sqlite3.connect("artiste.db")
    conn.row_factory = sqlite3.Row 
    return conn 

@app.route("/")
def market():
    db = get_db()
    query = """
        SELECT artists.name, artist_snapshots.listeners, artist_snapshots.playcount, MAX(artist_snapshots.date) as date, artists.tier 
        FROM artist_snapshots 
        JOIN artists ON artists.id = artist_snapshots.artist_id 
        GROUP BY artists.id 
        ORDER BY artists.id
    """
    artists = db.execute(query).fetchall()
    return render_template("market.html", artists=artists) 

@app.route("/artist/<name>")
def artist(name):
    query = "SELECT * FROM artist_snapshots JOIN artists ON artists.id = artist_snapshots.artist_id WHERE artists.name = ? ORDER BY artist_snapshots.date DESC LIMIT 1"
    db = get_db()
    artist = db.execute(query, (name, )).fetchone()
    return render_template("artist.html", artist=artist)

@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        db = get_db()
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        hashed_password = generate_password_hash(password)
        cursor = db.execute("INSERT INTO users (username, email, hashed_password) VALUES (?, ?, ?)", (username, email, hashed_password)) 
        db.commit()
        user_id = cursor.lastrowid
        user = User(user_id, username, email, 10000)
        login_user(user)
        return redirect(url_for("market"))
    return render_template("signup.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        db = get_db()
        username = request.form.get("username")
        password = request.form.get("password")

        user_row = db.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()

        if user_row and check_password_hash(user_row["hashed_password"], password):
            user = User(user_row["id"], user_row["username"], user_row["email"], user_row["bars"])
            login_user(user)

            return redirect(url_for("market"))
        else:
            return "Invalid password or username"
    return render_template("login.html")

@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("market"))
        

if __name__ == "__main__":
    app.run(debug=True)