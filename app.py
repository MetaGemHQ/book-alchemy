import os
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for
from data_models import db, Author, Book

# Initialize the Flask application
app = Flask(__name__)

# Configure the database connection using an absolute path
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(basedir, 'data/library.sqlite')}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Connect Flask app to the flask-sqlalchemy code
db.init_app(app)


# ---------- Routes ----------


@app.route('/')
def home():
    """Display all books in the library, with optional search and sort."""
    sort_by = request.args.get('sort_by', 'title')
    search_term = request.args.get('search', '').strip()
    success_message = request.args.get('success_message')

    query = Book.query.join(Author)

    if search_term:
        like_pattern = f"%{search_term}%"
        query = query.filter(
            db.or_(
                Book.title.ilike(like_pattern),
                Author.name.ilike(like_pattern)
            )
        )

    if sort_by == 'author':
        query = query.order_by(Author.name, Book.title)
    else:
        query = query.order_by(Book.title)

    books = query.all()

    return render_template(
        'home.html',
        books=books,
        search_term=search_term,
        success_message=success_message
    )


@app.route('/add_author', methods=['GET', 'POST'])
def add_author():
    """Display the add-author form (GET) or create a new Author (POST)."""
    success_message = None
    error_message = None

    if request.method == 'POST':
        name = request.form['name'].strip()
        birthdate_str = request.form['birthdate']
        date_of_death_str = request.form.get('date_of_death', '').strip()

        if not name:
            error_message = "Author name cannot be empty or whitespace."
            return render_template('add_author.html', error_message=error_message)

        existing_author = Author.query.filter_by(name=name).first()
        if existing_author:
            error_message = f"An author named '{name}' already exists. Please use a different name."
            return render_template('add_author.html', error_message=error_message)

        birth_date = datetime.strptime(birthdate_str, '%Y-%m-%d').date()
        date_of_death = None
        if date_of_death_str:
            date_of_death = datetime.strptime(date_of_death_str, '%Y-%m-%d').date()

        new_author = Author(
            name=name,
            birth_date=birth_date,
            date_of_death=date_of_death
        )
        db.session.add(new_author)
        db.session.commit()

        success_message = f"Author '{name}' was successfully added!"

    return render_template('add_author.html', success_message=success_message, error_message=error_message)


@app.route('/add_book', methods=['GET', 'POST'])
def add_book():
    """Display the add-book form (GET) or create a new Book (POST)."""
    success_message = None
    error_message = None

    if request.method == 'POST':
        isbn = request.form['isbn'].strip()
        title = request.form['title'].strip()
        publication_year = int(request.form['publication_year'])
        author_id = int(request.form['author_id'])

        if not isbn:
            error_message = "ISBN cannot be empty or whitespace."
        elif not title:
            error_message = "Title cannot be empty or whitespace."
        else:
            existing_book = Book.query.filter_by(isbn=isbn).first()
            if existing_book:
                error_message = (
                    f"A book with ISBN '{isbn}' already exists in the library "
                    f"('{existing_book.title}'). ISBNs must be unique."
                )

        if error_message is None:
            new_book = Book(
                isbn=isbn,
                title=title,
                publication_year=publication_year,
                author_id=author_id
            )
            db.session.add(new_book)
            db.session.commit()

            success_message = f"Book '{title}' was successfully added!"

    authors = Author.query.order_by(Author.name).all()

    return render_template(
        'add_book.html',
        authors=authors,
        success_message=success_message,
        error_message=error_message
    )


@app.route('/book/<int:book_id>/delete', methods=['POST'])
def delete_book(book_id):
    """Delete a book. If the author has no other books, delete the author too."""
    book = Book.query.get_or_404(book_id)
    author = book.author
    book_title = book.title

    db.session.delete(book)
    db.session.commit()

    remaining_books = Book.query.filter_by(author_id=author.id).count()
    if remaining_books == 0:
        db.session.delete(author)
        db.session.commit()
        success_message = f"Book '{book_title}' was deleted, along with author '{author.name}' (no other books)."
    else:
        success_message = f"Book '{book_title}' was successfully deleted."

    return redirect(url_for('home', success_message=success_message))


# Create the database tables if they do not yet exist.
# Safe to leave on; create_all() is a no-op when tables are already present.
with app.app_context():
    db.create_all()


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5002, debug=True)