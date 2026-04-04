import streamlit as st

from database import Database

class CheckIn:
    def __init__(self, database: Database):
        self.database = database

    def checkin_service(self):
        st.set_page_config(page_title="Check-in Vôlei", page_icon="🏐")
