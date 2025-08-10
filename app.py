import streamlit as st
__import__('pysqlite3')
import sys
sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')

st.title('QA legislação')

main=st.Page('main.py',title='Página Inicial')
documentos = st.Page("document.py", title="Analise de casos Versão 01")
chats = st.Page("chat.py", title="Chat de dúvidas Versão 01")
documentos_agosto = st.Page("document_v02.py", title="Analise de casos Versão 02")
chats_agosto = st.Page("chat_v02.py", title="Chat de dúvidas Versão 02")

navigator=st.navigation([main,documentos,chats, documentos_agosto,chats_agosto])

navigator.run()
