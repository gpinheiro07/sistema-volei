import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
import pandas as pd


# --- CONFIGURAÇÃO DE CONEXÃO ---
def conectar():
    scope = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
    # No Streamlit Cloud, use st.secrets. Localmente, use o caminho do seu JSON.
    if "gcp_service_account" in st.secrets:
        creds = Credentials.from_service_account_info(st.secrets["gcp_service_account"], scopes=scope)
    else:
        creds = Credentials.from_service_account_file("chave_google.json", scopes=scope)
    
    client = gspread.authorize(creds)
    return client.open("Sistema_Volei")

# --- BUSCA DE DADOS (CACHE DE 10 SEG) ---
@st.cache_data(ttl=10)
def carregar_dados():
    sh = conectar()
    
    # 1. Pegar todos os jogadores cadastrados e ativos
    df_j = pd.DataFrame(sh.worksheet("Jogadores").get_all_records())
    membros_ativos = df_j[df_j['Status'] == 'Ativo']['Nome'].tolist() if not df_j.empty else []
    
    # 2. Pegar quem já confirmou no Check-in
    aba_c = sh.worksheet("Checkin")
    dados_c = aba_c.get_all_records()
    confirmados_atualmente = [linha['Nome'] for linha in dados_c] if dados_c else []
    
    return sorted(membros_ativos), confirmados_atualmente

# --- SALVAR NO GOOGLE SHEETS ---
def atualizar_banco_checkin(lista_final):
    sh = conectar()
    aba = sh.worksheet("Checkin")
    
    # Limpa e reescreve (Estratégia mais segura para evitar duplicatas)
    aba.clear()
    aba.append_row(["Nome"]) 
    if lista_final:
        # Formata para o gspread: lista de listas [[nome1], [nome2]]
        formatado = [[n] for n in lista_final]
        aba.append_rows(formatado)
    
    st.cache_data.clear() # Limpa o cache para atualizar a tela na hora

# --- INTERFACE RESPONSIVA ---
st.set_page_config(page_title="Check-in Vôlei", page_icon="🏐")

st.title("🏐 Lista de Presença")
st.write("Selecione seu nome para confirmar no próximo jogo.")

try:
    ativos, ja_confirmados = carregar_dados()

    # 1. MULTISELECT (O coração do Check-in)
    # Mostra todos os ativos. O 'default' são os que já estão na aba Checkin
    selecao = st.multiselect(
        "Quem vai jogar?",
        options=ativos,
        default=[n for n in ja_confirmados if n in ativos],
        help="Toque no nome para adicionar ou no 'X' para remover."
    )

    # 2. ADICIONAR CONVIDADO (Para quem não está no banco)
    with st.expander("➕ Adicionar Convidado (Externo)"):
        nome_conv = st.text_input("Nome do Convidado:")
        if st.button("Incluir Convidado"):
            if nome_conv and nome_conv not in ja_confirmados:
                ja_confirmados.append(nome_conv)
                # Salva a união dos selecionados + o novo convidado
                atualizar_banco_checkin(list(set(selecao + ja_confirmados)))
                st.rerun()

    st.divider()

    # 3. BOTÃO DE AÇÃO (Salvar)
    if st.button("💾 CONFIRMAR MINHA PRESENÇA", use_container_width=True, type="primary"):
        # Aqui salvamos exatamente o que está no multiselect + convidados mantidos
        convidados_extras = [n for n in ja_confirmados if n not in ativos]
        lista_final = list(set(selecao + convidados_extras))
        
        atualizar_banco_checkin(lista_final)
        st.success("Presença sincronizada!")
        st.balloons()

    # 4. LISTA VISUAL (Para conferência rápida)
    st.subheader(f"✅ Confirmados: {len(ja_confirmados)}")
    if ja_confirmados:
        for i, nome in enumerate(ja_confirmados, 1):
            st.write(f"{i}. {nome}")
    else:
        st.info("Nenhum nome na lista ainda.")

except Exception as e:
    st.error("Erro de conexão. Verifique se as abas 'Jogadores' e 'Checkin' existem.")
    st.stop()
