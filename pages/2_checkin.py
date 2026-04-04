import streamlit as st
from database import Database

db = Database()

st.title("🏐 Check-in Semanal")

# Carregando dados
membros_ativos, confirmados = db.get_active_members(), db.get_checkin_list()

# 1. Gestão de Membros (Multiselect)
st.subheader("Confirme sua presença")
# Filtramos apenas quem é membro para o multiselect
membros_confirmados = [n for n in confirmados if n in membros_ativos]

selecao_membros = st.multiselect(
    "Selecione os nomes:",
    options=membros_ativos,
    default=membros_confirmados
)

# 2. Gestão de Convidados (Texto + Adição)
with st.expander("➕ Adicionar Convidado"):
    novo_conv = st.text_input("Nome do convidado")
    if st.button("Adicionar"):
        if novo_conv and novo_conv not in confirmados:
            nova_lista = list(set(confirmados + [novo_conv]))
            db.update_checkin(nova_lista)
            st.rerun()

st.divider()

# 3. Lista de Presença com Opção de Remoção Individual
st.subheader(f"✅ Confirmados ({len(confirmados)})")

if not confirmados:
    st.info("Ninguém confirmado ainda.")
else:
    # Mostramos a lista e permitimos remover um a um (útil para convidados)
    for nome in confirmados:
        col_nome, col_btn = st.columns([0.8, 0.2])
        col_nome.write(f"🔹 {nome}")
        # Botão de remover individual
        if col_btn.button("🗑️", key=f"rem_{nome}"):
            nova_lista = [n for n in confirmados if n != nome]
            db.update_checkin(nova_lista)
            st.rerun()

# 4. Botão de Sincronização Geral (Membros do Multiselect)
if st.button("💾 SALVAR ALTERAÇÕES", use_container_width=True, type="primary"):
    # Mantemos os convidados que já estavam na lista mas não estão no multiselect
    convidados_atuais = [n for n in confirmados if n not in membros_ativos]
    lista_final = list(set(selecao_membros + convidados_atuais))
    
    db.update_checkin(lista_final)
    st.success("Lista sincronizada!")
    st.balloons()
