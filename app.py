import streamlit as st
st.title('QA legislação')

main=st.Page('main.py',title='Página Inicial')
documentos = st.Page("document.py", title="Analise de casos")
chats = st.Page("chat.py", title="Chat de dúvidas")

navigator=st.navigation([main,documentos,chats])

navigator.run()
