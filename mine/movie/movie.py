from flask import Flask, render_template, request, redirect, url_for, session, flash,Blueprint
import os
from datetime import datetime
import urllib.request, urllib.parse, json
import mysql.connector as msc
from werkzeug.security import generate_password_hash, check_password_hash
import secrets

movie_bp = Blueprint('movie',__name__)
movie_bp.secret_key = secrets.token_hex(16)  # Generate a random secret key

# Database connections
def get_movie_db_connection():
    return msc.connect(host='localhost', user='root', passwd='1234', database='movies')

def get_users_db_connection():
    return msc.connect(host='localhost', user='root', passwd='1234', database='users')

# Initialize database tables
def init_databases():
    # Initialize movie database (for guests)
    movie_conn = get_movie_db_connection()
    movie_cursor = movie_conn.cursor()
    
    # Create movies table for guests if it doesn't exist
    movie_cursor.execute("""
        CREATE TABLE IF NOT EXISTS movies (
            id INT AUTO_INCREMENT PRIMARY KEY,
            tmdb_id INT NOT NULL,
            title VARCHAR(255) NOT NULL,
            year VARCHAR(4),
            genre VARCHAR(100),
            rating DECIMAL(3,1),
            overview TEXT,
            date_added DATE,
            poster_url VARCHAR(500),
            imdb_id VARCHAR(20),
            UNIQUE KEY unique_movie (tmdb_id)
        )
    """)
    
    movie_conn.commit()
    movie_cursor.close()
    movie_conn.close()
    
    # Initialize users database
    users_conn = get_users_db_connection()
    users_cursor = users_conn.cursor()
    
    # Create users table if it doesn't exist
    users_cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INT AUTO_INCREMENT PRIMARY KEY,
            username VARCHAR(50) UNIQUE NOT NULL,
            email VARCHAR(100) UNIQUE NOT NULL,
            password_hash VARCHAR(255) NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    users_conn.commit()
    users_cursor.close()
    users_conn.close()

# Initialize databases on startup
init_databases()

def create_user_movies_table(username):
    """Create a separate movies table for a specific user"""
    conn = get_users_db_connection()
    cursor = conn.cursor()
    
    table_name = f"{username}_movies"
    cursor.execute(f"""
        CREATE TABLE IF NOT EXISTS {table_name} (
            id INT AUTO_INCREMENT PRIMARY KEY,
            tmdb_id INT NOT NULL,
            title VARCHAR(255) NOT NULL,
            year VARCHAR(4),
            genre VARCHAR(100),
            rating DECIMAL(3,1),
            overview TEXT,
            date_added DATE,
            poster_url VARCHAR(500),
            imdb_id VARCHAR(20),
            UNIQUE KEY unique_movie (tmdb_id)
        )
    """)
    
    conn.commit()
    cursor.close()
    conn.close()

@movie_bp.route("/movie", methods=["GET", "POST"])
def movie():
    output = ""
    ans = ""
    year = ""
    rating = ""
    overview = ""
    poster_url = None
    imdb_url = None

    if request.method == "POST":
        title = request.form.get("inputText", "")
        query = urllib.parse.quote(title)
        url = f"https://api.themoviedb.org/3/search/movie?api_key=d74a624410ea1d50ef3545bfb815acf5&query={query}"
        
        try:
            data = json.load(urllib.request.urlopen(url))
        except Exception as e:
            ans = f"Error fetching data from TMDB API: {e}"
            return render_template("movie.html", output=output, ans=ans, year=year, rat=rating, ov=overview, poster_url=poster_url, imdb_url=imdb_url)

        if not data["results"]:
            ans = "Movie not found."
            return render_template("movie.html", output=output, ans=ans, year=year, rat=rating, ov=overview, poster_url=poster_url, imdb_url=imdb_url)

        movie = data["results"][0]
        id = movie["id"]

        details_url = f"https://api.themoviedb.org/3/movie/{id}?api_key=d74a624410ea1d50ef3545bfb815acf5"
        details = json.load(urllib.request.urlopen(details_url))

        tmdb_id = details["id"]
        title_db = details["title"]
        year = details.get("release_date", None)
        year = year[:4] if year else "Unknown"
        genre = details["genres"][0]["name"] if details.get("genres") else "Unknown"
        rating = round(details.get("vote_average", 0.0), 1)
        overview = details.get("overview", "No overview")
        date_added = datetime.now().strftime("%Y-%m-%d")
        output = title_db

        # Get poster and imdb url
        poster_path = details.get("poster_path")
        poster_url = f"https://image.tmdb.org/t/p/w500{poster_path}" if poster_path else None
        imdb_id = details.get("imdb_id")
        imdb_url = f"https://www.imdb.com/title/{imdb_id}" if imdb_id else None

        # Insert movie based on user status
        if 'user_id' in session:
            # Logged in user - insert into their personal table
            username = session['username']
            create_user_movies_table(username)
            
            conn = get_users_db_connection()
            cursor = conn.cursor()
            
            table_name = f"{username}_movies"
            insert_query = f"""
                INSERT INTO {table_name} (tmdb_id, title, year, genre, rating, overview, date_added, poster_url, imdb_id)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            values = (tmdb_id, title_db, year, genre, rating, overview, date_added, poster_url, imdb_id)

            try:
                cursor.execute(insert_query, values)
                conn.commit()
                ans = "Movie inserted successfully to your collection!"
            except msc.errors.IntegrityError:
                ans = "This movie is already in your collection."
            finally:
                cursor.close()
                conn.close()
        else:
            # Guest user - insert into shared movie database
            conn = get_movie_db_connection()
            cursor = conn.cursor()
            
            insert_query = """
                INSERT INTO movies (tmdb_id, title, year, genre, rating, overview, date_added, poster_url, imdb_id)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            values = (tmdb_id, title_db, year, genre, rating, overview, date_added, poster_url, imdb_id)

            try:
                cursor.execute(insert_query, values)
                conn.commit()
                ans = "Movie inserted successfully to guest collection!"
            except msc.errors.IntegrityError:
                ans = "This movie is already in the guest collection."
            finally:
                cursor.close()
                conn.close()

    return render_template("movie.html", output=output, ans=ans, year=year, rat=rating, ov=overview, poster_url=poster_url, imdb_url=imdb_url)

@movie_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        
        conn = get_users_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
        user = cursor.fetchone()

        cursor.close()
        conn.close()

        if user and check_password_hash(user['password_hash'], password):
            session['user_id'] = user['id']
            session['username'] = user['username']

            movie_conn = get_movie_db_connection()
            movie_cursor = movie_conn.cursor()

            movie_cursor.execute("INSERT INTO user_logs (username, status) VALUES (%s, %s)", (username, 'logged in'))
            movie_conn.commit()

            movie_cursor.close()
            movie_conn.close()

            return redirect(url_for('movie'))
        else:
            flash('Invalid username or password', 'error')
    
    return render_template("login.html")


@movie_bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username")
        email = request.form.get("email")
        password = request.form.get("password")
        confirm_password = request.form.get("confirm_password")
        
        if password != confirm_password:
            flash('Passwords do not match', 'error')
            return render_template("register.html")
        
        if len(password) < 6:
            flash('Password must be at least 6 characters long', 'error')
            return render_template("register.html")
        
        conn = get_users_db_connection()
        cursor = conn.cursor()
        
        try:
            password_hash = generate_password_hash(password)
            cursor.execute("INSERT INTO users (username, email, password_hash) VALUES (%s, %s, %s)", 
                         (username, email, password_hash))
            conn.commit()
            
            # Create user's personal movies table
            create_user_movies_table(username)
            
            flash('Registration successful! Please login.', 'success')
            return redirect(url_for('login'))
        except msc.errors.IntegrityError:
            flash('Username or email already exists', 'error')
        finally:
            cursor.close()
            conn.close()
    
    return render_template("register.html")
@movie_bp.route("/logout")
def logout():
    username = session.get('username')

    if username:
        movie_conn = get_movie_db_connection()
        movie_cursor = movie_conn.cursor()

        movie_cursor.execute("INSERT INTO user_logs (username, status) VALUES (%s, %s)", (username, 'logged out'))
        movie_conn.commit()

        movie_cursor.close()
        movie_conn.close()

    session.clear()
    return redirect(url_for('movie'))

@movie_bp.route("/view", methods=["GET"])
def view_movies():
    if 'user_id' in session:
        # Logged in user - show their personal collection
        username = session['username']
        conn = get_users_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        table_name = f"{username}_movies"
        cursor.execute(f"SELECT * FROM {table_name} ORDER BY date_added DESC")
        all_movies = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        return render_template("view.html", movies=all_movies, is_guest=False)
    else:
        # Guest user - show shared collection
        conn = get_movie_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        cursor.execute("SELECT * FROM movies ORDER BY date_added DESC")
        all_movies = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        return render_template("view.html", movies=all_movies, is_guest=True)

@movie_bp.route("/remove/<int:tmdb_id>", methods=["POST"])
def remove_movie(tmdb_id):
    if 'user_id' in session:
        # Logged in user - remove from their personal table
        username = session['username']
        conn = get_users_db_connection()
        cursor = conn.cursor()
        
        table_name = f"{username}_movies"
        cursor.execute(f"DELETE FROM {table_name} WHERE tmdb_id = %s", (tmdb_id,))
        conn.commit()
        
        cursor.close()
        conn.close()
    else:
        # Guest user - remove from shared collection
        conn = get_movie_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("DELETE FROM movies WHERE tmdb_id = %s", (tmdb_id,))
        conn.commit()
        
        cursor.close()
        conn.close()
    
    return redirect(url_for('view_movies'))

if __name__ == "__main__":
    movie_bp.run(debug=True)
