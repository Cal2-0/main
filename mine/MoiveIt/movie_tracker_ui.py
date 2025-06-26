import customtkinter as ctk
import json
from datetime import datetime
import urllib.request
import urllib.parse
import urllib.error
import time
import socket
from PIL import Image, ImageTk
import io
import threading
import requests
from movie_tracker import MovieTracker
import os

class MovieTrackerUI:
    def __init__(self):
        self.root = ctk.CTk()
        self.root.title("MovieIt")
        self.root.geometry("1200x800")
        self.root.minsize(800, 600)  # Set minimum window size
        
        # Set theme colors
        self.colors = {
            "bg_dark": "#1a1a1a",
            "bg_light": "#2d2d2d",
            "primary": "#00bd7e",
            "secondary": "#6c5ce7",
            "text": "#ffffff",
            "text_secondary": "#a0a0a0",
            "hover": "#3d3d3d",
            "card_bg": "#2d2d2d",
            "hover_card_bg": "#363636"
        }
        
        # Configure appearance
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("green")
        
        # Initialize backend
        self.tracker = MovieTracker()
        
        # Cache for movie posters
        self.poster_cache = {}
        self.hover_frame = None
        
        # Create main container
        self.create_main_layout()
        
        # Show initial view
        self.show_movie_grid()

    def create_main_layout(self):
        # Create sidebar
        self.sidebar = ctk.CTkFrame(self.root, width=200, corner_radius=0)
        self.sidebar.pack(side="left", fill="y", padx=0, pady=0)
        self.sidebar.pack_propagate(False)
        
        # App title with logo
        title_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        title_frame.pack(fill="x", padx=20, pady=30)
        
        title_label = ctk.CTkLabel(
            title_frame, 
            text="🎬 MovieIt",
            font=ctk.CTkFont(size=24, weight="bold"),
            text_color=self.colors["primary"]
        )
        title_label.pack()
        
        # Search bar in sidebar
        search_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        search_frame.pack(fill="x", padx=20, pady=(0, 20))
        
        self.search_var = ctk.StringVar()
        self.search_var.trace('w', self.on_search_change)
        
        self.search_entry = ctk.CTkEntry(
            search_frame,
            placeholder_text="Search movies...",
            height=35,
            font=ctk.CTkFont(size=12),
            textvariable=self.search_var
        )
        self.search_entry.pack(fill="x", pady=(0, 5))
        
        # Navigation buttons
        nav_buttons = [
            ("🏠 Home", self.show_movie_grid),
            ("➕ Add Movie", self.show_add_movie),
            ("⭐ Top Rated", lambda: self.show_movie_grid(sort_by="rating")),
            ("🎲 Random Movie", self.show_random_movie_dialog),
            ("⚙️ Settings", self.show_settings)
        ]
        
        for text, command in nav_buttons:
            btn = ctk.CTkButton(
                self.sidebar,
                text=text,
                command=command,
                fg_color="transparent",
                text_color=self.colors["text"],
                anchor="w",
                font=ctk.CTkFont(size=14),
                height=40,
                width=160,
                hover_color=self.colors["hover"]
            )
            btn.pack(padx=20, pady=5)
        
        # Main content area
        self.content_frame = ctk.CTkFrame(self.root, fg_color=self.colors["bg_dark"])
        self.content_frame.pack(side="left", fill="both", expand=True)
        
        # Header
        self.header_frame = ctk.CTkFrame(self.content_frame, fg_color="transparent", height=60)
        self.header_frame.pack(fill="x", padx=20, pady=10)
        
        self.header_title = ctk.CTkLabel(
            self.header_frame,
            text="My Movie Collection",
            font=ctk.CTkFont(size=20, weight="bold")
        )
        self.header_title.pack(side="left")
        
        # Movies container
        self.movies_frame = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        self.movies_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))

    def on_search_change(self, *args):
        # Debounce search
        if hasattr(self, '_after_id'):
            self.root.after_cancel(self._after_id)
        self._after_id = self.root.after(300, self.search_library)

    def search_library(self):
        query = self.search_var.get()
        if not query:
            self.show_movie_grid()
            return
            
        self.clear_content()
        self.header_title.configure(text=f"Search Results: {query}")
        
        scroll_frame = ctk.CTkScrollableFrame(self.movies_frame)
        scroll_frame.pack(fill="both", expand=True)
        
        filtered_movies = [
            movie for movie in self.tracker.movies
            if query.lower() in movie['title'].lower() or
               query.lower() in movie['genre'].lower()
        ]
        
        if not filtered_movies:
            no_results = ctk.CTkLabel(
                scroll_frame,
                text="No movies found matching your search",
                font=ctk.CTkFont(size=14)
            )
            no_results.pack(pady=20)
            return
        
        self.display_movie_grid(scroll_frame, filtered_movies)

    def display_movie_grid(self, parent, movies):
        grid_frame = ctk.CTkFrame(parent, fg_color="transparent")
        grid_frame.pack(fill="both", expand=True)
        
        # Calculate number of columns based on window width
        window_width = self.root.winfo_width()
        card_width = 200
        padding = 20
        num_columns = max(1, (window_width - 240) // (card_width + padding))
        
        for i, movie in enumerate(movies):
            row = i // num_columns
            col = i % num_columns
            self.create_movie_card(grid_frame, movie, row, col)
        
        grid_frame.grid_columnconfigure(tuple(range(num_columns)), weight=1)

    def create_movie_card(self, parent, movie, row, col):
        # Card frame with increased height for better spacing
        card = ctk.CTkFrame(
            parent,
            fg_color=self.colors["card_bg"],
            corner_radius=10,
            width=180,
            height=340  # Increased height for better spacing
        )
        card.grid(row=row, column=col, padx=10, pady=10, sticky="nsew")
        card.grid_propagate(False)
        
        # Load and display poster
        poster = self.load_poster(movie['tmdb_id'], "w342")
        if poster:
            poster_label = ctk.CTkLabel(
                card,
                image=poster,
                text="",
                width=160,
                height=240
            )
            poster_label.pack(padx=10, pady=(10, 5))
        
        # Title with better wrapping
        title = movie['title']
        if len(title) > 25:
            title = title[:22] + "..."
        
        title_label = ctk.CTkLabel(
            card,
            text=title,
            font=ctk.CTkFont(size=14, weight="bold"),
            wraplength=160,
            height=40  # Fixed height for title
        )
        title_label.pack(padx=10, pady=(5, 5))
        
        # Rating badge
        rating_frame = ctk.CTkFrame(
            card,
            fg_color=self.colors["primary"],
            corner_radius=5,
            width=40,
            height=20
        )
        rating_frame.pack(pady=5)
        rating_frame.pack_propagate(False)
        
        rating_label = ctk.CTkLabel(
            rating_frame,
            text=f"{movie['rating']}/10",
            font=ctk.CTkFont(size=12, weight="bold")
        )
        rating_label.pack(expand=True)
        
        # Genre with fixed height
        genre_label = ctk.CTkLabel(
            card,
            text=movie['genre'],
            font=ctk.CTkFont(size=12),
            text_color=self.colors["text_secondary"],
            height=20  # Fixed height for genre
        )
        genre_label.pack(pady=5)
        
        # Bind click event to show details
        card.bind("<Button-1>", lambda e, m=movie: self.show_movie_details(m))
        # Keep hover effect
        card.bind("<Enter>", lambda e, m=movie: self.show_hover(e, m))
        card.bind("<Leave>", self.hide_hover)

    def show_hover(self, event, movie):
        if self.hover_frame:
            self.hide_hover(None)
        
        # Create hover card
        self.hover_frame = ctk.CTkFrame(
            self.root,
            fg_color=self.colors["hover_card_bg"],
            corner_radius=10
        )
        
        # Position hover card near the mouse but ensure it stays within window bounds
        x = event.x_root + 10
        y = event.y_root + 10
        
        # Get screen dimensions
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        
        # Adjust position if needed
        if x + 300 > screen_width:
            x = screen_width - 310
        if y + 400 > screen_height:
            y = screen_height - 410
        
        self.hover_frame.place(x=x, y=y)
        
        # Movie details
        title_label = ctk.CTkLabel(
            self.hover_frame,
            text=movie['title'],
            font=ctk.CTkFont(size=16, weight="bold"),
            wraplength=280
        )
        title_label.pack(padx=15, pady=(15, 5))
        
        details_text = f"Year: {movie['year']}\n"
        details_text += f"Genre: {movie['genre']}\n"
        details_text += f"Rating: {movie['rating']}/10\n\n"
        details_text += f"Overview:\n{movie['overview'][:200]}..."
        
        details_label = ctk.CTkLabel(
            self.hover_frame,
            text=details_text,
            font=ctk.CTkFont(size=12),
            justify="left",
            wraplength=280
        )
        details_label.pack(padx=15, pady=(5, 15))
        
        # Remove button
        remove_btn = ctk.CTkButton(
            self.hover_frame,
            text="Remove",
            command=lambda: self.remove_movie(movie),
            fg_color=self.colors["secondary"],
            hover_color="#5a4cc7",
            width=100,
            height=30
        )
        remove_btn.pack(pady=(0, 15))

    def hide_hover(self, event):
        if self.hover_frame:
            self.hover_frame.destroy()
            self.hover_frame = None

    def show_movie_grid(self, sort_by="date_added"):
        self.clear_content()
        self.header_title.configure(text="My Movie Collection")
        
        # Sort options
        sort_frame = ctk.CTkFrame(self.header_frame, fg_color="transparent")
        sort_frame.pack(side="right")
        
        sort_label = ctk.CTkLabel(
            sort_frame,
            text="Sort by:",
            font=ctk.CTkFont(size=12)
        )
        sort_label.pack(side="left", padx=(0, 10))
        
        sort_options = [
            ("Date Added", "date_added"),
            ("Rating", "rating"),
            ("Title", "title"),
            ("Year", "year")
        ]
        
        for text, value in sort_options:
            btn = ctk.CTkButton(
                sort_frame,
                text=text,
                command=lambda v=value: self.show_movie_grid(sort_by=v),
                fg_color="transparent" if sort_by != value else self.colors["primary"],
                text_color=self.colors["text"],
                font=ctk.CTkFont(size=12),
                height=25,
                width=80
            )
            btn.pack(side="left", padx=2)
        
        # Create scrollable frame
        scroll_frame = ctk.CTkScrollableFrame(self.movies_frame)
        scroll_frame.pack(fill="both", expand=True)
        
        # Sort movies
        if sort_by == "rating":
            movies = sorted(self.tracker.movies, key=lambda x: float(x['rating']), reverse=True)
        elif sort_by == "title":
            movies = sorted(self.tracker.movies, key=lambda x: x['title'].lower())
        elif sort_by == "year":
            movies = sorted(self.tracker.movies, key=lambda x: x['year'], reverse=True)
        else:  # date_added
            movies = list(reversed(self.tracker.movies))
        
        self.display_movie_grid(scroll_frame, movies)

    def remove_movie(self, movie):
        self.hide_hover(None)
        self.tracker.movies = [m for m in self.tracker.movies if m['tmdb_id'] != movie['tmdb_id']]
        self.tracker.save_movies()
        self.show_notification(f"Removed '{movie['title']}'")
        self.show_movie_grid()

    def clear_content(self):
        for widget in self.movies_frame.winfo_children():
            widget.destroy()
        for widget in self.header_frame.winfo_children()[1:]:
            widget.destroy()

    def show_notification(self, message, type_="info"):
        notification = ctk.CTkFrame(
            self.root,
            fg_color=self.colors["primary"] if type_ == "info" else "#e74c3c",
            corner_radius=5
        )
        
        label = ctk.CTkLabel(
            notification,
            text=message,
            font=ctk.CTkFont(size=12),
            text_color=self.colors["text"]
        )
        label.pack(padx=15, pady=10)
        
        # Position at the bottom center
        notification.place(
            relx=0.5,
            rely=0.95,
            anchor="center"
        )
        
        # Auto-hide after 3 seconds
        self.root.after(3000, notification.destroy)

    def show_add_movie(self):
        self.clear_content()
        self.header_title.configure(text="Add New Movie")
        
        # Create search frame
        search_frame = ctk.CTkFrame(self.movies_frame, fg_color="transparent")
        search_frame.pack(fill="x", padx=20, pady=20)
        
        search_entry = ctk.CTkEntry(
            search_frame,
            placeholder_text="Enter movie title...",
            height=40,
            font=ctk.CTkFont(size=14),
            width=300
        )
        search_entry.pack(side="left", padx=(0, 10))
        
        search_btn = ctk.CTkButton(
            search_frame,
            text="Search",
            command=lambda: self.search_movie(search_entry.get()),
            height=40,
            width=100
        )
        search_btn.pack(side="left")
        
        # Results frame
        self.results_frame = ctk.CTkScrollableFrame(self.movies_frame)
        self.results_frame.pack(fill="both", expand=True, padx=20)

    def search_movie(self, title):
        if not title:
            return
            
        for widget in self.results_frame.winfo_children():
            widget.destroy()
            
        loading_label = ctk.CTkLabel(
            self.results_frame,
            text="Searching...",
            font=ctk.CTkFont(size=14)
        )
        loading_label.pack(pady=20)
        self.root.update()
        
        results = self.tracker.search_movies(title)
        loading_label.destroy()
        
        if not results:
            no_results = ctk.CTkLabel(
                self.results_frame,
                text="No movies found",
                font=ctk.CTkFont(size=14)
            )
            no_results.pack(pady=20)
            return
            
        for i, movie in enumerate(results):
            self.create_search_result_card(movie, i // 2, i % 2)

    def create_search_result_card(self, movie, row, col):
        card = ctk.CTkFrame(
            self.results_frame,
            fg_color=self.colors["card_bg"],
            corner_radius=10
        )
        card.grid(row=row, column=col, padx=10, pady=10, sticky="ew")
        
        title_label = ctk.CTkLabel(
            card,
            text=movie['title'],
            font=ctk.CTkFont(size=16, weight="bold"),
            wraplength=280
        )
        title_label.pack(padx=15, pady=(15, 5))
        
        if 'release_date' in movie and movie['release_date']:
            year = movie['release_date'][:4]
            year_label = ctk.CTkLabel(
                card,
                text=f"Year: {year}",
                font=ctk.CTkFont(size=12),
                text_color=self.colors["text_secondary"]
            )
            year_label.pack(pady=2)
        
        if 'vote_average' in movie:
            rating_label = ctk.CTkLabel(
                card,
                text=f"Rating: {movie['vote_average']}/10",
                font=ctk.CTkFont(size=12),
                text_color=self.colors["text_secondary"]
            )
            rating_label.pack(pady=2)
        
        if 'overview' in movie:
            overview = movie['overview']
            if len(overview) > 150:
                overview = overview[:147] + "..."
            overview_label = ctk.CTkLabel(
                card,
                text=overview,
                font=ctk.CTkFont(size=12),
                wraplength=280,
                justify="left"
            )
            overview_label.pack(padx=15, pady=(5, 15))
        
        add_btn = ctk.CTkButton(
            card,
            text="Add to Library",
            command=lambda: self.add_movie_from_search(movie),
            width=120,
            height=32
        )
        add_btn.pack(pady=(0, 15))

    def add_movie_from_search(self, movie_data):
        # Check if movie already exists
        if any(m.get('tmdb_id') == movie_data['id'] for m in self.tracker.movies):
            self.show_notification(f"'{movie_data['title']}' is already in your collection!", type_="error")
            return
        
        # Get full movie details
        details = self.tracker.get_movie_details(movie_data['id'])
        if not details:
            self.show_notification("Could not fetch movie details", type_="error")
            return
        
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
        
        self.tracker.movies.append(movie)
        self.tracker.save_movies()
        self.show_notification(f"Added '{movie['title']}' to your collection!")
        
        # Clear search results
        for widget in self.results_frame.winfo_children():
            widget.destroy()

    def show_settings(self):
        self.clear_content()
        self.header_title.configure(text="Settings")
        
        settings_frame = ctk.CTkFrame(self.movies_frame, fg_color="transparent")
        settings_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Theme settings
        theme_label = ctk.CTkLabel(
            settings_frame,
            text="Theme",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        theme_label.pack(anchor="w", pady=(0, 10))
        
        theme_frame = ctk.CTkFrame(settings_frame, fg_color="transparent")
        theme_frame.pack(fill="x", pady=(0, 20))
        
        themes = [("Dark", "dark"), ("Light", "light")]
        for text, mode in themes:
            btn = ctk.CTkButton(
                theme_frame,
                text=text,
                command=lambda m=mode: self.change_theme(m),
                width=100,
                height=32
            )
            btn.pack(side="left", padx=5)
        
        # Library management
        library_label = ctk.CTkLabel(
            settings_frame,
            text="Library Management",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        library_label.pack(anchor="w", pady=(0, 10))
        
        # Add sample movies button
        sample_btn = ctk.CTkButton(
            settings_frame,
            text="Add Sample Movies",
            command=self.add_sample_movies,
            width=150,
            height=32
        )
        sample_btn.pack(anchor="w", pady=5)
        
        export_btn = ctk.CTkButton(
            settings_frame,
            text="Export Library",
            command=self.export_library,
            width=150,
            height=32
        )
        export_btn.pack(anchor="w", pady=5)
        
        clear_btn = ctk.CTkButton(
            settings_frame,
            text="Clear Library",
            command=self.confirm_clear_library,
            fg_color="#e74c3c",
            hover_color="#c0392b",
            width=150,
            height=32
        )
        clear_btn.pack(anchor="w", pady=5)

    def add_sample_movies(self):
        """Add a collection of top movies across different genres"""
        # Dictionary of movies by genre
        movies_by_genre = {
            "Action": [
                {"title": "The Dark Knight", "year": "2008", "genre": "Action", "rating": "9.0", "overview": "When the menace known as the Joker wreaks havoc and chaos on the people of Gotham, Batman must accept one of the greatest psychological and physical tests of his ability to fight injustice.", "tmdb_id": "155"},
                {"title": "Inception", "year": "2010", "genre": "Action", "rating": "8.8", "overview": "A thief who steals corporate secrets through the use of dream-sharing technology is given the inverse task of planting an idea into the mind of a C.E.O.", "tmdb_id": "27205"},
                {"title": "The Matrix", "year": "1999", "genre": "Action", "rating": "8.7", "overview": "A computer hacker learns from mysterious rebels about the true nature of his reality and his role in the war against its controllers.", "tmdb_id": "603"},
                {"title": "Die Hard", "year": "1988", "genre": "Action", "rating": "8.2", "overview": "An action classic about an off-duty cop who must save hostages from terrorists in a Los Angeles skyscraper.", "tmdb_id": "562"},
                {"title": "Mad Max: Fury Road", "year": "2015", "genre": "Action", "rating": "8.1", "overview": "In a post-apocalyptic wasteland, a woman rebels against a tyrannical ruler in search for her homeland with the aid of a group of female prisoners, a psychotic worshiper, and a drifter named Max.", "tmdb_id": "76341"}
            ],
            "Drama": [
                {"title": "The Godfather", "year": "1972", "genre": "Drama", "rating": "9.2", "overview": "The aging patriarch of an organized crime dynasty transfers control of his clandestine empire to his reluctant son.", "tmdb_id": "238"},
                {"title": "Pulp Fiction", "year": "1994", "genre": "Drama", "rating": "8.9", "overview": "The lives of two mob hitmen, a boxer, a gangster and his wife, and a pair of diner bandits intertwine in four tales of violence and redemption.", "tmdb_id": "680"},
                {"title": "Forrest Gump", "year": "1994", "genre": "Drama", "rating": "8.8", "overview": "The presidencies of Kennedy and Johnson, the Vietnam War, the Watergate scandal and other historical events unfold from the perspective of an Alabama man with an IQ of 75.", "tmdb_id": "13"},
                {"title": "The Green Mile", "year": "1999", "genre": "Drama", "rating": "8.6", "overview": "The lives of guards on Death Row are affected by one of their charges: a black man accused of child murder and rape, yet who has a mysterious gift.", "tmdb_id": "497"},
                {"title": "Fight Club", "year": "1999", "genre": "Drama", "rating": "8.8", "overview": "An insomniac office worker and a devil-may-care soapmaker form an underground fight club that evolves into something much, much more.", "tmdb_id": "550"}
            ],
            "Comedy": [
                {"title": "The Grand Budapest Hotel", "year": "2014", "genre": "Comedy", "rating": "8.1", "overview": "The adventures of Gustave H, a legendary concierge at a famous hotel from the fictional Republic of Zubrowka between the first and second World Wars.", "tmdb_id": "120467"},
                {"title": "Airplane!", "year": "1980", "genre": "Comedy", "rating": "7.7", "overview": "A man afraid to fly must ensure that a plane lands safely after the pilots become sick.", "tmdb_id": "813"},
                {"title": "Groundhog Day", "year": "1993", "genre": "Comedy", "rating": "8.0", "overview": "A weatherman finds himself inexplicably living the same day over and over again.", "tmdb_id": "137"},
                {"title": "The Big Lebowski", "year": "1998", "genre": "Comedy", "rating": "8.1", "overview": "The Dude is mistaken for a millionaire Lebowski and seeks restitution for his ruined rug and enlists his bowling buddies to help get it.", "tmdb_id": "115"},
                {"title": "What We Do in the Shadows", "year": "2014", "genre": "Comedy", "rating": "7.7", "overview": "A documentary team films the lives of a group of vampires for a few months. The vampires share a house in Wellington, New Zealand.", "tmdb_id": "246741"}
            ],
            "Sci-Fi": [
                {"title": "2001: A Space Odyssey", "year": "1968", "genre": "Sci-Fi", "rating": "8.3", "overview": "After discovering a mysterious artifact buried beneath the Lunar surface, mankind sets off on a quest to find its origins with help from intelligent supercomputer H.A.L. 9000.", "tmdb_id": "62"},
                {"title": "Alien", "year": "1979", "genre": "Sci-Fi", "rating": "8.4", "overview": "After a space merchant vessel receives an unknown transmission as a distress call, one of the crew is attacked by a mysterious life form and they soon realize that its life cycle has merely begun.", "tmdb_id": "348"},
                {"title": "The Martian", "year": "2015", "genre": "Sci-Fi", "rating": "8.0", "overview": "An astronaut becomes stranded on Mars after his team assume him dead, and must rely on his ingenuity to find a way to signal to Earth that he is alive.", "tmdb_id": "286217"},
                {"title": "Ex Machina", "year": "2014", "genre": "Sci-Fi", "rating": "7.7", "overview": "A young programmer is selected to participate in a ground-breaking experiment in synthetic intelligence by evaluating the human qualities of a highly advanced humanoid A.I.", "tmdb_id": "264660"},
                {"title": "Blade Runner", "year": "1982", "genre": "Sci-Fi", "rating": "8.1", "overview": "A blade runner must pursue and terminate four replicants who stole a ship in space, and have returned to Earth to find their creator.", "tmdb_id": "78"}
            ],
            "Horror": [
                {"title": "The Exorcist", "year": "1973", "genre": "Horror", "rating": "8.0", "overview": "When a 12-year-old girl is possessed by a mysterious entity, her mother seeks the help of two priests to save her.", "tmdb_id": "9552"},
                {"title": "A Quiet Place", "year": "2018", "genre": "Horror", "rating": "7.5", "overview": "In a post-apocalyptic world, a family is forced to live in silence while hiding from monsters with ultra-sensitive hearing.", "tmdb_id": "447332"},
                {"title": "The Babadook", "year": "2014", "genre": "Horror", "rating": "6.8", "overview": "A single mother, plagued by the violent death of her husband, battles with her son's fear of a monster lurking in the house, but soon discovers a sinister presence all around her.", "tmdb_id": "242512"},
                {"title": "The Shining", "year": "1980", "genre": "Horror", "rating": "8.4", "overview": "A family heads to an isolated hotel for the winter where an evil and spiritual presence influences the father into violence, while his psychic son sees horrific forebodings from both past and future.", "tmdb_id": "694"},
                {"title": "Psycho", "year": "1960", "genre": "Horror", "rating": "8.5", "overview": "A Phoenix secretary embezzles $40,000 from her employer's client, goes on the run, and checks into a remote motel run by a young man under the domination of his mother.", "tmdb_id": "539"}
            ]
        }
        
        # Add movies to library
        added_count = 0
        for genre, movies in movies_by_genre.items():
            for movie in movies:
                # Check if movie already exists
                if not any(m.get('tmdb_id') == movie['tmdb_id'] for m in self.tracker.movies):
                    movie['date_added'] = datetime.now().strftime("%Y-%m-%d")
                    self.tracker.movies.append(movie)
                    added_count += 1
        
        # Save changes
        self.tracker.save_movies()
        
        # Show notification
        self.show_notification(f"Added {added_count} new movies to your library!")
        
        # Refresh the view
        self.show_movie_grid()

    def export_library(self):
        with open("movies_export.json", "w") as f:
            json.dump(self.tracker.movies, f, indent=4)
        self.show_notification("Library exported to movies_export.json")

    def confirm_clear_library(self):
        confirm_frame = ctk.CTkFrame(
            self.root,
            fg_color=self.colors["bg_light"],
            corner_radius=10
        )
        
        label = ctk.CTkLabel(
            confirm_frame,
            text="Are you sure you want to clear your entire library?",
            font=ctk.CTkFont(size=14)
        )
        label.pack(padx=20, pady=(20, 15))
        
        btn_frame = ctk.CTkFrame(confirm_frame, fg_color="transparent")
        btn_frame.pack(padx=20, pady=(0, 20))
        
        cancel_btn = ctk.CTkButton(
            btn_frame,
            text="Cancel",
            command=confirm_frame.destroy,
            fg_color="transparent",
            border_width=1,
            width=100
        )
        cancel_btn.pack(side="left", padx=5)
        
        confirm_btn = ctk.CTkButton(
            btn_frame,
            text="Clear",
            command=lambda: [
                self.tracker.clear_library(),
                confirm_frame.destroy(),
                self.show_notification("Library cleared"),
                self.show_movie_grid()
            ],
            fg_color="#e74c3c",
            hover_color="#c0392b",
            width=100
        )
        confirm_btn.pack(side="left", padx=5)
        
        # Center the confirmation dialog
        confirm_frame.place(relx=0.5, rely=0.5, anchor="center")

    def change_theme(self, theme):
        ctk.set_appearance_mode(theme)
        self.show_notification(f"Theme changed to {theme}")

    def show_movie_details(self, movie):
        # Create a new window for movie details
        details_window = ctk.CTkToplevel(self.root)
        details_window.title(f"Movie Details - {movie['title']}")
        details_window.geometry("1000x900")  # Increased size for more content
        details_window.minsize(800, 800)
        
        # Make it modal
        details_window.transient(self.root)
        details_window.grab_set()
        
        # Main container
        main_frame = ctk.CTkScrollableFrame(details_window)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Top section with poster and title
        top_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        top_frame.pack(fill="x", pady=(0, 20))
        
        # Load and display poster
        poster = self.load_poster(movie['tmdb_id'], "w500")
        if poster:
            poster_frame = ctk.CTkFrame(top_frame, fg_color="transparent")
            poster_frame.pack(side="left", padx=(0, 20))
            
            poster_label = ctk.CTkLabel(
                poster_frame,
                image=poster,
                text="",  # Empty text
                width=300,
                height=450
            )
            poster_label.pack()
        
        # Title and rating section
        title_frame = ctk.CTkFrame(top_frame, fg_color="transparent")
        title_frame.pack(side="left", fill="both", expand=True)
        
        title_label = ctk.CTkLabel(
            title_frame,
            text=movie['title'],
            font=ctk.CTkFont(size=28, weight="bold"),
            wraplength=400
        )
        title_label.pack(anchor="w", pady=(0, 10))
        
        # Rating badge
        rating_frame = ctk.CTkFrame(
            title_frame,
            fg_color=self.colors["primary"],
            corner_radius=5,
            width=80,
            height=40
        )
        rating_frame.pack(anchor="w", pady=(0, 20))
        rating_frame.pack_propagate(False)
        
        rating_label = ctk.CTkLabel(
            rating_frame,
            text=f"{movie['rating']}/10",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        rating_label.pack(expand=True)
        
        # Get additional movie details
        additional_details = self.tracker.get_movie_details(movie['tmdb_id'])
        
        # Movie Info Section
        info_frame = ctk.CTkFrame(title_frame, fg_color=self.colors["card_bg"])
        info_frame.pack(fill="x", pady=(0, 20))
        
        # Basic Info
        basic_info = [
            ("Year", movie['year']),
            ("Genre", movie['genre']),
            ("Runtime", f"{additional_details.get('runtime', 'N/A')} min"),
            ("Language", additional_details.get('original_language', 'N/A').upper()),
            ("Release Date", additional_details.get('release_date', 'N/A')),
            ("Status", additional_details.get('status', 'N/A'))
        ]
        
        for label, value in basic_info:
            info_row = ctk.CTkFrame(info_frame, fg_color="transparent")
            info_row.pack(fill="x", padx=20, pady=5)
            
            label_widget = ctk.CTkLabel(
                info_row,
                text=f"{label}:",
                font=ctk.CTkFont(size=14, weight="bold"),
                text_color=self.colors["text_secondary"]
            )
            label_widget.pack(side="left", padx=(0, 10))
            
            value_widget = ctk.CTkLabel(
                info_row,
                text=value,
                font=ctk.CTkFont(size=14)
            )
            value_widget.pack(side="left")
        
        # Box Office Info
        if 'budget' in additional_details or 'revenue' in additional_details:
            box_office_frame = ctk.CTkFrame(title_frame, fg_color=self.colors["card_bg"])
            box_office_frame.pack(fill="x", pady=(0, 20))
            
            box_office_title = ctk.CTkLabel(
                box_office_frame,
                text="Box Office",
                font=ctk.CTkFont(size=16, weight="bold")
            )
            box_office_title.pack(anchor="w", padx=20, pady=(15, 10))
            
            budget = additional_details.get('budget', 0)
            revenue = additional_details.get('revenue', 0)
            
            if budget > 0:
                budget_label = ctk.CTkLabel(
                    box_office_frame,
                    text=f"Budget: ${budget:,}",
                    font=ctk.CTkFont(size=14)
                )
                budget_label.pack(anchor="w", padx=20, pady=2)
            
            if revenue > 0:
                revenue_label = ctk.CTkLabel(
                    box_office_frame,
                    text=f"Revenue: ${revenue:,}",
                    font=ctk.CTkFont(size=14)
                )
                revenue_label.pack(anchor="w", padx=20, pady=2)
        
        # Cast Section
        if 'credits' in additional_details and 'cast' in additional_details['credits']:
            cast_frame = ctk.CTkFrame(main_frame, fg_color=self.colors["card_bg"])
            cast_frame.pack(fill="x", pady=(0, 20))
            
            cast_title = ctk.CTkLabel(
                cast_frame,
                text="Top Cast",
                font=ctk.CTkFont(size=16, weight="bold")
            )
            cast_title.pack(anchor="w", padx=20, pady=(15, 10))
            
            cast_list = additional_details['credits']['cast'][:5]  # Top 5 cast members
            for cast_member in cast_list:
                cast_row = ctk.CTkFrame(cast_frame, fg_color="transparent")
                cast_row.pack(fill="x", padx=20, pady=2)
                
                name_label = ctk.CTkLabel(
                    cast_row,
                    text=f"{cast_member['name']}",
                    font=ctk.CTkFont(size=14, weight="bold")
                )
                name_label.pack(side="left", padx=(0, 10))
                
                character_label = ctk.CTkLabel(
                    cast_row,
                    text=f"as {cast_member['character']}",
                    font=ctk.CTkFont(size=14),
                    text_color=self.colors["text_secondary"]
                )
                character_label.pack(side="left")
        
        # Overview section
        overview_frame = ctk.CTkFrame(main_frame, fg_color=self.colors["card_bg"])
        overview_frame.pack(fill="x", pady=(0, 20))
        
        overview_title = ctk.CTkLabel(
            overview_frame,
            text="Overview",
            font=ctk.CTkFont(size=20, weight="bold")
        )
        overview_title.pack(anchor="w", padx=20, pady=(15, 10))
        
        overview_text = ctk.CTkLabel(
            overview_frame,
            text=movie['overview'],
            font=ctk.CTkFont(size=16),
            wraplength=900,
            justify="left"
        )
        overview_text.pack(padx=20, pady=(0, 15))
        
        # AI Recommendations Section
        recommendations_frame = ctk.CTkFrame(main_frame, fg_color=self.colors["card_bg"])
        recommendations_frame.pack(fill="x", pady=(0, 20))
        
        recommendations_title = ctk.CTkLabel(
            recommendations_frame,
            text="You Might Also Like",
            font=ctk.CTkFont(size=20, weight="bold")
        )
        recommendations_title.pack(anchor="w", padx=20, pady=(15, 10))
        
        # Get recommendations
        recommendations = self.tracker.get_movie_recommendations(movie['tmdb_id'])
        if recommendations:
            for rec in recommendations[:3]:  # Show top 3 recommendations
                rec_frame = ctk.CTkFrame(recommendations_frame, fg_color="transparent")
                rec_frame.pack(fill="x", padx=20, pady=5)
                
                rec_title = ctk.CTkLabel(
                    rec_frame,
                    text=rec['title'],
                    font=ctk.CTkFont(size=14, weight="bold")
                )
                rec_title.pack(side="left", padx=(0, 10))
                
                rec_rating = ctk.CTkLabel(
                    rec_frame,
                    text=f"Rating: {rec.get('vote_average', 'N/A')}/10",
                    font=ctk.CTkFont(size=14),
                    text_color=self.colors["text_secondary"]
                )
                rec_rating.pack(side="left")
        
        # Random Movie Button
        random_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        random_frame.pack(fill="x", pady=(0, 20))
        
        random_btn = ctk.CTkButton(
            random_frame,
            text="🎲 Suggest Random Movie",
            command=lambda: self.show_random_movie(),
            width=200,
            height=40,
            font=ctk.CTkFont(size=14, weight="bold")
        )
        random_btn.pack(pady=10)
        
        # Action buttons
        button_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        button_frame.pack(fill="x", pady=(0, 20))
        
        remove_btn = ctk.CTkButton(
            button_frame,
            text="Remove from Library",
            command=lambda: [self.remove_movie(movie), details_window.destroy()],
            fg_color="#e74c3c",
            hover_color="#c0392b",
            width=150,
            height=35
        )
        remove_btn.pack(side="left", padx=5)
        
        close_btn = ctk.CTkButton(
            button_frame,
            text="Close",
            command=details_window.destroy,
            width=100,
            height=35
        )
        close_btn.pack(side="right", padx=5)
        
        # Center the window
        details_window.update_idletasks()
        width = details_window.winfo_width()
        height = details_window.winfo_height()
        x = (details_window.winfo_screenwidth() // 2) - (width // 2)
        y = (details_window.winfo_screenheight() // 2) - (height // 2)
        details_window.geometry(f'{width}x{height}+{x}+{y}')

    def show_random_movie_dialog(self):
        """Show dialog to select genre for random movie"""
        dialog = ctk.CTkToplevel(self.root)
        dialog.title("Random Movie")
        dialog.geometry("400x500")
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Get unique genres from movies
        genres = set()
        for movie in self.tracker.movies:
            genres.add(movie['genre'])
        genres = sorted(list(genres))
        
        # Title
        title_label = ctk.CTkLabel(
            dialog,
            text="🎲 Random Movie",
            font=ctk.CTkFont(size=24, weight="bold"),
            text_color=self.colors["primary"]
        )
        title_label.pack(pady=(20, 10))
        
        # Description
        desc_label = ctk.CTkLabel(
            dialog,
            text="Select a genre or get a completely random movie!",
            font=ctk.CTkFont(size=14),
            text_color=self.colors["text_secondary"]
        )
        desc_label.pack(pady=(0, 20))
        
        # Genre selection
        genre_frame = ctk.CTkFrame(dialog, fg_color="transparent")
        genre_frame.pack(fill="x", padx=20, pady=(0, 20))
        
        genre_label = ctk.CTkLabel(
            genre_frame,
            text="Select Genre:",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        genre_label.pack(anchor="w", pady=(0, 10))
        
        # Create genre buttons in a grid
        grid_frame = ctk.CTkFrame(genre_frame, fg_color="transparent")
        grid_frame.pack(fill="x")
        
        cols = 2
        for i, genre in enumerate(genres):
            row = i // cols
            col = i % cols
            
            btn = ctk.CTkButton(
                grid_frame,
                text=genre,
                command=lambda g=genre: [self.show_random_movie(g), dialog.destroy()],
                width=150,
                height=35,
                font=ctk.CTkFont(size=14)
            )
            btn.grid(row=row, column=col, padx=5, pady=5, sticky="ew")
        
        # Random button
        random_btn = ctk.CTkButton(
            dialog,
            text="🎲 Completely Random",
            command=lambda: [self.show_random_movie(), dialog.destroy()],
            width=200,
            height=40,
            font=ctk.CTkFont(size=16, weight="bold"),
            fg_color=self.colors["secondary"],
            hover_color="#5a4cc7"
        )
        random_btn.pack(pady=20)
        
        # Center the dialog
        dialog.update_idletasks()
        width = dialog.winfo_width()
        height = dialog.winfo_height()
        x = (dialog.winfo_screenwidth() // 2) - (width // 2)
        y = (dialog.winfo_screenheight() // 2) - (height // 2)
        dialog.geometry(f'{width}x{height}+{x}+{y}')

    def show_random_movie(self, genre=None):
        """Show a random movie suggestion with optional genre filter"""
        if not self.tracker.movies:
            self.show_notification("No movies in your library to suggest from!", type_="error")
            return
            
        import random
        if genre:
            filtered_movies = [m for m in self.tracker.movies if m['genre'] == genre]
            if not filtered_movies:
                self.show_notification(f"No movies found in genre: {genre}", type_="error")
                return
            random_movie = random.choice(filtered_movies)
        else:
            random_movie = random.choice(self.tracker.movies)
            
        self.show_movie_details(random_movie)

    def load_poster(self, movie_id, size="w500"):
        """Load movie poster from TMDB API with error handling and caching"""
        cache_key = f"{movie_id}_{size}"
        if cache_key in self.poster_cache:
            return self.poster_cache[cache_key]
            
        try:
            # Create placeholder image first
            placeholder = Image.new('RGB', (300, 450), color='#2d2d2d')
            photo = ImageTk.PhotoImage(placeholder)
            self.poster_cache[cache_key] = photo
            
            # Try to load actual poster
            url = f"https://image.tmdb.org/t/p/{size}/{movie_id}.jpg"
            response = requests.get(url, timeout=3)  # Reduced timeout
            if response.status_code == 200:
                image = Image.open(io.BytesIO(response.content))
                # Resize image to reduce memory usage
                if size == "w500":
                    image = image.resize((300, 450), Image.Resampling.LANCZOS)
                elif size == "w342":
                    image = image.resize((160, 240), Image.Resampling.LANCZOS)
                photo = ImageTk.PhotoImage(image)
                self.poster_cache[cache_key] = photo
                return photo
            return photo
        except Exception as e:
            print(f"Error loading poster: {e}")
            return photo

def main():
    app = MovieTrackerUI()
    app.root.mainloop()

if __name__ == "__main__":
    main() 