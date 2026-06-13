import os
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv
from flask import Flask, render_template, request, redirect, url_for
from flask_login import LoginManager, login_user, logout_user, login_required, current_user, UserMixin 
from werkzeug.security import generate_password_hash, check_password_hash

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY")
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
    user = db.execute("SELECT * FROM users WHERE id = %s", (user_id,)).fetchone()
    if user:
        return User(user["id"], user["username"], user["email"], user["bars"])
    return None 

class DBWrapper:
    def __init__(self):
        self.conn = psycopg2.connect(os.getenv("DATABASE_URL"))
        
    def execute(self, query, vars=None):
        # RealDictCursor makes Postgres return rows as dictionaries
        cursor = self.conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute(query, vars)
        return cursor
        
    def commit(self):
        self.conn.commit()

def get_db():
    return DBWrapper()

@app.route("/")
def market():
    db = get_db()
    query = """
        SELECT DISTINCT ON (artists.id) 
            artists.name, 
            artist_snapshots.listeners, 
            artist_snapshots.playcount, 
            artist_snapshots.date, 
            artists.tier 
        FROM artist_snapshots 
        JOIN artists ON artists.id = artist_snapshots.artist_id 
        ORDER BY artists.id, artist_snapshots.date DESC
    """
    artists = db.execute(query).fetchall()
    return render_template("market.html", artists=artists) 

@app.route("/artist/<name>")
def artist(name):
    query = "SELECT * FROM artist_snapshots JOIN artists ON artists.id = artist_snapshots.artist_id WHERE artists.name = %s ORDER BY artist_snapshots.date DESC LIMIT 1"
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
        cursor = db.execute("INSERT INTO users (username, email, hashed_password) VALUES (%s, %s, %s) RETURNING id", (username, email, hashed_password)) 
        db.commit()
        user_id = cursor.fetchone()["id"]
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

        user_row = db.execute("SELECT * FROM users WHERE username = %s", (username,)).fetchone()

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

@app.route("/buy", methods=["POST"])
@login_required
def buy():
    db = get_db()
    artist_id = request.form.get('artist_id')
    shares = int(request.form.get('shares'))
    artist_name = request.form.get('name')
    query = "SELECT artist_id, listeners FROM artist_snapshots WHERE artist_id = %s"

    artist_row = db.execute(query, (artist_id,)).fetchone()
    listeners = artist_row["listeners"]
    price_per_share = listeners / 10000
    total_cost = price_per_share * shares 

    if current_user.bars >= total_cost:
        db.execute("UPDATE users SET bars = %s WHERE id = %s", (current_user.bars - total_cost, current_user.id))
    else:
        return "Not a sufficient amount of bars"

    insert_query = "INSERT INTO holdings (user_id, artist_id, shares, price_per_share, bought_at) VALUES (%s, %s, %s, %s, CURRENT_DATE)"
    db.execute(insert_query, (current_user.id, artist_id, shares, price_per_share))
    db.commit()
    return redirect(url_for("artist", name=artist_name))

@app.route("/sell", methods=["POST"])
@login_required
def sell():
    db = get_db()
    artist_id = request.form.get('artist_id')
    artist_name = request.form.get('name')
    shares_to_sell = int(request.form.get('shares'))

    # Get current price from the latest snapshot (same formula as buy)
    snapshot = db.execute(
        "SELECT listeners FROM artist_snapshots WHERE artist_id = %s ORDER BY date DESC LIMIT 1",
        (artist_id,)
    ).fetchone()
    current_price = snapshot["listeners"] / 10000

    # Get total shares the user owns for this artist
    holdings = db.execute(
        "SELECT id, shares, price_per_share FROM holdings WHERE user_id = %s AND artist_id = %s",
        (current_user.id, artist_id)
    ).fetchall()
    total_shares_owned = sum(row["shares"] for row in holdings)

    if shares_to_sell <= 0 or shares_to_sell > total_shares_owned:
        return "Invalid number of shares to sell"

    # Credit the user with current market value of the sold shares
    payout = current_price * shares_to_sell
    db.execute(
        "UPDATE users SET bars = bars + %s WHERE id = %s",
        (payout, current_user.id)
    )

    # Delete all holdings rows for this artist, then re-insert remaining shares
    # (preserving original avg price_per_share weighted average)
    remaining = total_shares_owned - shares_to_sell
    db.execute(
        "DELETE FROM holdings WHERE user_id = %s AND artist_id = %s",
        (current_user.id, artist_id)
    )
    if remaining > 0:
        # Compute weighted average buy price from original holdings
        total_cost = sum(row["shares"] * row["price_per_share"] for row in holdings)
        avg_price = total_cost / total_shares_owned
        db.execute(
            "INSERT INTO holdings (user_id, artist_id, shares, price_per_share, bought_at) VALUES (%s, %s, %s, %s, CURRENT_DATE)",
            (current_user.id, artist_id, remaining, avg_price)
        )

    db.commit()
    return redirect(url_for("artist", name=artist_name))



@app.route("/portfolio")
@login_required
def portfolio():
    db = get_db()
    
    query = """
        SELECT 
            artists.name,
            holdings.shares,
            holdings.price_per_share,
            holdings.bought_at,
            artist_snapshots.listeners
        FROM holdings
        JOIN artists ON artists.id = holdings.artist_id
        JOIN artist_snapshots ON artist_snapshots.artist_id = holdings.artist_id
        WHERE holdings.user_id = %s
          AND artist_snapshots.date = (SELECT MAX(date) FROM artist_snapshots WHERE artist_id = artists.id)
    """
    
    # You have to execute the query against the database and save it to the `raw_holdings` variable
    raw_holdings = db.execute(query, (current_user.id,)).fetchall()
    
    # Now we loop through the raw data to calculate the values in Python
    holdings = []
    for row in raw_holdings:
        holding = dict(row)

        current_price = holding['listeners'] / 10000
        holding['current_price'] = current_price
        holding['current_value'] = current_price * holding['shares']
        holding['gain_loss'] = (current_price - holding['price_per_share']) * holding['shares']

        holdings.append(holding)

    # Finally, pass the calculated `holdings` list to the template
    return render_template("portfolio.html", holdings=holdings)

if __name__ == "__main__":
    app.run(debug=True)