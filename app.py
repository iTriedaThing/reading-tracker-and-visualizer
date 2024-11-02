import streamlit as st
from backend.database import SessionLocal, Book, add_reading_progress, add_book, remove_book, fetch_reading_data
from frontend.ui import BookManagementForm, ReadingInputForm, ProgressVisualization
from time import sleep


def fetch_books(session):
    """Fetches the list of books from the database."""
    return session.query(Book).all()


def main():
    # initialize the local session
    session = SessionLocal()

    if 'book_list' not in st.session_state:
        st.session_state['book_list'] = fetch_books(session)

    if 'selected_color' not in st.session_state:
        st.session_state['selected_color'] = 'Blues'

    book_df = fetch_reading_data(session)

    # get the list of books from the database
    book_list = session.query(Book).all()

    # establish all the class instances to display on the UI
    book_manager_form = BookManagementForm(book_list)
    reading_input_form = ReadingInputForm(book_list)
    progress_vis = ProgressVisualization(book_df)

    st.header("Ben's Reading Tracker")
    st.subheader("An exercise in reclaiming a sense of direction or at least progress")


    with st.sidebar:
        book_manager = book_manager_form.display(session=session)
        colormap = progress_vis.choose_graph_color()

    book_inputter = reading_input_form.display(session=session)

    # display the progress visualization
    progress_vis.display_table()

    graph = progress_vis.display_graph(colormap)
    st.pyplot(graph)

    session.close()


if __name__ == '__main__':
    main()
