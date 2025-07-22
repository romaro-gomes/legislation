import streamlit as st

import os
import sys
from dotenv import load_dotenv

import ollama
from langchain_core.messages import AIMessage, HumanMessage,SystemMessage
from langchain_groq import ChatGroq
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma

import instructor
from enum import Enum
from pydantic import BaseModel, Field
from typing_extensions import Literal
from groq import Groq

from llama_cloud_services import LlamaParse
import tempfile

import pandas as pd
import plotly.express as px

from datetime import date,datetime


import pysqlite3
sys.modules["sqlite3"] = pysqlite3 
load_dotenv()

CHROMA_PATH = st.secrets["CHROMA_PATH"]
MODEL_NAME = st.secrets["MODEL_NAME"]
GROQ_API_KEY = st.secrets["GROQ_API_KEY"]
LLAMA_CLOUD_API_KEY = st.secrets["LLAMAINDEX_KEY"]

converter = LlamaParse(
    api_key=LLAMA_CLOUD_API_KEY,  
    num_workers=4,       
    verbose=False,
    language="pt",       
)

client_groq = instructor.patch(Groq())

json=None

if 'df' not in st.session_state:
    st.session_state.df = pd.DataFrame(columns=['nome','legalidade','data_da_analise', 'analise'])




class Legalidade(str,Enum):
  legal='legal'
  ilegal='ilegal'

class LegalStatus(BaseModel):
  "Embase a análise apartir do texto apresentado"

  nome: str = Field(...,description='Crie um nome no formato snakecase para identificar o documento'),
  legalidade: Legalidade = Field(..., description="Escolher se o caso é legal ou ilegal"),
  data_da_analise:date=Field(datetime.today(),description='Data da analise no formato: YYYY-MM-DD')
  analise: str = Field(...,description="Resuma a analise, listando os argumentos apresentados",
    )



def colorir_legalidade(val):
    if val == "legal":
        return 'color: blue'
    elif val == "ilegal":
        return 'color: red'
    return ''

def criar_prompt_com_contexto(contexto):
  system_prompt =f"""
    Vocẽ é um consultor especialista em legislações relcionados ao mercado financeiro brasileiro.

    Seu dever é ajudar outros advogados a solucionar dúvidas relacionadas a jurisprudência brasileira sobre o assunto.

    Você irá analisar:
    -contratos
    -decisões judiciais
    -casos que chegam ao consultorio
    -documentações

    Você deve responder perguntas com base no contexto apresentado.Caso você não saiba a resposta, seja honesto e diga que não sabe responder.NUNCA DIGA PARA PROCURAR UM ESPECIALISTA OU OUTRO PROFISSIONAL
      - Há algo incorreto do ponto de vista legal?
      - Como você interpreta o caso de um ponto de vista legal.
      - Como ele poderia ser resolvido.
    Contexto:{contexto}

    -
    """
  return system_prompt

def convert_streamlit_upload_to_markdown(uploaded_file):
    if uploaded_file is None:
        raise ValueError("Nenhum arquivo foi enviado.")


    filename = uploaded_file.name
    ext = filename.split(".")[-1].lower()
    if ext not in ['pdf', 'txt', 'md']:
        raise ValueError("Tipo de arquivo não suportado. Use .pdf, .txt ou .md")

    
    with tempfile.NamedTemporaryFile(delete=False, suffix='.' + ext) as tmp_file:
        tmp_file.write(uploaded_file.read())
        tmp_path = tmp_file.name

    doc = converter.parse(tmp_path)
    doc_final=''
    for i in range(len(doc.pages)):
        doc_final=''.join(doc.pages[i].md)
        

    return doc_final
    
def criar_json_groq_chromadb(pergunta,modelo_groq=MODEL_NAME,response_model=LegalStatus):
  system_prompt=criar_prompt_com_contexto(pergunta)
  json_groq= client_groq.chat.completions.create(
      model=modelo_groq,
      messages= [
          {"role":"user","content":f"{system_prompt}"}
      ],
      response_model=LegalStatus,
  )

  return json_groq.model_dump()
    




tab_texto, tab_documento = st.tabs(["Escrever Texto", "Upload de documentos"])

with tab_texto:
    contexto=st.text_area('Escreva ou cole o texto aqui.')

with tab_documento:
    uploaded_file = st.file_uploader("Envie um arquivo (.pdf, .txt ou .md)", type=["pdf", "txt", "md"])

    if uploaded_file is not None:
        try:
            contexto = convert_streamlit_upload_to_markdown(uploaded_file)
            st.code(contexto,language='markdown')
        except Exception as e:
            st.error(f"Erro: {e}")



if st.button("Enviar"):
    print(f'Esse é o contexto: {contexto}')
    if contexto.strip():
        st.success("Texto recebido com sucesso!")
        json=criar_json_groq_chromadb(contexto)
    else:
        st.warning("Você precisa digitar ou envia algo antes da analise.")
        
tab_analise,tab_grafico, tab_tabela = st.tabs(["Analise","Gráfico de analises", "Tabela de Análises"])


if json:
    st.session_state.df = pd.concat(
        [st.session_state.df, pd.DataFrame([json])],
        ignore_index=True
    )

    resposta = json['legalidade'].split('.')[-1]

    df_legalidade = st.session_state.df['legalidade'].value_counts().reset_index()
    df_legalidade.columns = ['legalidade', 'count']
    
    
    df_legalidade['legalidade'] = df_legalidade['legalidade'].apply(lambda x: str(x).split('.')[-1])

    
    print(df_legalidade)
    
    cores = {
        'Legal': 'blue',
        'Ilegal': 'red'
    }
    with tab_analise:
        st.markdown(f"""
                *Legalidade*: {resposta}
                 
                *Análise*: {json['analise']}""")
        
    with tab_grafico:
        fig = px.bar(
            df_legalidade,
            x='legalidade',
            y='count',
            color='legalidade',
            color_discrete_map=cores,
            labels={'count': 'Quantidade', 'legalidade': 'Classificação'},
            title='Distribuição de Legalidade das Análises',
        )

        # Exibe no Streamlit
        st.plotly_chart(fig, use_container_width=True)

    with tab_tabela:
        st.dataframe(
                st.session_state.df.style.map(colorir_legalidade, subset=['legalidade'])
        )   
