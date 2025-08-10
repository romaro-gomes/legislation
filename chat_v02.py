import streamlit as st

import os
import sys
from dotenv import load_dotenv
 
import ollama
from langchain_core.messages import AIMessage, HumanMessage,SystemMessage
from langchain_groq import ChatGroq
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma

import pysqlite3
sys.modules["sqlite3"] = pysqlite3 


load_dotenv()

CHROMA_PATH = st.secrets["CHROMA_PATH"]
MODEL_NAME = st.secrets["MODEL_NAME"]
GROQ_API_KEY = st.secrets["GROQ_API_KEY"]

embedding_model = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
model_name = "maritaca-ai/sabia-7b"

embeddings= HuggingFaceEmbeddings(model_name=embedding_model,model_kwargs={"device": "cpu"})


llm=ChatGroq(
        model_name=MODEL_NAME,
        temperature=0.2,
        api_key=GROQ_API_KEY)


vector_store = Chroma(
    collection_name="base_agosto",
    embedding_function=embeddings,
    persist_directory=CHROMA_PATH
)

if 'messages' not in st.session_state:
    st.session_state.messages=[]
    st.session_state.messages.append(SystemMessage("""
    Você é um assistente especializado:
    - Direito societário (sociedades limitadas e S/A de capital fechado) - aqui entram as estruturas de SPE e SCP
    -Direito contratual
    -direito tributário , voltado pra tributos como (IR sobre o ganho de capital, IRPF , itcmd e ITBI ) esses são os principais tributos que envolvem a temática
    -direito regulatório (principalmente CVM - com a questão de oferta pública de investimentos )
        e áreas macros são : direito empresarial e civil ..

    Você irá analisar:
    -contratos
    -decisões judiciais
    -casos que chegam ao consultorio
    -documentações

    Você deve responder perguntas com base no contexto apresentado.Caso você não saiba a resposta, seja honesto e diga que não sabe responder.NUNCA DIGA PARA PROCURAR UM ESPECIALISTA OU OUTRO PROFISSIONAL. Não cite que sua resposta é baseada no contexto, mas sim na legislação e jurisprudência brasileira.
      - Há algo incorreto do ponto de vista legal?
      - Como você interpreta o caso de um ponto de vista legal.
      - Como ele poderia ser resolvido.

                                                   """))

for message in st.session_state.messages:
    if isinstance(message,HumanMessage):
        with st.chat_message('user'):
            st.markdown(message.content)
    elif isinstance(message,AIMessage):
        with st.chat_message('assistant'):
            st.markdown(message.content)

prompt=st.chat_input('Como posso lhe ajudar?')

if prompt:
    with st.chat_message('user'):
        st.markdown(prompt)
        st.session_state.messages.append(HumanMessage(prompt))

    docs= vector_store.similarity_search(prompt,k=1)
        
    docs_text=''.join(doc.page_content for doc in docs)
    
    print(docs_text)
    st.session_state.messages.append(SystemMessage(docs_text)
                                     )
    print(st.session_state.messages)
    result = llm.invoke(st.session_state.messages).content

    with st.chat_message("assistant"):
        st.markdown(result)

        st.session_state.messages.append(AIMessage(result))






