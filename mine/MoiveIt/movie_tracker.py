import json
import os
from datetime import datetime
import urllib.request
import urllib.parse
import urllib.error
import time
import socket
import requests

class MovieTracker:
    def __init__(self):
        self.movies_file = "movies.json"
        self.movies = self.load_movies()
        # Replace this with your TMDB API key from https://www.themoviedb.org/settings/api
        self.api_key = "d74a624410ea1d50ef3545bfb815acf5"  # <-- Put your API key here
        self.base_url = "https://api.themoviedb.org/3"
        socket.setdefaulttimeout(10)
        
        # Genre shortcuts and common misspellings
        self.genre_shortcuts = {
            'a': 'action', 'ac': 'action',
            'adv': 'adventure', 'av': 'adventure',
            'ani': 'animation', 'an': 'animation',
            'com': 'comedy', 'c': 'comedy',
            'cri': 'crime', 'cr': 'crime',
            'doc': 'documentary', 'd': 'documentary',
            'dra': 'drama', 'dr': 'drama',
            'fam': 'family', 'f': 'family',
            'fan': 'fantasy', 'fa': 'fantasy',
            'hor': 'horror', 'h': 'horror',
            'mys': 'mystery', 'm': 'mystery',
            'rom': 'romance', 'r': 'romance',
            'sci': 'science fiction', 'sf': 'science fiction',
            'thr': 'thriller', 't': 'thriller'
        }
        
        # Common genre suggestions
        self.genre_suggestions = [
            "Action", "Adventure", "Animation", "Comedy", "Crime",
            "Documentary", "Drama", "Family", "Fantasy", "Horror",
            "Mystery", "Romance", "Science Fiction", "Thriller"
        ]

    def load_movies(self):
        if os.path.exists(self.movies_file):
            with open(self.movies_file, 'r') as f:
                return json.load(f)
        return []

    def save_movies(self):
        with open(self.movies_file, 'w') as f:
            json.dump(self.movies, f, indent=4)

    def make_api_request(self, url, max_retries=3):
        for attempt in range(max_retries):
            try:
                response = requests.get(url, timeout=5)  # Add timeout
                response.raise_for_status()
                return response.json()
            except requests.exceptions.Timeout:
                print(f"Request timed out. Attempt {attempt + 1}/{max_retries}")
                if attempt == max_retries - 1:
                    raise Exception("API request timed out after multiple attempts")
            except requests.exceptions.ConnectionError:
                print(f"Connection error. Attempt {attempt + 1}/{max_retries}")
                if attempt == max_retries - 1:
                    raise Exception("Could not connect to TMDB API. Please check your internet connection.")
            except requests.exceptions.RequestException as e:
                print(f"API request failed: {str(e)}. Attempt {attempt + 1}/{max_retries}")
                if attempt == max_retries - 1:
                    raise Exception(f"API request failed: {str(e)}")
            time.sleep(1)  # Wait before retrying
        return None

    def search_movies(self, title):
        """Search for multiple movies matching the title"""
        url = f"{self.base_url}/search/movie?api_key={self.api_key}&query={urllib.parse.quote(title)}"
        data = self.make_api_request(url)
        if data and data.get("results"):
            return data["results"]
        return []

    def get_movie_details(self, movie_id):
        """Get detailed information about a movie"""
        url = f"{self.base_url}/movie/{movie_id}?api_key={self.api_key}"
        return self.make_api_request(url)

    def get_movie_credits(self, movie_id):
        """Get cast and crew information for a movie"""
        url = f"{self.base_url}/movie/{movie_id}/credits?api_key={self.api_key}"
        return self.make_api_request(url)

    def get_genre_suggestions(self, partial):
        partial = partial.lower()
        suggestions = []
        # Check shortcuts
        for shortcut, genre in self.genre_shortcuts.items():
            if shortcut.startswith(partial):
                suggestions.append(genre)
        # Check full genres
        for genre in self.genre_suggestions:
            if genre.lower().startswith(partial):
                suggestions.append(genre.lower())
        return list(set(suggestions))

    def get_ai_recommendation(self, query):
        """Get movie recommendations based on a query"""
        # First, search for the movie
        search_results = self.search_movies(query)
        if not search_results:
            return None
            
        # Get recommendations for the first result
        movie_id = search_results[0]['id']
        url = f"{self.base_url}/movie/{movie_id}/recommendations?api_key={self.api_key}"
        data = self.make_api_request(url)
        
        if data and data.get("results"):
            return data["results"]
        return None

    def get_genre_movies(self, genre):
        """Get popular movies in a specific genre"""
        # First, get the genre ID
        url = f"{self.base_url}/genre/movie/list?api_key={self.api_key}"
        data = self.make_api_request(url)
        
        if not data or not data.get("genres"):
            return None
            
        genre_id = None
        for g in data["genres"]:
            if g["name"].lower() == genre.lower():
                genre_id = g["id"]
                break
                
        if not genre_id:
            return None
            
        # Get movies in this genre
        url = f"{self.base_url}/discover/movie?api_key={self.api_key}&with_genres={genre_id}&sort_by=popularity.desc"
        data = self.make_api_request(url)
        
        if data and data.get("results"):
            return data["results"]
        return None

    def add_movie(self):
        while True:
            print("\n=== Add New Movie ===")
            title = input("Enter movie title (or 'q' to quit): ")
            
            if title.lower() == 'q':
                print("\nReturning to main menu...")
                break
            
            print("\nSearching for movie...")
            movie_data = self.search_movies(title)
            if not movie_data:
                print(f"\nMovie '{title}' not found!")
                continue

            if any(m.get('tmdb_id') == movie_data[0]['id'] for m in self.movies):
                print(f"\nMovie '{movie_data[0]['title']}' is already in your collection!")
                continue

            print("Getting movie details...")
            details = self.get_movie_details(movie_data[0]['id'])
            if not details:
                print(f"\nCould not fetch details for '{title}'!")
                continue

            genre = details["genres"][0]["name"] if details["genres"] else "Unknown"
            
            movie = {
                "title": details["title"],
                "year": details["release_date"][:4],
                "genre": genre,
                "rating": str(round(details["vote_average"], 1)),
                "overview": details["overview"],
                "date_added": datetime.now().strftime("%Y-%m-%d"),
                "tmdb_id": details["id"]
            }
            
            self.movies.append(movie)
            self.save_movies()
            print(f"\nMovie '{movie['title']}' added successfully!")
            print(f"Year: {movie['year']}")
            print(f"Genre: {movie['genre']}")
            print(f"Rating: {movie['rating']}/10")
            print(f"Overview: {movie['overview'][:100]}...")
            
            print("\nAdd another movie? (Press Enter to continue, 'q' to quit)")

    def show_all_movies(self):
        if not self.movies:
            print("\nNo movies in your collection!")
            return

        print("\n=== Your Movie Collection ===")
        print("\n{:<4} {:<4} {:<40} {:<20} {:<10}".format("Rank", "No.", "Title", "Genre", "Rating"))
        print("-" * 80)

        sorted_movies = sorted(self.movies, key=lambda x: float(x['rating']), reverse=True)
        
        for i, movie in enumerate(sorted_movies, 1):
            title = movie['title']
            if len(title) > 37:
                title = title[:34] + "..."
            
            print("{:<4} {:<4} {:<40} {:<20} {:<10}".format(
                i, i, title, movie['genre'], movie['rating'] + "/10"
            ))
        
        print("-" * 80)
        print(f"\nTotal movies: {len(self.movies)}")

    def filter_movies(self):
        if not self.movies:
            print("\nNo movies to filter!")
            return

        print("\n=== Filter Movies ===")
        print("1. By Genre")
        print("2. By Year")
        print("3. By Rating")
        print("4. Get AI Recommendations")
        choice = input("\nChoose filter option (1-4): ")

        if choice == "1":
            print("\nAvailable genres (you can use shortcuts like 'a' for action):")
            for genre in self.genre_suggestions:
                print(f"- {genre}")
            
            genre = input("\nEnter genre to filter (or partial name): ").lower()
            suggestions = self.get_genre_suggestions(genre)
            if suggestions:
                if len(suggestions) > 1:
                    print("\nDid you mean one of these genres?")
                    for i, sug in enumerate(suggestions, 1):
                        print(f"{i}. {sug}")
                    try:
                        choice = int(input("\nSelect a genre number (or 0 to cancel): "))
                        if choice == 0:
                            return
                        if 1 <= choice <= len(suggestions):
                            genre = suggestions[choice - 1]
                        else:
                            print("Invalid choice!")
                            return
                    except ValueError:
                        print("Invalid input!")
                        return
                else:
                    genre = suggestions[0]
                    print(f"\nUsing genre: {genre}")

            filtered = [m for m in self.movies if genre in m['genre'].lower()]
            
        elif choice == "2":
            year = input("Enter year to filter: ")
            filtered = [m for m in self.movies if year == m['year']]
            
        elif choice == "3":
            rating = input("Enter minimum rating (1-10): ")
            filtered = [m for m in self.movies if float(m['rating']) >= float(rating)]
            
        elif choice == "4":
            query = input("\nWhat kind of movie are you looking for? (e.g., 'action movies like Die Hard'): ")
            print("\nSearching for recommendations...")
            recommendations = self.get_ai_recommendation(query)
            if recommendations:
                print("\n=== Recommended Movies ===")
                print("\n{:<4} {:<40} {:<20} {:<10}".format("No.", "Title", "Genre", "Rating"))
                print("-" * 75)
                for i, movie in enumerate(recommendations, 1):
                    print("{:<4} {:<40} {:<20} {:<10}".format(
                        i,
                        movie['title'][:37] + "..." if len(movie['title']) > 37 else movie['title'],
                        movie.get('genre', 'Unknown'),
                        str(round(movie.get('vote_average', 0), 1)) + "/10"
                    ))
                print("-" * 75)
                return
            else:
                print("\nCould not find recommendations. Try a different search term.")
                return
        else:
            print("Invalid option!")
            return

        if not filtered:
            print("\nNo movies found matching your criteria!")
            return

        print("\n=== Filtered Movies ===")
        print("\n{:<4} {:<4} {:<40} {:<20} {:<10}".format("Rank", "No.", "Title", "Genre", "Rating"))
        print("-" * 80)
        
        sorted_filtered = sorted(filtered, key=lambda x: float(x['rating']), reverse=True)
        
        for i, movie in enumerate(sorted_filtered, 1):
            title = movie['title']
            if len(title) > 37:
                title = title[:34] + "..."
            
            print("{:<4} {:<4} {:<40} {:<20} {:<10}".format(
                i, i, title, movie['genre'], movie['rating'] + "/10"
            ))
        
        print("-" * 80)
        print(f"\nFound {len(filtered)} movies matching your criteria.")

    def remove_movie(self):
        if not self.movies:
            print("\nNo movies in your collection!")
            return

        print("\n=== Remove Movie ===")
        sorted_movies = sorted(self.movies, key=lambda x: float(x['rating']), reverse=True)
        
        print("\n{:<4} {:<4} {:<40} {:<20} {:<10}".format("Rank", "No.", "Title", "Genre", "Rating"))
        print("-" * 80)
        
        for i, movie in enumerate(sorted_movies, 1):
            title = movie['title']
            if len(title) > 37:
                title = title[:34] + "..."
            
            print("{:<4} {:<4} {:<40} {:<20} {:<10}".format(
                i, i, title, movie['genre'], movie['rating'] + "/10"
            ))
        
        print("-" * 80)

        try:
            choice = int(input("\nEnter the rank number of the movie to remove (or 0 to cancel): "))
            if choice == 0:
                print("\nCancelled removal.")
                return
            if 1 <= choice <= len(sorted_movies):
                movie_to_remove = sorted_movies[choice - 1]
                self.movies = [m for m in self.movies if m['tmdb_id'] != movie_to_remove['tmdb_id']]
                self.save_movies()
                print(f"\nMovie '{movie_to_remove['title']}' has been removed from your collection!")
            else:
                print("\nInvalid rank number!")
        except ValueError:
            print("\nPlease enter a valid number!")

    def clear_library(self):
        if not self.movies:
            print("\nYour library is already empty!")
            return

        confirm = input("\nAre you sure you want to clear your entire movie library? (yes/no): ")
        if confirm.lower() == 'yes':
            self.movies = []
            self.save_movies()
            print("\nYour movie library has been cleared!")
        else:
            print("\nLibrary clearing cancelled.")

def main():
    tracker = MovieTracker()
    
    while True:
        print("\n=== Movie Tracker ===")
        print("1. Add New Movie")
        print("2. Show All Movies")
        print("3. Filter Movies")
        print("4. Remove Movie")
        print("5. Clear Library")
        print("6. Exit")
        
        choice = input("\nChoose an option (1-6): ")
        
        if choice == "1":
            tracker.add_movie()
        elif choice == "2":
            tracker.show_all_movies()
        elif choice == "3":
            tracker.filter_movies()
        elif choice == "4":
            tracker.remove_movie()
        elif choice == "5":
            tracker.clear_library()
        elif choice == "6":
            print("\nGoodbye!")
            break
        else:
            print("\nInvalid option! Please try again.")

if __name__ == "__main__":
    main() 
