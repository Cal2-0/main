# Movieszbt - Movie Collection Manager

A Flask-based web application for managing movie collections with dual-database architecture supporting both guest and registered users.

## Features

- **Dual Database Architecture**: Separate databases for guests and registered users
- **Guest Mode**: Anonymous users can use a shared movie collection
- **User Authentication**: Secure login and registration system for personal collections
- **Personal Collections**: Each registered user gets their own separate movie table
- **TMDB Integration**: Search and add movies from The Movie Database
- **Modern UI**: Beautiful, responsive design with dark theme
- **Movie Management**: Add, view, and remove movies from collections

## Database Architecture

### 1. `movie` Database (for Guests)
- **Purpose**: Shared collection for anonymous users
- **Table**: `movies` - contains all guest-added movies
- **Access**: Anyone can view and modify

### 2. `users` Database (for Registered Users)
- **Purpose**: User accounts and personal collections
- **Tables**:
  - `users` - user account information
  - `{username}_movies` - personal movie collection for each user

## Setup Instructions

### 1. Database Setup

Create two separate MySQL databases:

```sql
CREATE DATABASE movie;
CREATE DATABASE users;
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Run the Application

```bash
python app.py
```

The application will automatically create the necessary database tables on first run.

### 4. Access the Application

Open your browser and go to `http://localhost:5000`

## How It Works

### Guest Users
- Can access the application without registration
- Add movies to the shared `movie` database
- View and manage the guest collection
- Can register anytime to create a personal collection

### Registered Users
- Have their own personal movie collection
- Each user gets a separate table: `{username}_movies`
- Complete isolation between user collections
- Can only access their own movies

## Database Schema

### movie Database
**movies table:**
- `id`: Primary key
- `tmdb_id`: TMDB movie ID (unique)
- `title`: Movie title
- `year`: Release year
- `genre`: Movie genre
- `rating`: TMDB rating
- `overview`: Movie description
- `date_added`: Date added to collection
- `poster_url`: Movie poster URL
- `imdb_id`: IMDB ID for external links

### users Database
**users table:**
- `id`: Primary key
- `username`: Unique username
- `email`: Unique email address
- `password_hash`: Hashed password
- `created_at`: Account creation timestamp

**{username}_movies table (one per user):**
- `id`: Primary key
- `tmdb_id`: TMDB movie ID (unique per user)
- `title`: Movie title
- `year`: Release year
- `genre`: Movie genre
- `rating`: TMDB rating
- `overview`: Movie description
- `date_added`: Date added to collection
- `poster_url`: Movie poster URL
- `imdb_id`: IMDB ID for external links

## Key Features

1. **Dual Database Support**: Separate handling for guests and registered users
2. **Dynamic Table Creation**: User tables are created automatically on registration
3. **Session Management**: Secure session handling with Flask sessions
4. **User-Specific Operations**: All movie operations are isolated per user
5. **Guest-Friendly**: No registration required to start using the app

## Usage

### For Guests
1. **Visit the app** - no registration needed
2. **Search movies** - add them to the guest collection
3. **View collection** - see all guest-added movies
4. **Register anytime** - to create your own collection

### For Registered Users
1. **Register**: Create a new account with username, email, and password
2. **Login**: Sign in with your credentials
3. **Add Movies**: Search for movies and add them to your personal collection
4. **View Collection**: See all movies in your personal collection
5. **Remove Movies**: Delete movies from your collection
6. **Logout**: Securely sign out

## Security Features

- Password hashing using Werkzeug
- Session-based authentication
- User-specific data isolation
- SQL injection protection
- CSRF protection (built into Flask forms)
- Dynamic table creation with proper escaping

## API Integration

The application integrates with:
- **TMDB API**: For movie search and details
- **IMDB**: For external movie links

## File Structure

```
movie/
├── app.py              # Main Flask application
├── index.html          # Home page with movie search
├── view.html           # Movie collection view
├── login.html          # Login page
├── register.html       # Registration page
├── main.py             # CLI version (legacy)
├── requirements.txt    # Python dependencies
└── README.md          # This file
```

## Database Examples

### Guest Collection
```sql
-- In 'movie' database
SELECT * FROM movies;
```

### User Collections
```sql
-- In 'users' database
SELECT * FROM users;
SELECT * FROM john_movies;  -- John's personal collection
SELECT * FROM sarah_movies; -- Sarah's personal collection
``` 