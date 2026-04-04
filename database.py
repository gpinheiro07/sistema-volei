import gspread
import pandas as pd
import streamlit as st
from google.oauth2.service_account import Credentials


class Database:
    def __init__(self):
        self.spread_sheet = self._connect()

    def _connect(self):
        scope = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
        if "gcp_service_account" in st.secrets:
            creds = Credentials.from_service_account_info(st.secrets["gcp_service_account"], scopes=scope)
        else:
            creds = Credentials.from_service_account_file("chave_google.json", scopes=scope)
        
        client = gspread.authorize(creds)
        return client.open("Sistema_Volei")

    @st.cache_data(ttl=10)
    def get_players_checkin(self):
        # Pegar quem já confirmou no Check-in
        aba_c = self.spread_sheet.worksheet("Checkin")
        dados_c = aba_c.get_all_records()
        confirmados_atualmente = [linha['Nome'] for linha in dados_c] if dados_c else []
        return confirmados_atualmente

    @st.cache_data(ttl=10)
    def get_all_players_registered(self):
        # Pegar todos os jogadores cadastrados e ativos
        df_j = pd.DataFrame(self.spread_sheet.worksheet("Jogadores").get_all_records())
        membros_ativos = df_j[df_j['Status'] == 'Ativo']['Nome'].tolist() if not df_j.empty else []
        return sorted(membros_ativos)
