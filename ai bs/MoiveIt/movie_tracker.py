import json
import os
from datetime import datetime
import urllib.request
import urllib.parse
import urllib.error

class MovieTracker:
    def __init__(self):
        self.movies_file = "movies.json"
        self.movies = self.load_movies()
        self.api_key = "d74a624410ea1d50ef3545bfb815acf5"  # Your TMDB API key
        self.base_url = "https://api.themoviedb.org/3"

    def load_movies(self):
        if os.path.exists(self.movies_file):
            with open(self.movies_file, 'r') as f:
                return json.load(f)
        return []

    def save_movies(self):
        with open(self.movies_file, 'w') as f:
            json.dump(self.movies, f, indent=4)

    def fetch_from_tmdb(self, url):
        try:
            with urllib.request.urlopen(url) as response:
                data = response.read()
                return json.loads(data)
        except urllib.error.URLError as e:
            print(f"Error: {e}")
            return None

    def search_movie(self, title):
        """Search movie by title using TMDB API"""
        query = urllib.parse.quote(title)
        url = f"{self.base_url}/search/movie?api_key={self.api_key}&query={query}"
        data = self.fetch_from_tmdb(url)
        return data["results"][0] if data and data.get("results") else None

    def get_movie_details(self, movie_id):
        url = f"{self.base_url}/movie/{movie_id}?api_key={self.api_key}"
        return self.fetch_from_tmdb(url)

    def add_movie(self):
        title = input("Enter movie title: ")
        print("Searching TMDB...")
        movie_data = self.search_movie(title)
        if not movie_data:
            print("Movie not found.")
            return

        details = self.get_movie_details(movie_data['id'])
        if not details:
            print("Details not found.")
            return

        movie = {
            "title": details["title"],
            "year": details.get("release_date", "Unknown")[:4],
            "genre": details["genres"][0]["name"] if details.get("genres") else "Unknown",
            "rating": str(round(details.get("vote_average", 0.0), 1)),
            "overview": details.get("overview", ""),
            "date_added": datetime.now().strftime("%Y-%m-%d"),
            "tmdb_id": details["id"]
        }

        if any(m["tmdb_id"] == movie["tmdb_id"] for m in self.movies):
            print("Movie already in your list.")
            return

        self.movies.append(movie)
        self.save_movies()
        print(f"\nAdded: {movie['title']} ({movie['year']})")

    def show_all_movies(self):
        if not self.movies:
            print("No movies found.")
            return
        print("\n=== Your Movie Collection ===")
        print("{:<4} {:<40} {:<10} {:<10}".format("No.", "Title", "Genre", "Rating"))
        print("-" * 70)
        for i, m in enumerate(self.movies, 1):
            print("{:<4} {:<40} {:<10} {:<10}".format(i, m["title"][:37], m["genre"], m["rating"] + "/10"))

    def remove_movie(self):
        self.show_all_movies()
        if not self.movies:
            return
        try:
            index = int(input("Enter number to remove: ")) - 1
            if 0 <= index < len(self.movies):
                removed = self.movies.pop(index)
                self.save_movies()
                print(f"Removed: {removed['title']}")
            else:
                print("Invalid number.")
        except ValueError:
            print("Invalid input.")

def main():
    tracker = MovieTracker()
    while True:
        print("\n=== Movie Tracker ===")
        print("1. Add Movie from TMDB")
        print("2. Show All Movies")
        print("3. Remove Movie")
        print("4. Exit")
        choice = input("Choose (1–4): ")
        if choice == "1":
            tracker.add_movie()
        elif choice == "2":
            tracker.show_all_movies()
        elif choice == "3":
            tracker.remove_movie()
        elif choice == "4":
            break
        else:
            print("Invalid option.")

if __name__ == "__main__":
    main()
