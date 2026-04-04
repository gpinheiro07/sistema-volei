import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
import pandas as pd

class Database:
    def __init__(self):
        self.sh = self._connect()

    def _connect(self):
        scope = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
        if "gcp_service_account" in st.secrets:
            creds = Credentials.from_service_account_info(st.secrets["gcp_service_account"], scopes=scope)
        else:
            creds = Credentials.from_service_account_file("chave_google.json", scopes=scope)
        client = gspread.authorize(creds)
        return client.open("Sistema_Volei")

    @st.cache_data(ttl=10)
    def get_active_members(_self):
        """Retorna lista de nomes dos jogadores com Status 'Ativo'"""
        aba = _self.sh.worksheet("Jogadores")
        df = pd.DataFrame(aba.get_all_records())
        if df.empty: return []
        return df[df['Status'] == 'Ativo']['Nome'].tolist()

    @st.cache_data(ttl=5)
    def get_checkin_list(_self):
        """Retorna a lista de nomes confirmados para a próxima partida"""
        aba = _self.sh.worksheet("Checkin_Semana")
        dados = aba.get_all_records()
        return [linha['Nome'] for linha in dados] if dados else []

    def update_checkin(_self, lista_nomes):
        """Sobrescreve a aba de checkin com a nova lista"""
        aba = _self.sh.worksheet("Checkin_Semana")
        aba.clear()
        aba.append_row(["Nome"])
        if lista_nomes:
            formato_gspread = [[n] for n in lista_nomes]
            aba.append_rows(formato_gspread)
        st.cache_data.clear() # Limpa o cache para atualizar a UI imediatamente
