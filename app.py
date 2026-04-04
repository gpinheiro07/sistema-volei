import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
import pandas as pd

# --- 1. CONFIGURAÇÃO DE CONEXÃO ---
def conectar():
    scope = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
    # Usando st.secrets para segurança (será configurado no site do Streamlit)
    creds = Credentials.from_service_account_info(st.secrets["gcp_service_account"], scopes=scope)
    client = gspread.authorize(creds)
    return client.open("Sistema_Volei")

# --- 2. FUNÇÕES DE BANCO DE DATA (Sincronização) ---
@st.cache_data(ttl=10) # Verifica novos dados a cada 10 segundos
def buscar_dados_planilha():
    sh = conectar()
    # Busca membros ativos para o dropdown
    df_jogadores = pd.DataFrame(sh.worksheet("Jogadores").get_all_records())
    membros = df_jogadores[df_jogadores['Status'] == 'Ativo']['Nome'].tolist()
    
    # Busca quem já confirmou presença hoje
    df_presenca = pd.DataFrame(sh.worksheet("Presenca_Semana").get_all_records())
    confirmados = df_presenca['Nome'].tolist()
    
    return membros, confirmados

def salvar_presenca(lista_nomes):
    sh = conectar()
    aba = sh.worksheet("Presenca_Semana")
    aba.clear() # Limpa a lista antiga
    aba.append_row(["Nome", "Ja_Votou"]) # Recria o cabeçalho
    
    if lista_nomes:
        # Prepara os dados: Nome e False (ainda não votou)
        dados_novos = [[nome, False] for nome in lista_nomes]
        aba.append_rows(dados_novos)
    
    st.cache_data.clear() # Força o app a ler os dados novos após salvar

# --- 3. INTERFACE STREAMLIT ---
st.set_page_config(page_title="Vôlei Check-in", page_icon="🏐")

st.title("🏐 Check-in da Partida")
st.write("Selecione seu nome abaixo para confirmar presença.")

try:
    membros_disponiveis, ja_confirmados = buscar_dados_planilha()

    # Seleção de Membros
    selecionados = st.multiselect(
        "Membros Confirmados:",
        options=sorted(membros_disponiveis),
        default=[n for n in ja_confirmados if n in membros_disponiveis]
    )

    # Input de Convidados
    with st.expander("➕ Adicionar Convidado"):
        novo_convidado = st.text_input("Nome do Convidado")
        if st.button("Inserir Convidado"):
            if novo_convidado and novo_convidado not in selecionados:
                # Adicionamos o convidado à lista temporária
                ja_confirmados.append(novo_convidado)
                salvar_presenca(list(set(selecionados + ja_confirmados)))
                st.rerun()

    st.divider()

    # Botão de Sincronização Principal
    if st.button("💾 CONFIRMAR LISTA ATUAL", use_container_width=True, type="primary"):
        salvar_presenca(selecionados)
        st.success("Lista sincronizada com a Planilha!")
        st.balloons()

    # Visualização Final
    st.subheader(f"👥 Total: {len(selecionados)} jogadores")
    for i, nome in enumerate(selecionados, 1):
        st.write(f"{i}. {nome}")

except Exception as e:
    st.error("Erro ao conectar com a planilha. Verifique as configurações.")
    st.exception(e)
