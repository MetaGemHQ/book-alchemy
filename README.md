# Book Alchemy

A Flask + SQLAlchemy digital library app. Manage authors and books, sort, search, and delete entries from a SQLite database.

## Features

- Add authors with name, birth date, and optional date of death
- Add books with ISBN, title, publication year, and author
- Home page lists all books with their author
- Sort books by title or author
- Search books by title or author name (case-insensitive partial match)
- Delete a book; if its author has no other books, the author is also removed

## Tech stack

- Backend: Flask
- Database: SQLite via SQLAlchemy ORM
- Templating: Jinja2

## Project structure

- app.py - Flask routes and config
- data_models.py - SQLAlchemy models (Author, Book)
- templates/ - Jinja2 HTML templates (add_author.html, add_book.html, home.html)
- data/ - SQLite database lives here (gitignored)
- requirements.txt - Python dependencies
- README.md - this file

## Running locally

1. Install dependencies: pip install -r requirements.txt
2. Run the app: python app.py
3. Open http://localhost:5002/ in a browser

On first run, uncomment the db.create_all() block in app.py to create the SQLite tables, then comment it back out.

## Routes

- GET /                       Home page (supports ?sort_by=title|author and ?search=...)
- GET, POST /add_author       Display form / create author
- GET, POST /add_book         Display form / create book
- POST /book/<id>/delete      Delete a book (and its author if orphaned)
