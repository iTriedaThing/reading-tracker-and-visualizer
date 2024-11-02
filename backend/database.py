import pandas as pd
from sqlalchemy import create_engine, Column, Integer, String, Date, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship, Session
from datetime import date

# define PostgreSQL connection
DATABASE_URL = 'postgresql://reading_user:o7z8ZQX4yEi4_Gr@localhost/reading_tracker'

# set up the sqlalchemy engine
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# base class for the models
Base = declarative_base()


class Book(Base):
    __tablename__ = 'books'
    booksId = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    author = Column(String)
    start_date = Column(Date)
    end_date = Column(Date)
    daily_goal = Column(String)

    # set up the relationship to reading progress
    reading_progress = relationship('ReadingProgress', back_populates='book')


class ReadingProgress(Base):
    __tablename__ = 'reading_progress'
    reading_progressId = Column(Integer, primary_key=True, index=True)
    booksId = Column(Integer, ForeignKey('books.booksId'))
    date = Column(Date)
    pages_read = Column(Integer)

    # set up the relationship to books
    book = relationship('Book', back_populates='reading_progress')


# creates the tables in the database
Base.metadata.create_all(bind=engine)


def add_book(session: Session, title: str, author: str, start_date: date, end_date: date = None, daily_goal: str =
None):
    new_book = Book(
        title=title,
        author=author,
        start_date=start_date,
        end_date=end_date,
        daily_goal=daily_goal
    )
    session.add(new_book)
    # commit the transaction to save the changes
    session.commit()
    # refresh the instance with the new ID from the database
    session.refresh(new_book)
    return new_book


def add_reading_progress(session: Session, booksId: int, date: date, pages_read: int):
    new_progress = ReadingProgress(
        booksId=booksId,
        date=date,
        pages_read=pages_read
    )
    session.add(new_progress)
    session.commit()
    session.refresh(new_progress)
    return new_progress


def edit_book(session: Session, old_title, old_author, new_title, new_author,
              new_start_date, new_daily_goal, new_end_date):
    book_to_edit = session.query(Book).filter_by(title=old_title, author=old_author).first()
    if book_to_edit:
        book_to_edit.title = new_title
        book_to_edit.author = new_author
        book_to_edit.start_date = new_start_date
        book_to_edit.end_date = new_end_date
        book_to_edit.daily_goal = new_daily_goal
        session.commit()



def fetch_reading_data(session: Session):
    # query the reading data
    data = session.query(ReadingProgress, Book.title).join(Book).all()

    # create a list of dictionaries with the reading data
    records = []
    for progress, title in data:
        records.append({
            'Title': title,
            'Date': progress.date,
            'Pages Read': progress.pages_read
        })

    # convert the data to a pandas DataFrame
    df = pd.DataFrame(records)

    return df


def remove_book(session: Session, book_title, book_author):
    book_to_remove = session.query(Book).filter_by(title=book_title, author=book_author).first()
    if book_to_remove:
        session.delete(book_to_remove)
        session.commit()
        return True
    return False

