from sqlalchemy import create_engine, Column, Integer, String, Date, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship

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


