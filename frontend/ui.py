import streamlit as st
from datetime import date
import sys
from pathlib import Path

# Add the root directory to the Python path
sys.path.append(str(Path(__file__).resolve().parent.parent))

from backend.database import SessionLocal, add_book, Book, add_reading_progress


class ReadingInputForm:
    def __init__(self, books: list):
        self.books = books
        self.selected_book = None
        self.progress_date = date.today()
        self.pages_read = 0
        self.date_selection = 'Today'

    def display(self):
        st.header("Ben's Reading Tracker")
        st.subheader("An exercise in reclaiming a sense of direction or at least progress")

        book_titles = [book[0] for book in self.books]
        self.selected_book = st.selectbox('What book did you read today?', book_titles)
        # establish the radio button collection for when I read
        self.date_selection = st.radio('When did you read?',
                                       options=['Today', 'Another day'])

        if self.date_selection == 'Today':
            self.progress_date = date.today()
        else:
            self.progress_date = st.date_input('Select date', self.progress_date)

        self.pages_read = st.number_input('How many pages did you read?', min_value=0)

        st.text('Did you finish doing some reading?')
        if st.button('Yes!'):
            return self.selected_book, self.progress_date, self.pages_read
        return None, None, None


class BookManagementForm:
    def __init__(self):
        self.title = ''
        self.author = ''
        self.start_date = date.today()
        self.end_date = None

    def display_add_form(self):
        st.text('Do you have a book to add?')
        columns = st.columns([4, 2])
        with columns[0]:
            self.title = st.text_input(label='title', label_visibility='hidden', placeholder='Title')
        with columns[1]:
            self.author = st.text_input(label='author', label_visibility='hidden', placeholder='Author')

        self.start_date = st.date_input('Start Date', self.start_date)
        self.end_date = st.date_input('End Date (optional)', self.end_date)
        if st.button('Add my book!'):
            return self.title, self.author, self.start_date, self.end_date
        return None, None, None, None

    @staticmethod
    def display_remove_form(books: list):
        st.header('Do you want to remove a book?')

        book_titles = [book[0] for book in books]
        selected_book = st.selectbox('Choose a book to remove:', book_titles)

        if st.button('Remove book'):
            return selected_book
        return None


class ProgressVisualization:
    def __init__(self):
        self.book_id = None

    def display_grid(self, data):
        st.header('Your reading progress:')

    def display_graph(self, data):
        st.header('Reading progress over time: ')


if __name__ == '__main__':
    # initialize the local session
    session = SessionLocal()

    # get the list of books from the database
    book_list = session.query(Book).all()

    # display the reading input form
    reading_form = ReadingInputForm([(book.title, book.author) for book in book_list])
    selected_book_title, progress_date, pages_read = reading_form.display()

    if selected_book_title and progress_date and pages_read:
        selected_book = session.query(Book).filter_by(title=selected_book_title).first()
        if selected_book:
            # add the reading progress to the database
            new_progress = add_reading_progress(session, selected_book.booksId, progress_date, pages_read)
            st.success(f"Reading progress on {new_progress.date} for '{selected_book.title}' added:"
                       f" {new_progress.pages_read} pages read.")

    # display the book add form
    book_management_form = BookManagementForm()
    new_book_title, new_book_author, start_date, end_date = book_management_form.display_add_form()

    if new_book_title and new_book_author:
        # add the new book to the database
        new_book = add_book(session, new_book_title, new_book_author, start_date, end_date)
        st.success(f"Book '{new_book.title}' by {new_book.author} added to the list!")
        # refresh the book list after adding a new book
        book_list = session.query(Book).all()

    # display remove book form
    selected_book_to_remove = book_management_form.display_remove_form(
        [(book.title, book.author) for book in book_list])

    if selected_book_to_remove:
        # find the book to remove by title and delete it
        book_to_remove = session.query(Book).filter_by(title=selected_book_to_remove).first()
        if book_to_remove:
            session.delete(book_to_remove)
            session.commit()
            st.success(f"Book '{book_to_remove.title}' removed from the list!")
            # refresh the book list after adding a new book
            book_list = session.query(Book).all()

    session.close()



