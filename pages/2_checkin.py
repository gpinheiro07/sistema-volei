import streamlit as st
from database import Database

db = Database()

# Inicializa a lista provisória com o que está no banco na primeira carga
if "lista_provisoria" not in st.session_state:
    st.session_state.lista_provisoria = db.get_checkin_list()

st.title("🏐 Check-in Vôlei")
st.subheader("Garanta sua vaga nos 24!")

# --- ENTRADA DE NOMES ---
# Campo de texto único para qualquer pessoa
novo_nome = st.text_input("Digite o nome para adicionar (Seu ou Convidado):")

if st.button("Adicionar à Lista ➕", use_container_width=True):
    if not novo_nome:
        st.warning("Digite um nome primeiro!")
    elif novo_nome in st.session_state.lista_provisoria:
        st.error("Este nome já está na lista!")
    elif len(st.session_state.lista_provisoria) >= 24:
        st.error("Ops! A lista já está lotada (24/24).")
    else:
        st.session_state.lista_provisoria.append(novo_nome)
        st.rerun()

st.divider()

# --- BOTÃO DE SALVAMENTO FINAL ---
# Só este botão gasta "créditos" de escrita no Google Sheets
if st.button("🚀 CONFIRMAR E SALVAR LISTA", type="primary", use_container_width=True):
    db.update_checkin(st.session_state.lista_provisoria)
    st.success("Lista sincronizada com sucesso!")
    st.balloons()

# --- EXIBIÇÃO DOS 24 SLOTS ---
st.write(f"### Vagas Preenchidas: {len(st.session_state.lista_provisoria)}/24")

# Criamos a visualização dos 24 lugares
for i in range(1, 25):
    with st.container():
        # Se o slot estiver ocupado
        if i <= len(st.session_state.lista_provisoria):
            nome_da_vez = st.session_state.lista_provisoria[i-1]
            col_txt, col_del = st.columns([0.85, 0.15])
            
            col_txt.write(f"**{i}.** ✅ {nome_da_vez}")
            
            # Botão de remover (Lixeira) para corrigir erros antes de salvar
            if col_del.button("🗑️", key=f"btn_del_{i}"):
                st.session_state.lista_provisoria.remove(nome_da_vez)
                st.rerun()
        else:
            # Slot vazio
            st.write(f"*{i}.* 📭 Disponível")
