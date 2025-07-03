from flask import Flask, render_template, request, redirect, url_for
import os
from datetime import datetime
import urllib.request, urllib.parse, json
import mysql.connector as msc

app = Flask(__name__, template_folder=os.path.dirname(os.path.abspath(__file__)))

# Connect to MySQL
c = msc.connect(host='localhost', user='root', passwd='1234', database='movies')
cu = c.cursor(dictionary=True)
@app.route("/", methods=["GET", "POST"])
def index():
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
            return render_template("index.html", output=output, ans=ans, year=year, rat=rating, ov=overview, poster_url=poster_url, imdb_url=imdb_url)

        if not data["results"]:
            ans = "Movie not found."
            return render_template("index.html", output=output, ans=ans, year=year, rat=rating, ov=overview, poster_url=poster_url, imdb_url=imdb_url)

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

        insert_query = """
            INSERT INTO movies (tmdb_id, title, year, genre, rating, overview, date_added)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
        values = (tmdb_id, title_db, year, genre, rating, overview, date_added)

        try:
            cu.execute(insert_query, values)
            c.commit()
            ans = "Movie inserted successfully!"
        except msc.errors.IntegrityError:
            ans = "This movie is already added in the database."

    return render_template("index.html", output=output, ans=ans, year=year, rat=rating, ov=overview, poster_url=poster_url, imdb_url=imdb_url)

@app.route("/view", methods=["GET"])
def view_movies():
    cu.execute("SELECT * FROM movies")
    all_movies = cu.fetchall()
    return render_template("view.html", movies=all_movies)

@app.route("/remove/<int:tmdb_id>", methods=["POST"])
def remove_movie(tmdb_id):
    cu.execute("DELETE FROM movies WHERE tmdb_id = %s", (tmdb_id,))
    c.commit()
    return redirect(url_for('view_movies'))

if __name__ == "__main__":
    app.run(debug=True)
