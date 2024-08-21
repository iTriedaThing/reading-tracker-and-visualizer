import streamlit as st
from backend.database import SessionLocal, Book, add_reading_progress, add_book
from frontend.ui import BookManagementForm

session = SessionLocal()

book_management_form = BookManagementForm()
title, author, start_date, end_date = book_management_form.display_add_form()

if title and author:
    # add a book to the database
    new_book = Book(
        title=title,
        author=author,
        start_date=start_date,
        end_date=end_date
    )
    session.add(new_book)
    session.commit()
    st.success(f"Book '{title}' by {author} added to the list!")

session.close()
