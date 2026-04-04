import streamlit as st
from database import Database

db = Database()

# --- ESTADO DA SESSÃO (Para acumular nomes antes de salvar) ---
if "lista_provisoria" not in st.session_state:
    # Ao carregar, puxamos o que já está no banco
    _, confirmados_banco = db.get_active_members(), db.get_checkin_list()
    st.session_state.lista_provisoria = confirmados_banco

st.title("🏐 Check-in (Limite: 24 Vagas)")

# Carregar dados para os menus
membros_ativos, _ = db.get_active_members()

# --- 1. ADICIONAR NOMES À LISTA PROVISÓRIA ---
st.subheader("Quem vais adicionar?")

# Selecionar Membros
selecao_membros = st.multiselect(
    "Selecionar Membros:",
    options=membros_ativos,
    default=[n for n in st.session_state.lista_provisoria if n in membros_ativos]
)

# Adicionar Convidados (Vários)
col_input, col_add = st.columns([0.7, 0.3])
with col_input:
    nome_convidado = st.text_input("Nome do Convidado:", key="input_conv")
with col_add:
    st.write(" ") # Alinhamento
    if st.button("Adicionar ➕"):
        if nome_convidado and nome_convidado not in st.session_state.lista_provisoria:
            # Apenas adiciona à lista na memória do telemóvel
            st.session_state.lista_provisoria.append(nome_convidado)
            st.rerun()

# --- 2. BOTÃO DE CONFIRMAÇÃO FINAL (Grava no Google) ---
st.divider()

# Atualizamos a lista provisória com o que foi marcado no multiselect
convidados_na_lista = [n for n in st.session_state.lista_provisoria if n not in membros_ativos]
lista_para_salvar = list(set(selecao_membros + convidados_na_lista))

if st.button("🚀 CONFIRMAR TODAS AS PRESENÇAS", use_container_width=True, type="primary"):
    if len(lista_para_salvar) > 24:
        st.error(f"Erro: A lista tem {len(lista_para_salvar)} nomes. O limite é 24!")
    else:
        db.update_checkin(lista_para_salvar)
        st.session_state.lista_provisoria = lista_para_salvar
        st.success("Presenças confirmadas com sucesso!")
        st.balloons()

# --- 3. EXIBIÇÃO DOS 24 LUGARES ---
st.subheader("📋 Lista de Chamada (24 Vagas)")

# Criamos 24 "slots" visuais
for i in range(1, 25):
    # Se já houver alguém naquela posição, mostra o nome
    if i <= len(st.session_state.lista_provisoria):
        nome = st.session_state.lista_provisoria[i-1]
        col_n, col_del = st.columns([0.9, 0.1])
        col_n.write(f"**{i}.** ✅ {nome}")
        # Botão para remover da lista provisória antes de salvar
        if col_del.button("🗑️", key=f"del_{i}"):
            st.session_state.lista_provisoria.remove(nome)
            st.rerun()
    else:
        # Mostra o lugar vazio
        st.write(f"*{i}.* 📭 Disponível")

# Aviso se exceder
if len(st.session_state.lista_provisoria) > 24:
    st.warning(f"Atenção: Existem {len(st.session_state.lista_provisoria) - 24} pessoas na lista de espera!")
