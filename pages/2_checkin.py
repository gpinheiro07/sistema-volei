import streamlit as st
from database import Database

db = Database()

# Inicializa estados
if "lista_provisoria" not in st.session_state:
    st.session_state.lista_provisoria = db.get_checkin_list()

# Busca a lista de jogadores cadastrados no banco para o Dropdown
# Supondo que você tenha um método get_all_players() que retorna uma lista de strings
if "jogadores_cadastrados" not in st.session_state:
    st.session_state.jogadores_cadastrados = db.get_active_members()

st.title("🏐 Check-in Vôlei")
st.subheader("Garanta sua vaga nos 24!")

# --- ENTRADA DE NOMES ---
st.write("### Adicionar Jogador")
tipo_registro = st.radio("Selecione o tipo:", ["Cadastrado", "Convidado"], horizontal=True)

nome_para_adicionar = None

if tipo_registro == "Cadastrado":
    # Filtra os cadastrados que ainda não estão na lista provisória para evitar duplicatas no select
    opcoes = [p for p in st.session_state.jogadores_cadastrados if p not in st.session_state.lista_provisoria]
    nome_para_adicionar = st.selectbox("Selecione o nome:", [""] + opcoes)
else:
    nome_para_adicionar = st.text_input("Digite o nome do convidado:")

if st.button("Adicionar à Lista ➕", use_container_width=True):
    if not nome_para_adicionar or nome_para_adicionar == "":
        st.warning("Selecione ou digite um nome!")
    elif nome_para_adicionar in st.session_state.lista_provisoria:
        st.error("Este nome já está na lista!")
    elif len(st.session_state.lista_provisoria) >= 24:
        st.error("Ops! A lista já está lotada (24/24).")
    else:
        st.session_state.lista_provisoria.append(nome_para_adicionar)
        st.rerun()

st.divider()

# --- BOTÃO DE SALVAMENTO FINAL ---
if st.button("🚀 CONFIRMAR E SALVAR LISTA", type="primary", use_container_width=True):
    # Aqui o db.update_checkin deve estar preparado para receber a lista final
    db.update_checkin(st.session_state.lista_provisoria)
    st.success("Lista sincronizada com sucesso!")
    st.balloons()

# --- EXIBIÇÃO DOS 24 SLOTS ---
st.write(f"### Vagas Preenchidas: {len(st.session_state.lista_provisoria)}/24")

for i in range(1, 25):
    with st.container():
        if i <= len(st.session_state.lista_provisoria):
            nome_da_vez = st.session_state.lista_provisoria[i-1]
            col_txt, col_del = st.columns([0.85, 0.15])
            
            # Diferencia visualmente quem é convidado (opcional)
            is_convidado = nome_da_vez not in st.session_state.jogadores_cadastrados
            label = f"👤 {nome_da_vez} (Convidado)" if is_convidado else f"✅ {nome_da_vez}"
            
            col_txt.write(f"**{i}.** {label}")
            
            if col_del.button("🗑️", key=f"btn_del_{i}"):
                st.session_state.lista_provisoria.remove(nome_da_vez)
                st.rerun()
        else:
            st.write(f"*{i}.* 📭 Disponível")
