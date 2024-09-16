import streamlit as st
from backend.database import SessionLocal, Book, add_reading_progress, add_book, remove_book, fetch_reading_data
from frontend.ui import BookManagementForm, ReadingInputForm
from time import sleep


def fetch_books(session):
    """Fetches the list of books from the database."""
    return session.query(Book).all()


def main():
    # initialize the local session
    session = SessionLocal()

    if 'book_list' not in st.session_state:
        st.session_state['book_list'] = fetch_books(session)

    df = fetch_reading_data(session)

    # get the list of books from the database
    book_list = session.query(Book).all()
    # print(book_list)

    st.header("Ben's Reading Tracker")
    st.subheader("An exercise in reclaiming a sense of direction or at least progress")

    book_manager_form = BookManagementForm(book_list)
    reading_input_form = ReadingInputForm(book_list)

    book_input = reading_input_form.display_reading_input()
    if book_input:
        add_reading_progress(session, booksId=book_input[0], date=book_input[1],
                             pages_read=book_input[2])

    with st.sidebar:
        book_manager = book_manager_form.display(session=session)




    session.close()
    # print(f'add: {book_add}')
    # print(f'input: {book_input}')


if __name__ == '__main__':
    main()