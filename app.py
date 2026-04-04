import streamlit as st


try:
    st.title("Bem-vindo ao Sistema de Vôlei")

    # Criando um botão grande para o celular
    if st.button("Ir para o Check-in 🏐", use_container_width=True, type="primary"):
        # O caminho deve ser o nome do arquivo dentro da pasta pages/
        # ou o nome do arquivo principal se for voltar para o início
        st.switch_page("pages/1_checkin.py")
except Exception as e:
    ...
