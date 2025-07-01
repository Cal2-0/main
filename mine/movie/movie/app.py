from flask import Flask, render_template, request, redirect, url_for
import urllib.request, urllib.parse, json
import mysql.connector as msc

app = Flask(__name__)

def get_db():
    return msc.connect(host='localhost', user='root', passwd='1234', database='movies')

@app.route('/', methods=['GET'])
def home():
    db = get_db()
    cu = db.cursor(dictionary=True)
    cu.execute("SELECT * FROM movies")
    movies = cu.fetchall()
    cu.close()
    db.close()
    return render_template('index.html', movies=movies, message=None, error=None, last_title=None)

@app.route('/add', methods=['POST'])
def add_movie():
    entered_title = request.form['title']
    query = urllib.parse.quote(entered_title)
    url = f"https://api.themoviedb.org/3/search/movie?api_key=d74a624410ea1d50ef3545bfb815acf5&query={query}"
    data = json.load(urllib.request.urlopen(url))
    db = get_db()
    cu = db.cursor(dictionary=True)
    cu.execute("SELECT * FROM movies")
    movies = cu.fetchall()
    message = None
    error = None
    last_title = entered_title
    if not data["results"]:
        error = f"Movie not found for: {entered_title}"
    else:
        movie = data["results"][0]
        id = movie["id"]
        details = json.load(urllib.request.urlopen(
            f"https://api.themoviedb.org/3/movie/{id}?api_key=d74a624410ea1d50ef3545bfb815acf5"
        ))
        tmdb_id = details["id"]
        title_db = details["title"]
        year = details.get("release_date", None)
        year = year[:4] if year else None
        genre = details["genres"][0]["name"] if details.get("genres") else None
        rating = round(details.get("vote_average", 0.0), 1)
        overview = details.get("overview", None)
        date_added = "2025-07-01"  # static for now
        insert_query = """
            INSERT INTO movies (tmdb_id, title, year, genre, rating, overview, date_added)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
        values = (tmdb_id, title_db, year, genre, rating, overview, date_added)
        try:
            cu2 = db.cursor()
            cu2.execute(insert_query, values)
            db.commit()
            cu2.close()
            message = f"Movie added: {title_db}"
            last_title = title_db
        except msc.errors.IntegrityError:
            error = f"This movie is already in the database: {title_db}"
            last_title = title_db
        except Exception as e:
            error = f"Error: {e}"
    cu.close()
    db.close()
    return render_template('index.html', movies=movies, message=message, error=error, last_title=last_title)

@app.route('/remove/<int:tmdb_id>', methods=['POST'])
def remove_movie(tmdb_id):
    db = get_db()
    cu = db.cursor()
    cu.execute("DELETE FROM movies WHERE tmdb_id = %s", (tmdb_id,))
    db.commit()
    cu.close()
    db.close()
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True) 