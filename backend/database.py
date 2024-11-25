import os  # Module for interacting with the operating system

import pandas as pd  # Pandas for data manipulation
from sqlalchemy import create_engine, Column, Integer, String, Date, ForeignKey  # Core SQLAlchemy components
from sqlalchemy.ext.declarative import declarative_base  # Base class for ORM models
from sqlalchemy.orm import sessionmaker, relationship, Session  # ORM components, including Session
from datetime import date  # Module for handling dates

import os  # Duplicate import of `os` is retained exactly as in input

# Retrieve and modify the database URL from environment variables
DATABASE_URL = os.environ.get("DATABASE_URL")  # Fetch the database URL from environment
if DATABASE_URL and DATABASE_URL.startswith("postgres://"):
    # Replace the outdated 'postgres://' URL prefix with 'postgresql://'
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

# Set up the SQLAlchemy engine for database interaction
engine = create_engine(DATABASE_URL)  # Connect to the database using the modified URL

# Configure a session factory for database transactions
# - autocommit=False: Transactions must be explicitly committed
# - autoflush=False: Prevents automatic flushing of changes to the database
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Define the declarative base class for ORM models
Base = declarative_base()


# Define the `Book` model
class Book(Base):
    """
    Represents a book in the database.

    Attributes:
        booksId (int): Primary key for the book.
        title (str): The title of the book.
        author (str): The author of the book.
        start_date (date): The date when reading starts.
        end_date (date): The date when reading ends.
        daily_goal (str): The daily reading goal.
        reading_progress (list): Relationship linking to associated reading progress entries.
    """
    __tablename__ = 'books'  # Define the name of the table in the database

    # Define the columns for the `books` table
    booksId = Column(Integer, primary_key=True, index=True)  # Primary key column
    title = Column(String, index=True)  # Title of the book (indexed for faster queries)
    author = Column(String)  # Author of the book
    start_date = Column(Date)  # Start date of reading the book
    end_date = Column(Date)  # End date of reading the book
    daily_goal = Column(String)  # Daily reading goal for the book

    # Define a one-to-many relationship with the `ReadingProgress` table
    reading_progress = relationship('ReadingProgress', back_populates='book')


# Define the `ReadingProgress` model
class ReadingProgress(Base):
    """
    Represents the reading progress for a specific book.

    Attributes:
        reading_progressId (int): Primary key for the reading progress entry.
        booksId (int): Foreign key referencing the `books` table.
        date (date): The date for the reading progress record.
        pages_read (int): The number of pages read on this date.
        book (Book): Relationship linking back to the associated `Book`.
    """
    __tablename__ = 'reading_progress'  # Define the name of the table in the database

    # Define the columns for the `reading_progress` table
    reading_progressId = Column(Integer, primary_key=True, index=True)  # Primary key column
    booksId = Column(Integer, ForeignKey('books.booksId'))  # Foreign key linking to `books` table
    date = Column(Date)  # The date of the reading progress entry
    pages_read = Column(Integer)  # Number of pages read on the specific date

    # Define a many-to-one relationship with the `Book` table
    book = relationship('Book', back_populates='reading_progress')


# Create the tables in the database if they do not already exist
Base.metadata.create_all(bind=engine)


def add_book(session: Session, title: str, author: str, start_date: date, end_date: date = None,
             daily_goal: str = None):
    """
    Adds a new book to the database.

    Args:
        session (Session): The SQLAlchemy session for database interaction.
        title (str): The title of the book.
        author (str): The author of the book.
        start_date (date): The start date for reading the book.
        end_date (date, optional): The end date for reading the book. Defaults to None.
        daily_goal (str, optional): The daily reading goal for the book. Defaults to None.

    Returns:
        Book: The newly added book instance.
    """
    # Create a new Book object with the provided details.
    new_book = Book(
        title=title,
        author=author,
        start_date=start_date,
        end_date=end_date,
        daily_goal=daily_goal
    )
    # Add the new book to the database session.
    session.add(new_book)

    # Commit the transaction to save the new book to the database.
    session.commit()

    # Refresh the new_book instance to load the generated ID from the database.
    session.refresh(new_book)

    return new_book  # Return the newly added book instance.


def add_reading_progress(session: Session, booksId: int, date: date, pages_read: int):
    """
    Adds a new reading progress entry to the database.

    Args:
        session (Session): The SQLAlchemy session for database interaction.
        booksId (int): The ID of the book the progress is associated with.
        date (date): The date of the reading progress.
        pages_read (int): The number of pages read on the given date.

    Returns:
        ReadingProgress: The newly added reading progress instance.
    """
    # Create a new ReadingProgress object with the provided details.
    new_progress = ReadingProgress(
        booksId=booksId,
        date=date,
        pages_read=pages_read
    )
    # Add the new reading progress entry to the database session.
    session.add(new_progress)

    # Commit the transaction to save the new reading progress to the database.
    session.commit()

    # Refresh the new_progress instance to load the generated ID from the database.
    session.refresh(new_progress)

    return new_progress  # Return the newly added reading progress instance.


def edit_book(session: Session, old_title: str, old_author: str, new_title: str, new_author: str,
              new_start_date: date, new_daily_goal: str, new_end_date: date):
    """
    Updates an existing book's details in the database.

    Args:
        session (Session): The SQLAlchemy session for database interaction.
        old_title (str): The current title of the book to be edited.
        old_author (str): The current author of the book to be edited.
        new_title (str): The new title of the book.
        new_author (str): The new author of the book.
        new_start_date (date): The new start date for the book.
        new_daily_goal (str): The new daily reading goal for the book.
        new_end_date (date): The new end date for the book.

    Returns:
        None
    """
    # Query the database to find the book to be edited based on the current title and author.
    book_to_edit = session.query(Book).filter_by(title=old_title, author=old_author).first()

    if book_to_edit:
        # Update the book's details with the new values.
        book_to_edit.title = new_title
        book_to_edit.author = new_author
        book_to_edit.start_date = new_start_date
        book_to_edit.daily_goal = new_daily_goal
        book_to_edit.end_date = new_end_date

        # Commit the changes to the database.
        session.commit()


def fetch_reading_data(session: Session):
    """
    Fetches reading progress data and book titles from the database.

    Args:
        session (Session): The SQLAlchemy session for database interaction.

    Returns:
        pd.DataFrame: A pandas DataFrame containing the reading progress records with columns:
            - 'Title': The title of the book.
            - 'Date': The date of the reading progress entry.
            - 'Pages Read': The number of pages read on the given date.
    """
    # Query the reading progress data, joining it with book titles.
    data = session.query(ReadingProgress, Book.title).join(Book).all()

    # Initialize a list to hold the records as dictionaries.
    records = []
    for progress, title in data:
        # Create a dictionary for each record with relevant details.
        records.append({
            'Title': title,
            'Date': progress.date,
            'Pages Read': progress.pages_read
        })

    # Convert the list of dictionaries into a pandas DataFrame.
    df = pd.DataFrame(records)

    return df  # Return the DataFrame with the reading data.


def remove_book(session: Session, book_title, book_author):
    """
    Removes a book and its associated data from the database.

    Args:
        session (Session): The SQLAlchemy session for database interaction.
        book_title (str): The title of the book to be removed.
        book_author (str): The author of the book to be removed.

    Returns:
        bool: True if the book was successfully removed, False if the book was not found.
    """
    # Query the database to find the book by its title and author.
    book_to_remove = session.query(Book).filter_by(title=book_title, author=book_author).first()

    if book_to_remove:
        # Delete the book record from the database.
        session.delete(book_to_remove)

        # Commit the transaction to save the changes.
        session.commit()

        return True  # Indicate the book was successfully removed.

    return False  # Indicate the book was not found in the database.
