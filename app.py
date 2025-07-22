import streamlit as st
import sys
import pysqlite3

st.title('QA legislação')
sys.modules["sqlite3"] = pysqlite3
main=st.Page('main.py',title='Página Inicial')
documentos = st.Page("document.py", title="Analise de casos")
chats = st.Page("chat.py", title="Chat de dúvidas")

navigator=st.navigation([main,documentos,chats])

navigator.run()
