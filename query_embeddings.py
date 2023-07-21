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
from langchain.prompts import (
    ChatPromptTemplate,
    PromptTemplate,
    SystemMessagePromptTemplate,
    AIMessagePromptTemplate,
    HumanMessagePromptTemplate,
)

os.environ["OPENAI_API_KEY"] = ""

class QueryEmbeddedData():
    def __init__(self,memory_buffer=ConversationBufferMemory()):
        self.open_api_key = os.environ.get("OPENAI_API_KEY")
        self.embeddings = OpenAIEmbeddings();
        self.llm_model  = OpenAI(openai_api_key=self.open_api_key, temperature=0.0)    
        self.memory_buffer = memory_buffer

    def run_existing_embedding_from_faiss(self,user_query,embedded_file_location):
        print(f'--{datetime.now()}--run_existing_embedding_from_faiss')
        vector_store = FAISS.load_local(embedded_file_location, self.embeddings)
        chain = ConversationalRetrievalChain.from_llm(self.llm_model, vector_store.as_retriever(),memory=self.memory_buffer)
        return self._call_chain_and_get_result(user_query,vector_store)

    def crete_new_embeedings_from_pdf(self,user_query,prompt,pdf_file_location):
        print(f'--{datetime.now()}--crete_new_embeedings_from_pdf--with--prompt')
        loader = PyPDFLoader(pdf_file_location)
        document = loader.load_and_split(self._get_text_splitter())
        vector_store = FAISS.from_documents(document, self.embeddings)
        # return self._call_chain_and_get_result_include_prompt(user_query,vector_store)
        return self._call_chain_custom_prompt(user_query,prompt,vector_store)

    def _call_chain_and_get_result(self,user_query,vector_store):
        chain = ConversationalRetrievalChain.from_llm(self.llm_model, vector_store.as_retriever(),memory=self.memory_buffer)
        result = chain({"question":user_query})
        return result['answer'];

    def _call_chain_and_get_result_include_prompt(self,question,vector_store):
        general_user_template = "Question:```{question}```"
        general_system_template = f""" 
        You are an AI Bot, and your responsibility is to provide a standard operating procedure using fix logs. \
        Please provide a detailed response about the fix. \
        when providing the standard operating procedure. If some next steps include database queries required to solve the issue, \
        please mention those database queries indivisually in a bulleted list\
        For example if this is a sample question: What is the SOP for file contention\
        Then your answer should be formatted in the following way: \n\
        This job has a resource requirement on the mainframe file PAAA.VSM.PAAAW151.CARDHIST.CLUSTER.\
        If the Job fails due to contention of file PAAA.VSM.PAAAW151.CARDHIST.CLUSTER by holder CICS1513, follow below steps for the resolution:\
        \n Start your answer with a description of the SOP, and then divide the steps into different bullet points to make it \
        more readable and human friendly.
        ----
        {context}
        ----
        """
        messages = [
                    SystemMessagePromptTemplate.from_template(general_system_template),
                    HumanMessagePromptTemplate.from_template(general_user_template)
        ]
        qa_prompt = ChatPromptTemplate.from_messages( messages )


        chain = ConversationalRetrievalChain.from_llm(
            self.llm_model, 
            vector_store.as_retriever(),
            memory=self.memory_buffer,
            combine_docs_chain_kwargs={"prompt": qa_prompt})
        result = chain({"question":user_query})
        return result['answer'];

    def _call_chain_custom_prompt(self,question,prompt,vector_store):
        LLM_PROMPT = prompt + """ 
        ----
        {context}
        ----
        Question: {question}
        Answer: 
        """
        QA_PROMPT = PromptTemplate(input_variables=["context", "question"], template=LLM_PROMPT)
        chain = ConversationalRetrievalChain.from_llm(
            self.llm_model, 
            vector_store.as_retriever(),
            memory=self.memory_buffer,
            combine_docs_chain_kwargs={"prompt": QA_PROMPT})
        result = chain({"question":question})
        return result['answer'];
    
    def _get_text_splitter(self):
        return CharacterTextSplitter(separator='\n',chunk_size=2000,chunk_overlap=200,length_function=len)
    