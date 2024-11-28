# Top Movies Collection

A Flask-based web application for managing and displaying a collection of movies using **The Movie Database (TMDb)** API. Users can add, rate, review, and delete movies.

---

## Features

- **View movies**: Browse the list of top movies sorted by rating.
- **Add movies**: Search and add movies using the TMDb API.
- **Edit movies**: Update ratings and reviews for existing movies.
- **Delete movies**: Remove movies from your collection.

---

## Setup

### Prerequisites

- Python 3.8+
- Flask
- SQLite
- TMDb API Key

### Installation

1. Clone the repository:
   ```bash
   git https://github.com/Dimplektech/Top-Movies-Collection.git

2. Create a virtual environment and install dependencies:
 ```bash
   python -m venv venv
  source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
  pip install -r requirements.txt

3. Create a .env file and add your credentials:
```bash
  API_Key=your_tmdb_api_key
  APP_SECRET_KEY=your_secret_key
  URL=https://api.themoviedb.org/3/search/movie

4. Run the application
 ```bash
  python app.py
