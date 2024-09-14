import sys
from pathlib import Path
import streamlit as st
from datetime import date
from frontend.plots import HorizontalBarGraph
from sqlalchemy.orm import sessionmaker

# Add the root directory to the Python path
from backend.database import SessionLocal, add_book, Book, add_reading_progress, fetch_reading_data
# sys.path.append(str(Path(__file__).resolve().parent.parent))


class ReadingProgressForm:
    def __init__(self, books: list):
        self.books = books

    def display(self):
        st.table(data=self.books)


class ReadingInputForm:
    def __init__(self, books: list):
        self.books = books
        self.selected_book = None
        self.progress_date = date.today()
        self.pages_read = 0
        self.date_selection = 'Today'

    def display(self):

        book_titles = [book.title for book in self.books]
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
        # return None, None, None


class BookManagementForm:
    def __init__(self):
        self.title = ''
        self.author = ''
        self.start_date = date.today()
        self.end_date = None
        self.reading_goal = None

    def display_add_form(self):

        st.header('Do you have a book to add?')
        self.title = st.text_input(label='title', label_visibility='hidden', placeholder='Title')
        self.author = st.text_input(label='author', label_visibility='hidden', placeholder='Author')
        self.reading_goal = st.text_input(label='goal', label_visibility='hidden',
                                          placeholder="What's your daily goal?")
        self.start_date = st.date_input('Start Date', self.start_date)
        self.end_date = st.date_input('End Date (optional)', self.end_date)
        if st.button('Add my book!'):
            return self.title, self.author, self.start_date, self.end_date, self.reading_goal
        # return None, None, None, None, None

    @staticmethod
    def display_remove_form(books: list):
        st.header('Do you want to remove a book?')

        # create the dropdown for selecting as book to delete
        books_title_author = ['Select a book...']+[f'{book.title} by {book.author}' for book in books]

        selected_book = st.selectbox('Choose a book to remove:', books_title_author)

        if selected_book == 'Select a book...':
            st.session_state['confirming_delete'] = False

        # if a book is selected proceed
        try:
            selected_split = selected_book.split(' by ')
            selected_book_title = selected_split[0]
            selected_book_author = selected_split[1]
            print(selected_book_title)
            print(selected_book_author)
        except IndexError:
            pass

        try:
            # store the selected title and author so it doesn't get lost
            if ('selected_book_title' not in st.session_state or
                    st.session_state['selected_book_title'] != selected_book_title):
                st.session_state['selected_book_title'] = selected_book_title
            if ('selected_book_author' not in st.session_state or
                    st.session_state['selected_book_author'] != selected_book_author):
                st.session_state['selected_book_author'] = selected_book_author

            if st.button('Delete Book'):
                # get confirmation before deleting a book and set flag
                st.session_state['confirming_delete'] = True

            if st.session_state.get('confirming_delete', False):
                # get the title and author from the session state
                selected_book_title = st.session_state.get('selected_book_title', None)
                selected_book_author = st.session_state.get('selected_book_author', None)


                if selected_book_title and selected_book_author:
                    st.warning(f'Are you sure you want to delete {selected_book_title} by {selected_book_author}?')

                    confirm_delete = st.button('Yes, Delete', key='confirm_delete')
                    cancel_delete = st.button('Cancel', key='cancel_delete')

                    if confirm_delete:
                        # reset confirmation flag and selected book/author
                        st.session_state['confirming_delete'] = False
                        st.session_state['selected_book'] = 'Select a book...'
                        return selected_book_title, selected_book_author, 'Yes'
                    if cancel_delete:
                        st.session_state['confirming_delete'] = False
                        st.session_state['selected_book'] = 'Select a book...'
                        return None, None, 'No'
        except UnboundLocalError:
            pass



class ProgressVisualization:
    def __init__(self):
        self.book_id = None

    def display_grid(self, data):
        st.header('Your reading progress:')

    def display_graph(self, data):
        st.header('Reading progress over time: ')
        bar_graph = HorizontalBarGraph()
        figure = bar_graph.plot_reading_progress(data)
        return figure


if __name__ == '__main__':
    # initialize the local session
    session = SessionLocal()
    df = fetch_reading_data(session)

    # get the list of books from the database
    book_list = session.query(Book).all()

    st.header("Ben's Reading Tracker")
    st.subheader("An exercise in reclaiming a sense of direction or at least progress")
    helper_functions = HelperFunctions(session)

    with st.sidebar:
        # display the book add form
        book_management_form = BookManagementForm()
        new_book_title, new_book_author, start_date, end_date, daily_goal = book_management_form.display_add_form()

        if new_book_title and new_book_author:
            # add the new book to the database
            new_book = add_book(session, new_book_title, new_book_author, start_date, end_date, daily_goal)
            st.success(f"Book '{new_book.title}' by {new_book.author} added to the list!")
            # refresh the book list after adding a new book
            book_list = session.query(Book).all()

        # display remove book form
        selected_book_title, selected_book_author, confirmation = book_management_form.display_remove_form(book_list)
        print(selected_book_title, selected_book_author, confirmation)

        if selected_book_title and confirmation == 'Yes':
            if helper_functions.remove_book(selected_book_title, selected_book_author):
                st.success(f"'{selected_book_title}' by {selected_book_author} has been removed!")
                # refresh the book list after adding a new book
                book_list = session.query(Book).all()
                st.session_state['confirming_delete'] = False
            else:
                st.error('Error removing the book.')
        elif confirmation == 'No':
            st.success('Deletion canceled.')
            st.session_state['confirming_delete'] = False

    # display the reading progress form
    progress_form = ReadingProgressForm([(book.title, book.author, book.daily_goal) for book in book_list])
    progress_form.display()

    # display the reading input form
    reading_form = ReadingInputForm([(book.title, book.author) for book in book_list])
    selected_book_title, progress_date, pages_read = reading_form.display()

    if selected_book_title and progress_date and pages_read:
        selected_book = session.query(Book).filter_by(title=selected_book_title).first()
        if selected_book:
            book_list = session.query(Book).all()
            # add the reading progress to the database
            new_progress = add_reading_progress(session, selected_book.booksId, progress_date, pages_read)
            st.success(f"Reading progress on {new_progress.date} for '{selected_book.title}' added:"
                       f" {new_progress.pages_read} pages read.")



    progress_vis = ProgressVisualization()

    fig = progress_vis.display_graph(data=df)

    st.pyplot(fig)

    session.close()



