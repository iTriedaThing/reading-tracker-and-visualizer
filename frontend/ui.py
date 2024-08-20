import streamlit as st
from datetime import date


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

    def display_add_form(self):
        st.text('Do you have a book to add?')
        columns = st.columns([4, 2])
        with columns[0]:
            self.title = st.text_input(label='title', label_visibility='hidden', placeholder='Title')
        with columns[1]:
            self.author = st.text_input(label='author', label_visibility='hidden', placeholder='Author')
        if st.button('Add my book!'):
            pass

    def display_remove_form(self, books: list):
        st.header('Do you want to remove a book?')

        book_titles = [book[0] for book in books]
        selected_book = st.selectbox('Choose a book to remove:', book_titles)

        if st.button('Remove book'):
            return selected_book


class ProgressVisualization:
    def __init__(self):
        self.book_id = None

    def display_grid(self, data):
        st.header('Your reading progress:')

    def display_graph(self, data):
        st.header('Reading progress over time: ')


if __name__ == '__main__':
    book_list = [
        ["To Kill a Mockingbird", "Harper Lee"],
        ["1984", "George Orwell"],
        ["The Great Gatsby", "F. Scott Fitzgerald"],
        ["Pride and Prejudice", "Jane Austen"],
        ["Moby-Dick", "Herman Melville"]
    ]
    opt1, opt2, opt3 = ReadingInputForm(book_list).display()
    opt4 = BookManagementForm().display_remove_form(book_list)
    ProgressVisualization().display_grid(0)
    ProgressVisualization().display_graph(0)

    if opt1:
        print('Book title: ' + opt1)
        print('Progress date: ' + str(opt2))
        print('Pages read: ' + str(opt3))

    if opt4:
        print('Book to remove: ' + opt4)

