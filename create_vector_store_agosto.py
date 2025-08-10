import os
from dotenv import load_dotenv

from langchain_community.document_loaders import PyPDFDirectoryLoader
from langchain.text_splitter import CharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma

load_dotenv()


__import__('pysqlite3')
import sys
sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')

DATA_PATH= os.environ.get("DATA_PATH_02")
CHROMA_PATH = os.environ.get('CHROMA_PATH')


embedding_model = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
model_name = "maritaca-ai/sabia-7b"

embeddings = HuggingFaceEmbeddings(model_name=embedding_model)

loader = PyPDFDirectoryLoader(DATA_PATH)

raw_documents=loader.load()

pdf_text_splitter = CharacterTextSplitter(chunk_size=1000)

chunks=pdf_text_splitter.split_documents(raw_documents)

documents=[]
metadata=[]
ids=[]

i=0

for chunk in chunks:
    documents.append(chunk.page_content)
    ids.append("ID"+str(i))
    metadata.append(chunk.metadata)

    i += 1

def chunk_data(data, chunk_size):
    for i in range(0, len(data), chunk_size):
        yield data[i:i + chunk_size]

chroma_vector_store = Chroma(
    collection_name="base_agosto",
    embedding_function=embeddings,
    persist_directory=CHROMA_PATH,
)

chunk_size = 5461

for doc_chunk, meta_chunk, id_chunk in zip(
    chunk_data(documents, chunk_size),
    chunk_data(metadata, chunk_size),
    chunk_data(ids, chunk_size)
):
    chroma_vector_store.add_documents(documents=chunks, ids=id_chunk,metadata=meta_chunk)

chroma_vector_store._persist_directory()
