from PyPDF2 import PdfReader
import os,time,ast
import pandas as pd
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.text_splitter import CharacterTextSplitter 
from langchain.chains import ConversationalRetrievalChain,RetrievalQA,ConversationChain
from langchain.memory import ConversationBufferMemory
from langchain.document_loaders import PyPDFLoader
from langchain.document_loaders import TextLoader
from langchain.docstore.document import Document
from langchain.prompts import PromptTemplate
from langchain.indexes.vectorstore import VectorstoreIndexCreator
from langchain.text_splitter import CharacterTextSplitter 
from langchain.vectorstores import Chroma
from langchain.llms import OpenAI
from langchain import FAISS
from datetime import datetime, timedelta

os.environ["OPENAI_API_KEY"] = "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"

class QueryEmbeddedData():
    def __init__(self,memory_buffer=ConversationBufferMemory()):
        self.open_api_key = os.environ.get("OPENAI_API_KEY")
        self.embeddings = OpenAIEmbeddings();
        self.llm_model  = OpenAI(openai_api_key=self.open_api_key, temperature=0.0,)    
        self.memory_buffer = memory_buffer

    def run_existing_embedding_from_faiss(self,user_query,embedded_file_location):
        print(f'--{datetime.now()}--run_existing_embedding_from_faiss')
        vector_store = FAISS.load_local(embedded_file_location, self.embeddings)
        chain = ConversationalRetrievalChain.from_llm(self.llm_model, vector_store.as_retriever(),memory=self.memory_buffer)
        return self._call_chain_and_get_result(user_query,vector_store)

    def crete_new_embeedings_from_pdf(self,user_query,pdf_file_location):
        print(f'--{datetime.now()}--crete_new_embeedings_from_pdf')
        loader = PyPDFLoader(pdf_file_location)
        document = loader.load_and_split(self.get_text_splitter())
        vector_store = FAISS.from_document(document, self.embeddings)
        return self._call_chain_and_get_result(user_query,vector_store)

    def _call_chain_and_get_result(self,user_query,vector_store):
        chain = ConversationalRetrievalChain.from_llm(self.llm_model, vector_store.as_retriever(),memory=self.memory_buffer)
        result = chain({"question":user_query})
        return result['answer'];
    
    def _get_text_splitter(self):
        return CharacterTextSplitter(separator='\n',chunk_size=5000,chunk_overlap=200,length_function=len)
    