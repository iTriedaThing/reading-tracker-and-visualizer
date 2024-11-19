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
    """
    A class that represents a form for displaying the reading progress of books.

    Attributes:
        books (list): A list containing book details. Each book can be a dictionary or any object
                      representing book data.
    """

    def __init__(self, books: list):
        """
        Initializes the ReadingProgressForm with a list of books.

        Args:
            books (list): A list of books to track reading progress.
        """
        self.books = books  # Store the provided list of books as an instance attribute.

    def display(self):
        """
        Displays the list of books using a Streamlit interface.

        If no books are available, an informational message is displayed. Otherwise,
        the books are shown in a table format.

        Returns:
            None
        """
        # Check if the list of books is empty.
        if not self.books:
            # Display an info message if no books are present.
            st.info('No books available. Please add a book first.')
            return  # Exit the function early if no books to display.
        else:
            # Display the list of books in a tabular format.
            st.table(data=self.books)


class ReadingInputForm:
    """
    A form to input reading progress for a list of books.

    Attributes:
        books (list): A list of book objects with details such as bookId, title, and author.
        selected_book (str): The ID of the book selected by the user.
        progress_date (date): The date associated with the reading progress.
        pages_read (int): The number of pages read by the user.
        date_selection (str): Option for selecting the date ('Today' or 'Another day').
    """

    def __init__(self, books: list):
        """
        Initializes the ReadingInputForm with a list of books and default values for
        other attributes.

        Args:
            books (list): A list of book objects.
        """
        self.books = books  # Store the list of books as an instance attribute.
        self.selected_book = None  # To store the selected book ID.
        self.progress_date = date.today()  # Default progress date is today.
        self.pages_read = 0  # Default number of pages read is 0.
        self.date_selection = 'Today'  # Default selection for date input is 'Today'.

    def display(self, session):
        """
        Displays the input form for capturing reading progress using Streamlit.

        If no books are available, an informational message is displayed. Otherwise, the form
        allows the user to select a book, input the date of reading, and specify the number of
        pages read. Upon submission, the progress is added to the session.

        Args:
            session: The session object for tracking reading progress.

        Returns:
            None
        """
        # Check if there are books available to display.
        if not self.books:
            st.info('No books available. Please add a book first.')  # Display info message if no books.
            return  # Exit early if no books to show.

        # Create a dictionary of book options with bookId as keys and formatted strings as values.
        book_options = {book.booksId: f'{book.title} ({book.author})' for book in self.books}

        # Display a dropdown (selectbox) to choose a book.
        selected_option = st.selectbox('What book did you read today?', list(book_options.values()))

        # Find the ID of the selected book based on the user's selection.
        self.selected_book = [key for key, value in book_options.items() if value == selected_option][0]

        # Display a radio button group to select the reading date (Today or Another day).
        self.date_selection = st.radio('When did you read?',
                                       options=['Today', 'Another day'],  # Two options for date input.
                                       horizontal=True)  # Display options horizontally.

        # Determine the reading date based on the user's selection.
        if self.date_selection == 'Today':
            self.progress_date = date.today()  # Set to today's date if 'Today' is selected.
        else:
            # Allow the user to pick a date if 'Another day' is selected.
            self.progress_date = st.date_input('Select date', self.progress_date)

        # Allow the user to input the number of pages read.
        self.pages_read = st.number_input('How many pages did you read?', min_value=0)

        # Display a text prompt asking if the user has completed their reading.
        st.text('Did you finish doing some reading?')

        # Add a button that submits the reading progress when clicked.
        if st.button('Yes!'):
            # Call the `add_reading_progress` function to log the progress.
            add_reading_progress(session, self.selected_book, self.progress_date, self.pages_read)

            # Refresh the Streamlit application to reflect changes.
            st.rerun()


class BookManagementForm:
    """
    A form for managing a collection of books, including adding, removing, and editing book details.

    Attributes:
        books (list): A list containing the current collection of books.
    """

    def __init__(self, books):
        """
        Initializes the BookManagementForm with a list of books.

        Args:
            books (list): The current collection of books to be managed.
        """
        self.books = books  # Store the list of books as an instance attribute.

    def reset_add_selectbox(self):
        """
        Resets the 'Add' expander UI state in the Streamlit session state.

        This function is used to collapse or hide the 'Add Book' expander UI element.
        """
        st.session_state['add_expander'] = False  # Set the 'Add' expander state to False.

    def reset_remove_selectbox(self):
        """
        Resets the 'Remove' expander UI state in the Streamlit session state.

        This function is used to collapse or hide the 'Remove Book' expander UI element.
        """
        st.session_state['remove_expander'] = False  # Set the 'Remove' expander state to False.

    def cancel_remove_selectbox(self):
        """
        Resets the book selection dropdown in the 'Remove Book' UI to its default state.

        This ensures that no book remains selected after canceling the remove operation.
        """
        st.session_state['select_remove_book'] = 'Select a book...'  # Reset the selection to default text.

    def reset_edit_selectbox(self):
        """
        Resets the 'Edit' expander UI state in the Streamlit session state.

        This function is used to collapse or hide the 'Edit Book' expander UI element.
        """
        st.session_state['edit_expander'] = False  # Set the 'Edit' expander state to False.

    def update_book(self, session, selected_book_title, selected_book_author, new_title,
                    new_author, new_start_date, new_daily_goal, new_end_date):
        """
        Updates the details of a selected book and resets the 'Edit' expander UI.

        Args:
            session: The current Streamlit session, used for managing application state.
            selected_book_title (str): The title of the book to be updated.
            selected_book_author (str): The author of the book to be updated.
            new_title (str): The new title for the book.
            new_author (str): The new author for the book.
            new_start_date (date): The new start date for the book.
            new_daily_goal (int): The new daily reading goal for the book.
            new_end_date (date): The new end date for the book.

        Returns:
            None
        """
        # Call the `edit_book` function to update the book's details.
        edit_book(session, selected_book_title, selected_book_author, new_title,
                  new_author, new_start_date, new_daily_goal, new_end_date)

        # Reset the 'Edit' expander UI after updating the book.
        self.reset_edit_selectbox()

    def display(self, session):
        """
        Displays the book management interface, allowing users to add, edit, or remove books.

        This method uses Streamlit to create an interactive UI for managing a collection of books.

        Args:
            session: The current database session used to query and manipulate book records.

        Returns:
            None
        """
        # Generate a list of book titles and authors for dropdown options.
        book_titles = [f'{book.title} by {book.author}' for book in self.books]

        # Ensure necessary session state variables are initialized.
        if 'add_expander' not in st.session_state:
            st.session_state['add_expander'] = False
        if 'edit_expander' not in st.session_state:
            st.session_state['edit_expander'] = False
        if 'select_edit_book' not in st.session_state:
            st.session_state['select_edit_book'] = 'Select a book...'
        if 'remove_expander' not in st.session_state:
            st.session_state['remove_expander'] = False

        # Main section header.
        st.header('Manage Your Books')

        # ---------- Add a Book Section ----------
        if st.session_state['add_expander']:
            with st.expander('Add a Book', expanded=True):
                # Inputs for adding a book.
                title = st.text_input('Title')
                author = st.text_input('Author')
                daily_goal = st.text_input('Daily Goal')
                start_date = st.date_input('Start Date')
                end_date = st.date_input('End Date', value=None)

                if st.button('Add Book'):
                    if title and author:
                        # Add the book to the database using a helper function.
                        add_book(session, title, author, start_date, end_date, daily_goal)
                        st.success(f'Book "{title}" was added to the reading list!')
                        time.sleep(1)  # Brief delay for user feedback.
                        self.reset_add_selectbox()  # Reset the 'Add' expander state.
                        st.rerun()  # Refresh the app to reflect changes.
                    else:
                        # Warn the user if mandatory fields are missing.
                        st.warning('Please enter at least a title and author.')
        elif st.button('Add a Book'):
            # Expand the 'Add a Book' section when the button is clicked.
            st.session_state['add_expander'] = True
            st.rerun()

        # ---------- Edit a Book Section ----------
        if st.session_state['edit_expander']:
            with st.expander('Edit a Book', expanded=st.session_state['edit_expander']):
                # Dropdown for selecting a book to edit.
                selected_book_to_edit = st.selectbox(
                    'Choose a book to edit',
                    ['Select a book...'] + book_titles,
                    key='select_edit_book'
                )
                try:
                    # Split the selected book string to extract title and author.
                    selected_split = selected_book_to_edit.split(' by ')
                    selected_book_title = selected_split[0]
                    selected_book_author = selected_split[1]

                    if selected_book_to_edit:
                        # Query the selected book from the database.
                        book = session.query(Book).filter_by(
                            title=selected_book_title,
                            author=selected_book_author
                        ).first()

                        # Inputs for updating book details.
                        new_title = st.text_input('New Title', value=book.title)
                        new_author = st.text_input('New Author', value=book.author)
                        new_start_date = st.date_input('New Start Date', value=book.start_date)
                        new_end_date = st.date_input('New End Date', value=book.end_date)
                        new_daily_goal = st.text_input('New Daily Goal', value=book.daily_goal)

                        if st.button('Update Book'):
                            # Update the book in the database.
                            self.update_book(
                                session, selected_book_title, selected_book_author,
                                new_title, new_author, new_start_date, new_daily_goal, new_end_date
                            )
                            st.success(f'{new_title} has been updated!')
                            time.sleep(1)  # Brief delay for user feedback.
                            st.rerun()  # Refresh the app to reflect changes.
                except IndexError:
                    # Handle cases where no valid book is selected.
                    pass
        elif st.button('Edit a Book'):
            # Expand the 'Edit a Book' section when the button is clicked.
            st.session_state['edit_expander'] = True
            st.session_state['select_edit_book'] = 'Select a book...'
            st.rerun()

        # ---------- Remove a Book Section ----------
        if st.session_state['remove_expander']:
            with st.expander('Remove a Book', expanded=True):
                # Initialize session state variables for remove operations.
                if 'select_remove_book' not in st.session_state:
                    st.session_state['select_remove_book'] = 'Select a book...'
                    st.session_state['confirming_delete'] = False

                # Dropdown for selecting a book to remove.
                selected_book = st.selectbox(
                    'Choose a book to remove',
                    ['Select a book...'] + book_titles,
                    key='select_remove_book'
                )

                # Determine whether a book is selected for removal.
                if selected_book == 'Select a book...':
                    st.session_state['confirming_delete'] = False
                else:
                    st.session_state['confirming_delete'] = True

                if st.session_state['confirming_delete']:
                    # Display confirmation prompt.
                    st.text(f'Are you sure you want to delete?')
                    col1, col2 = st.columns(2)

                    with col1:
                        # Confirm delete button.
                        confirm_delete = st.button('Delete', key='confirm_delete')
                    with col2:
                        # Cancel delete button with associated action.
                        cancel_delete = st.button(
                            'Cancel',
                            key='cancel_delete',
                            on_click=self.cancel_remove_selectbox
                        )

                    if confirm_delete:
                        # Extract title and author from the selected book.
                        selected_split = selected_book.split(' by ')
                        selected_book_title = selected_split[0]
                        selected_book_author = selected_split[1]

                        # Remove the book from the database.
                        remove_book(session, selected_book_title, selected_book_author)
                        st.success(f'{selected_book} has been removed!')
                        time.sleep(1)  # Brief delay for user feedback.
                        self.reset_remove_selectbox()  # Reset the 'Remove' expander state.
                        st.rerun()  # Refresh the app to reflect changes.

                    if cancel_delete:
                        # Reset session state for cancel action.
                        st.session_state['select_remove_book'] = 'Select a book...'
                        st.session_state['confirming_delete'] = False
                        st.rerun()
        elif st.button('Remove a Book'):
            # Expand the 'Remove a Book' section when the button is clicked.
            st.session_state['remove_expander'] = True
            st.session_state['select_remove_book'] = 'Select a book...'
            st.rerun()

class ProgressVisualization:
    """
    A class to visualize reading progress through grids, graphs, and tables.

    Attributes:
        books (list or DataFrame): The collection of books and their associated reading progress.
    """

    def __init__(self, books):
        """
        Initializes the ProgressVisualization class with a list or DataFrame of books.

        Args:
            books (list or DataFrame): The collection of books with their progress data.
        """
        self.books = books  # Store the books data as an instance attribute.

    def display_grid(self, data):
        """
        Displays a grid-based representation of reading progress.

        Args:
            data (any): Placeholder for data used in a grid visualization.

        Returns:
            None
        """
        st.header('Your reading progress:')  # Display the header for the grid.

    def display_graph(self, colormap):
        """
        Displays a bar graph of reading progress over time.

        Args:
            colormap (str): The colormap to use for the bar graph (e.g., 'Blues', 'Greens').

        Returns:
            matplotlib.figure.Figure: The generated bar graph figure.
        """
        st.header('Reading progress over time: ')  # Display the header for the graph.

        # Instantiate a HorizontalBarGraph object for plotting.
        bar_graph = HorizontalBarGraph()

        # Generate the graph using the books data and selected colormap.
        figure = bar_graph.plot_reading_progress(self.books, colormap=colormap)

        return figure  # Return the graph figure for further use or display.

    def display_table(self):
        """
        Displays a table showing reading progress.

        Converts the books data into a Streamlit dataframe and allows the user to expand or collapse the view.

        Returns:
            None
        """
        st.header("Your reading progress:")  # Display the header for the table.

        # Use an expander to show or hide the progress table.
        with st.expander(label='Show your progress', expanded=False):
            st.dataframe(self.books, hide_index=True)  # Display the books data as a Streamlit dataframe.

    def choose_graph_color(self):
        """
        Allows the user to select a color scheme for the graph.

        Provides a dropdown menu of colormaps to customize the graph's appearance.

        Returns:
            str: The selected colormap.
        """
        # List of available colormap options for the graph.
        colormaps = ['Blues', 'Greens', 'Reds', 'Purples', 'Oranges', 'Greys']

        # Dropdown menu for selecting a colormap, with the default value from session state.
        selected_color = st.selectbox(
            'Choose a chart color:',
            colormaps,
            index=colormaps.index(st.session_state['selected_color'])
        )

        # Update the session state with the newly selected colormap.
        st.session_state['selected_color'] = selected_color

        return selected_color  # Return the selected colormap.a


if __name__ == '__main__':
    # initialize the local session
    session = SessionLocal()
    df = fetch_reading_data(session)

    # get the list of books from the database
    book_list = session.query(Book).all()

    st.header("Ben's Reading Tracker")
    st.subheader("An exercise in reclaiming a sense of direction or at least progress")

