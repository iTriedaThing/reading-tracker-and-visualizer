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

    book_manager = BookManagementForm()
    reading_input = ReadingInputForm(book_list)

    book_input = reading_input.display()
    with st.sidebar:
        book_add = book_manager.display_add_form()
        if book_add:
            add_book(session, title=book_add[0], author=book_add[1], start_date=book_add[2],
                     end_date=book_add[3], daily_goal=book_add[4])

            st.session_state['book_list'] = fetch_books(session)
            st.success(f'{book_add[0]} was added to your reading list!')
            sleep(.75)
            st.rerun()

        book_remove = book_manager.display_remove_form(book_list)
        if book_remove:
            print(book_remove)
            remove_book(session, book_title=book_remove[0], book_author=book_remove[1])
            st.rerun()



    session.close()
    # print(f'add: {book_add}')
    # print(f'input: {book_input}')


if __name__ == '__main__':
    main()