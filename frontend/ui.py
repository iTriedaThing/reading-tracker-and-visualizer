import sys
import time

import streamlit as st
from datetime import date
from frontend.plots import HorizontalBarGraph

# Add the root directory to the Python path
from backend.database import (SessionLocal, add_book, Book, add_reading_progress, fetch_reading_data, edit_book,
                              remove_book)


# sys.path.append(str(Path(__file__).resolve().parent.parent))


class ReadingProgressForm:
    def __init__(self, books: list):
        self.books = books

    def display(self):
        if not self.books:
            st.info('No books available. Please add a book first.')
            return
        else:
            st.table(data=self.books)


class ReadingInputForm:
    def __init__(self, books: list):
        self.books = books
        self.selected_book = None
        self.progress_date = date.today()
        self.pages_read = 0
        self.date_selection = 'Today'

    def display(self, session):
        if not self.books:
            st.info('No books available. Please add a book first.')
            return

        book_options = {book.booksId: f'{book.title} ({book.author})' for book in self.books}
        selected_option = st.selectbox('What book did you read today?', list(book_options.values()))

        self.selected_book = [key for key, value in book_options.items() if value == selected_option][0]
        # establish the radio button collection for when I read
        self.date_selection = st.radio('When did you read?',
                                       options=['Today', 'Another day',],
                                       horizontal=True)

        if self.date_selection == 'Today':
            self.progress_date = date.today()
        else:
            self.progress_date = st.date_input('Select date', self.progress_date)

        self.pages_read = st.number_input('How many pages did you read?', min_value=0)

        st.text('Did you finish doing some reading?')
        if st.button('Yes!'):
            add_reading_progress(session, self.selected_book, self.progress_date, self.pages_read)
            st.rerun()
        # return None, None, None


class BookManagementForm:
    def __init__(self, books):
        self.books = books

    def reset_add_selectbox(self):
        st.session_state['add_expander'] = False

    def reset_remove_selectbox(self):
        st.session_state['remove_expander'] = False

    def cancel_remove_selectbox(self):
        st.session_state['select_remove_book'] = 'Select a book...'

    def reset_edit_selectbox(self):
        st.session_state['edit_expander'] = False


    def update_book(self, session, selected_book_title, selected_book_author, new_title,
                    new_author, new_start_date, new_daily_goal, new_end_date):
        edit_book(session, selected_book_title, selected_book_author, new_title,
                  new_author, new_start_date, new_daily_goal, new_end_date)
        self.reset_edit_selectbox()

    def display(self, session):

        book_titles = [f'{book.title} by {book.author}' for book in self.books]
        if 'add_expander' not in st.session_state:
            st.session_state['add_expander'] = False
        if 'edit_expander' not in st.session_state:
            st.session_state['edit_expander'] = False
        if 'select_edit_book' not in st.session_state:
            st.session_state['select_edit_book'] = 'Select a book...'
        if 'remove_expander' not in st.session_state:
            st.session_state['remove_expander'] = False

        st.header('Manage Your Books')

        if st.session_state['add_expander']:
            with st.expander('Add a Book', expanded=True):
                title = st.text_input('Title')
                author = st.text_input('Author')
                daily_goal = st.text_input('Daily Goal')
                start_date = st.date_input('Start Date')
                end_date = st.date_input('End Date', value=None)

                if st.button('Add Book'):
                    if title and author:
                        add_book(session, title, author, start_date, end_date, daily_goal)
                        st.success(f'Book "{title}" was added to the reading list!')
                        time.sleep(1)
                        self.reset_add_selectbox()
                        st.rerun()
                    else:
                        st.warning('Please enter at least a title and author.')
        elif st.button('Add a Book'):
            st.session_state['add_expander'] = True
            st.rerun()

        if st.session_state['edit_expander']:
            with st.expander('Edit a Book', expanded=st.session_state['edit_expander']):
                selected_book_to_edit = st.selectbox('Choose a book to edit',
                                                     ['Select a book...'] + book_titles,
                                                     key='select_edit_book')
                try:
                    selected_split = selected_book_to_edit.split(' by ')
                    selected_book_title = selected_split[0]
                    selected_book_author = selected_split[1]
                    if selected_book_to_edit:
                        book = session.query(Book).filter_by(title=selected_book_title,
                                                             author=selected_book_author).first()

                        new_title = st.text_input('New Title', value=book.title)
                        new_author = st.text_input('New Author', value=book.author)
                        new_start_date = st.date_input('New Start Date', value=book.start_date)
                        new_end_date = st.date_input('New End Date', value=book.end_date)
                        new_daily_goal = st.text_input('New Daily Goal', value=book.daily_goal)

                        if st.button('Update Book'):
                            self.update_book(session, selected_book_title, selected_book_author, new_title,
                                             new_author, new_start_date, new_daily_goal, new_end_date)
                            st.success(f'{new_title} has been updated!')
                            time.sleep(1)
                            st.rerun()
                except IndexError:
                    pass

        elif st.button('Edit a Book'):
            st.session_state['edit_expander'] = True
            st.session_state['select_edit_book'] = 'Select a book...'
            st.rerun()

        if st.session_state['remove_expander']:
            with st.expander('Remove a Book', expanded=True):
                if 'select_remove_book' not in st.session_state:
                    st.session_state['select_remove_book'] = 'Select a book...'
                    st.session_state['confirming_delete'] = False

                selected_book = st.selectbox('Choose a book to remove',
                                             ['Select a book...'] + book_titles,
                                             key='select_remove_book')

                if selected_book == 'Select a book...':
                    st.session_state['confirming_delete'] = False
                else:
                    st.session_state['confirming_delete'] = True

                if st.session_state['confirming_delete']:
                    st.text(f'Are you sure you want to delete?')
                    col1, col2 = st.columns(2)
                    with col1:
                        confirm_delete = st.button('Delete', key='confirm_delete')
                    with col2:
                        cancel_delete = st.button('Cancel', key='cancel_delete', on_click=self.cancel_remove_selectbox)

                    if confirm_delete:
                        selected_split = selected_book.split(' by ')
                        selected_book_title = selected_split[0]
                        selected_book_author = selected_split[1]

                        remove_book(session, selected_book_title, selected_book_author)
                        st.success(f'{selected_book} has been removed!')
                        time.sleep(1)
                        self.reset_remove_selectbox()
                        st.rerun()

                    if cancel_delete:
                        # st.session_state.cancel_delete = 'Select a book...'
                        st.session_state['select_remove_book'] = 'Select a book...'
                        st.session_state['confirming_delete'] = False
                        st.rerun()
        elif st.button('Remove a Book'):
            st.session_state['remove_expander'] = True
            st.session_state['select_remove_book'] = 'Select a book...'
            st.rerun()


class ProgressVisualization:
    def __init__(self, books):
        self.books = books

    def display_grid(self, data):
        st.header('Your reading progress:')

    def display_graph(self, colormap):
        st.header('Reading progress over time: ')
        bar_graph = HorizontalBarGraph()
        figure = bar_graph.plot_reading_progress(self.books, colormap=colormap)
        return figure

    def display_table(self):
        """
        takes the class level data frame and converts it into a table

        :return:
        """
        st.header("Your reading progress:")
        with st.expander(label='Show your progress', expanded=False):
            st.dataframe(self.books, hide_index=True)

    def choose_graph_color(self):
        colormaps = ['Blues', 'Greens', 'Reds', 'Purples', 'Oranges', 'Greys',]

        selected_color = st.selectbox('Choose a chart color:', colormaps,
                                      index=colormaps.index(st.session_state['selected_color']))

        st.session_state['selected_color'] = selected_color

        return selected_color




if __name__ == '__main__':
    # initialize the local session
    session = SessionLocal()
    df = fetch_reading_data(session)

    # get the list of books from the database
    book_list = session.query(Book).all()

    st.header("Ben's Reading Tracker")
    st.subheader("An exercise in reclaiming a sense of direction or at least progress")

