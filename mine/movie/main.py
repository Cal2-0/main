import urllib.request, urllib.parse, json
import mysql.connector as msc

# Connect to MySQL
c = msc.connect(host='localhost', user='root', passwd='1234', database='movies')
cu = c.cursor(dictionary=True)

p=1
while p>0:
    print("=== Movie Tracker Menu ===")
    print()
    print("1. Add Movie from TMDB")
    print("2. Show All Movies")
    print("0. Exit")
    p=int(input(" \nEnter  Option--->"))
    print("==========================")
    print()
    if p==1:
        title = '1'
        while title != '0':
            title = input("Movie: ")
            if title == '0':
                break

            query = urllib.parse.quote(title)
            url = f"https://api.themoviedb.org/3/search/movie?api_key=d74a624410ea1d50ef3545bfb815acf5&query={query}"
            data = json.load(urllib.request.urlopen(url))
            if not data["results"]:
                print("Movie not found.")
                continue

            movie = data["results"][0]
            id = movie["id"]

            details = json.load(urllib.request.urlopen(
                f"https://api.themoviedb.org/3/movie/{id}?api_key=d74a624410ea1d50ef3545bfb815acf5"
            ))

            print("\n", details["title"])
            print(details.get("tagline", ""))
            print()
            print("Year:", details.get("release_date", "Unknown")[:4])
            print("Genre:", details["genres"][0]["name"] if details.get("genres") else "Unknown")
            print("Rating:", round(details.get("vote_average", 0.0), 1), "/10")
            print("Overview:", details.get("overview", "No overview"))


            # Prepare data for insertion
            tmdb_id = details["id"]
            title_db = details["title"]
            year = details.get("release_date", None)
            year = year[:4] if year else None
            genre = details["genres"][0]["name"] if details.get("genres") else None
            rating = round(details.get("vote_average", 0.0), 1)
            overview = details.get("overview", None)
            date_added = "2025-07-01"  # or you can use current date with datetime module

            insert_query = """
                INSERT INTO movies (tmdb_id, title, year, genre, rating, overview, date_added)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """
            values = (tmdb_id, title_db, year, genre, rating, overview, date_added)

            try:
                cu.execute(insert_query, values)
                c.commit()
                print()
                print("Movie inserted successfully!")
            except msc.errors.IntegrityError:
                print()
                print("This movie is already added in the database.")
            print("==========================")

        print("Exiting...")
        print("===================================================================")
        print()
        cu.close()
        c.close()
    if p==2:
        cu.execute("select * from movies")
        am=cu.fetchall()
        for row in am:
            for key, value in row.items():
                print(f"{key}: {value}")
            print("==========================")
        print("===================================================================")
else:
    quit()


