# MovieIt - AI-Powered Movie Tracker

A modern web application for tracking and discovering movies, powered by AI recommendations.

## Features

- Movie tracking and organization
- AI-powered movie recommendations
- Smart filtering and search
- Interactive movie details
- User-friendly interface

## Tech Stack

- Frontend: React.js with modern UI components
- Backend: Flask (Python)
- Database: SQLite
- AI Integration: OpenAI API
- Movie Data: TMDB API

## Setup Instructions

### Backend Setup
1. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
2. Install dependencies:
   ```bash
   cd backend
   pip install -r requirements.txt
   ```
3. Set up environment variables in `.env`:
   ```
   FLASK_APP=run.py
   FLASK_ENV=development
   OPENAI_API_KEY=your_openai_api_key
   TMDB_API_KEY=your_tmdb_api_key
   ```
4. Run the backend:
   ```bash
   flask run
   ```

### Frontend Setup
1. Install dependencies:
   ```bash
   cd frontend
   npm install
   ```
2. Run the development server:
   ```bash
   npm start
   ```

## Project Structure

```
MovieIt/
├── backend/
│   ├── app/
│   │   ├── models/
│   │   ├── routes/
│   │   └── services/
│   ├── requirements.txt
│   └── run.py
├── frontend/
│   ├── public/
│   ├── src/
│   │   ├── components/
│   │   ├── services/
│   │   └── App.js
│   └── package.json
└── README.md
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request 